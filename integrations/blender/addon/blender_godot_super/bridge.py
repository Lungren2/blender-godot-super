"""Loopback bridge from the MCP process into Blender.

Socket handling runs in worker threads. Blender API access never does: requests are
placed on a queue and executed by a bpy application timer on Blender's main thread.
"""

from __future__ import annotations

import json
import queue
import socketserver
import threading
from dataclasses import dataclass, field
from typing import Any, Final

import bpy

BRIDGE_HOST: Final = "127.0.0.1"
BRIDGE_PORT: Final = 8765
REQUEST_TIMEOUT_SECONDS: Final = 5.0
TIMER_INTERVAL_SECONDS: Final = 0.05
MAX_REQUEST_BYTES: Final = 65_536


@dataclass(slots=True)
class PendingRequest:
    request_id: str
    method: str
    completed: threading.Event = field(default_factory=threading.Event)
    result: dict[str, Any] | None = None
    error: dict[str, str] | None = None


class _BridgeServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


class _BridgeRequestHandler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        raw = self.rfile.readline(MAX_REQUEST_BYTES + 1)
        if len(raw) > MAX_REQUEST_BYTES:
            self._write_error("", "request_too_large", "Request exceeded 64 KiB.")
            return

        try:
            message = json.loads(raw)
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._write_error("", "invalid_json", "Request was not valid JSON.")
            return

        if not isinstance(message, dict):
            self._write_error("", "invalid_request", "Request must be a JSON object.")
            return

        request_id = message.get("id")
        method = message.get("method")
        if not isinstance(request_id, str) or not isinstance(method, str):
            self._write_error("", "invalid_request", "Request requires string id and method.")
            return

        pending = PendingRequest(request_id=request_id, method=method)
        _requests.put(pending)

        if not pending.completed.wait(REQUEST_TIMEOUT_SECONDS):
            self._write_error(
                request_id,
                "main_thread_timeout",
                "Blender did not process the request before the bridge timeout.",
            )
            return

        if pending.error is not None:
            response: dict[str, Any] = {
                "id": request_id,
                "ok": False,
                "error": pending.error,
            }
        else:
            response = {
                "id": request_id,
                "ok": True,
                "result": pending.result or {},
            }

        self._write_response(response)

    def _write_error(self, request_id: str, code: str, message: str) -> None:
        self._write_response(
            {
                "id": request_id,
                "ok": False,
                "error": {"code": code, "message": message},
            }
        )

    def _write_response(self, response: dict[str, Any]) -> None:
        payload = (json.dumps(response, separators=(",", ":")) + "\n").encode("utf-8")
        self.wfile.write(payload)


_requests: queue.Queue[PendingRequest] = queue.Queue()
_server: _BridgeServer | None = None
_server_thread: threading.Thread | None = None


def _inspect_scene() -> dict[str, Any]:
    """Inspect Blender state. This function must run on Blender's main thread."""

    scene = bpy.context.scene
    active = bpy.context.view_layer.objects.active
    camera = scene.camera

    return {
        "host": {
            "kind": "blender",
            "version": bpy.app.version_string,
        },
        "document": {
            "filepath": bpy.data.filepath or None,
            "saved": bool(bpy.data.filepath),
        },
        "scene": {
            "name": scene.name,
            "active_object": active.name if active is not None else None,
            "camera": camera.name if camera is not None else None,
            "objects": [
                {
                    "name": obj.name,
                    "type": obj.type,
                }
                for obj in scene.objects
            ],
        },
    }


def _drain_requests() -> float:
    """Execute queued work from Blender's main-thread application timer."""

    for _ in range(32):
        try:
            pending = _requests.get_nowait()
        except queue.Empty:
            break

        try:
            if pending.method == "scene.inspect":
                pending.result = _inspect_scene()
            else:
                pending.error = {
                    "code": "method_not_found",
                    "message": f"Unsupported bridge method: {pending.method}",
                }
        except Exception as exc:  # Blender errors need to cross the process boundary.
            pending.error = {
                "code": "host_error",
                "message": f"{type(exc).__name__}: {exc}",
            }
        finally:
            pending.completed.set()

    return TIMER_INTERVAL_SECONDS


def start_bridge() -> None:
    """Start the loopback bridge and main-thread dispatcher."""

    global _server, _server_thread

    if _server is not None:
        return

    _server = _BridgeServer((BRIDGE_HOST, BRIDGE_PORT), _BridgeRequestHandler)
    _server_thread = threading.Thread(
        target=_server.serve_forever,
        name="blender-godot-super-bridge",
        daemon=True,
    )
    _server_thread.start()

    if not bpy.app.timers.is_registered(_drain_requests):
        bpy.app.timers.register(_drain_requests, first_interval=TIMER_INTERVAL_SECONDS)


def stop_bridge() -> None:
    """Stop bridge I/O and unregister the Blender main-thread dispatcher."""

    global _server, _server_thread

    if bpy.app.timers.is_registered(_drain_requests):
        bpy.app.timers.unregister(_drain_requests)

    server = _server
    thread = _server_thread
    _server = None
    _server_thread = None

    if server is not None:
        server.shutdown()
        server.server_close()
    if thread is not None:
        thread.join(timeout=1.0)

    while True:
        try:
            pending = _requests.get_nowait()
        except queue.Empty:
            break
        pending.error = {
            "code": "bridge_stopped",
            "message": "Blender bridge stopped before the request completed.",
        }
        pending.completed.set()
