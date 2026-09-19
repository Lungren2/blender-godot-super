"""Server-side client for the Blender add-on bridge."""

from __future__ import annotations

import asyncio
import json
import os
import socket
import uuid
from typing import Any, Final

DEFAULT_BLENDER_BRIDGE_HOST: Final = "127.0.0.1"
DEFAULT_BLENDER_BRIDGE_PORT: Final = 8765
DEFAULT_BLENDER_BRIDGE_TIMEOUT_SECONDS: Final = 2.0
MAX_RESPONSE_BYTES: Final = 1_048_576


class BlenderBridgeError(RuntimeError):
    """Base class for Blender bridge failures."""


class BlenderBridgeUnavailable(BlenderBridgeError):
    """The local Blender bridge could not be reached."""


class BlenderBridgeProtocolError(BlenderBridgeError):
    """The local Blender bridge returned an invalid response."""


class BlenderBridgeRemoteError(BlenderBridgeError):
    """Blender accepted the request but failed while handling it."""


class BlenderBridgeClient:
    """Small loopback client for observation requests sent to Blender."""

    def __init__(
        self,
        *,
        host: str | None = None,
        port: int | None = None,
        timeout_seconds: float = DEFAULT_BLENDER_BRIDGE_TIMEOUT_SECONDS,
    ) -> None:
        resolved_host = host or os.environ.get(
            "SUPER_BLENDER_BRIDGE_HOST", DEFAULT_BLENDER_BRIDGE_HOST
        )
        if resolved_host not in {"127.0.0.1", "localhost", "::1"}:
            raise ValueError("The initial Blender bridge is loopback-only.")

        self.host = resolved_host
        self.port = port or int(
            os.environ.get("SUPER_BLENDER_BRIDGE_PORT", DEFAULT_BLENDER_BRIDGE_PORT)
        )
        self.timeout_seconds = timeout_seconds

    async def inspect_scene(self) -> dict[str, Any]:
        """Read the active Blender scene through the real add-on bridge."""

        return await asyncio.to_thread(self._request, "scene.inspect")

    def _request(self, method: str) -> dict[str, Any]:
        request_id = uuid.uuid4().hex
        request = {"id": request_id, "method": method}
        payload = (json.dumps(request, separators=(",", ":")) + "\n").encode("utf-8")

        try:
            with socket.create_connection(
                (self.host, self.port), timeout=self.timeout_seconds
            ) as connection:
                connection.settimeout(self.timeout_seconds)
                connection.sendall(payload)
                response_bytes = self._read_line(connection)
        except (OSError, TimeoutError) as exc:
            raise BlenderBridgeUnavailable(
                f"Blender bridge is unavailable at {self.host}:{self.port}."
            ) from exc

        return self._decode_response(response_bytes, expected_id=request_id)

    @staticmethod
    def _read_line(connection: socket.socket) -> bytes:
        chunks = bytearray()
        while len(chunks) <= MAX_RESPONSE_BYTES:
            block = connection.recv(min(65_536, MAX_RESPONSE_BYTES + 1 - len(chunks)))
            if not block:
                break
            chunks.extend(block)
            newline = chunks.find(b"\n")
            if newline >= 0:
                return bytes(chunks[:newline])

        if len(chunks) > MAX_RESPONSE_BYTES:
            raise BlenderBridgeProtocolError("Blender bridge response exceeded 1 MiB.")
        raise BlenderBridgeProtocolError("Blender bridge closed without a complete response.")

    @staticmethod
    def _decode_response(payload: bytes, *, expected_id: str) -> dict[str, Any]:
        try:
            message = json.loads(payload)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise BlenderBridgeProtocolError("Blender bridge returned invalid JSON.") from exc

        if not isinstance(message, dict):
            raise BlenderBridgeProtocolError("Blender bridge response must be an object.")
        if message.get("id") != expected_id:
            raise BlenderBridgeProtocolError("Blender bridge response id did not match the request.")

        if message.get("ok") is True:
            result = message.get("result")
            if not isinstance(result, dict):
                raise BlenderBridgeProtocolError(
                    "Successful Blender bridge responses must contain an object result."
                )
            return result

        error = message.get("error")
        if isinstance(error, dict):
            code = str(error.get("code", "host_error"))
            detail = str(error.get("message", "Blender bridge request failed."))
            raise BlenderBridgeRemoteError(f"{code}: {detail}")

        raise BlenderBridgeProtocolError("Blender bridge returned an invalid failure response.")
