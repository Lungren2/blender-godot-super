"""Structured action and artifact logging for the unified MCP server."""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
import threading
import time
from collections.abc import Awaitable, Callable, Mapping, Sequence
from dataclasses import asdict, is_dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastmcp.server.middleware import Middleware

_REDACTED_KEYS = {
    "api_key",
    "authorization",
    "password",
    "secret",
    "token",
}
_MAX_INLINE_TEXT = 32 * 1024


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _is_sensitive_key(key: str) -> bool:
    lowered = key.lower()
    return any(marker in lowered for marker in _REDACTED_KEYS)


def _request_id(context: Any) -> str | None:
    fastmcp_context = getattr(context, "fastmcp_context", None)
    if fastmcp_context is None:
        return None
    request_context = getattr(fastmcp_context, "request_context", None)
    if request_context is None:
        return None
    value = getattr(fastmcp_context, "request_id", None)
    return str(value) if value is not None else None


class AuditSink:
    """Write JSONL action records and materialize binary/large-text artifacts."""

    def __init__(self, root: Path):
        self.root = root
        self.actions_path = root / "actions.jsonl"
        self.artifacts_path = root / "artifacts.jsonl"
        self.artifact_dir = root / "artifacts"
        self._lock = threading.Lock()
        self.root.mkdir(parents=True, exist_ok=True)
        self.artifact_dir.mkdir(parents=True, exist_ok=True)

    def emit_action(self, record: Mapping[str, Any]) -> None:
        self._append_jsonl(self.actions_path, record)

    def store_bytes(
        self,
        data: bytes,
        *,
        request_id: str | None,
        label: str,
        suffix: str,
        media_type: str | None = None,
    ) -> dict[str, Any]:
        digest = hashlib.sha256(data).hexdigest()
        safe_label = "".join(char if char.isalnum() or char in "-_" else "_" for char in label)
        request_part = request_id or "no-request-id"
        filename = f"{request_part}-{safe_label}-{digest[:12]}{suffix}"
        path = self.artifact_dir / filename
        with self._lock:
            if not path.exists():
                path.write_bytes(data)
        record = {
            "record_type": "artifact",
            "created_at": _utc_now(),
            "request_id": request_id,
            "label": label,
            "path": str(path),
            "sha256": digest,
            "bytes": len(data),
            "media_type": media_type,
        }
        self._append_jsonl(self.artifacts_path, record)
        return {
            "$artifact": str(path),
            "sha256": digest,
            "bytes": len(data),
            "media_type": media_type,
        }

    def normalize(
        self,
        value: Any,
        *,
        request_id: str | None,
        label: str,
        key: str | None = None,
    ) -> Any:
        if key is not None and _is_sensitive_key(key):
            return "<redacted>"
        if value is None or isinstance(value, (bool, int, float)):
            return value
        if isinstance(value, str):
            if len(value) <= _MAX_INLINE_TEXT:
                return value
            return self.store_bytes(
                value.encode("utf-8"),
                request_id=request_id,
                label=f"{label}-text",
                suffix=".txt",
                media_type="text/plain; charset=utf-8",
            )
        if isinstance(value, bytes):
            return self.store_bytes(
                value,
                request_id=request_id,
                label=label,
                suffix=".bin",
                media_type="application/octet-stream",
            )
        if is_dataclass(value) and not isinstance(value, type):
            return self.normalize(asdict(value), request_id=request_id, label=label)
        model_dump = getattr(value, "model_dump", None)
        if callable(model_dump):
            dumped = model_dump(mode="json", by_alias=True)
            return self.normalize(dumped, request_id=request_id, label=label)
        if isinstance(value, Mapping):
            image_artifact = self._maybe_extract_image(value, request_id=request_id, label=label)
            if image_artifact is not None:
                return image_artifact
            return {
                str(item_key): self.normalize(
                    item_value,
                    request_id=request_id,
                    label=f"{label}-{item_key}",
                    key=str(item_key),
                )
                for item_key, item_value in value.items()
            }
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            return [
                self.normalize(item, request_id=request_id, label=f"{label}-{index}")
                for index, item in enumerate(value)
            ]
        if hasattr(value, "__dict__"):
            return self.normalize(vars(value), request_id=request_id, label=label)
        return repr(value)

    def _maybe_extract_image(
        self,
        value: Mapping[Any, Any],
        *,
        request_id: str | None,
        label: str,
    ) -> dict[str, Any] | None:
        block_type = value.get("type")
        data = value.get("data")
        if block_type != "image" or not isinstance(data, str):
            return None
        media_type_raw = value.get("mimeType", value.get("mime_type", "image/png"))
        media_type = str(media_type_raw)
        try:
            decoded = base64.b64decode(data, validate=True)
        except (binascii.Error, ValueError):
            return {
                str(item_key): self.normalize(
                    item_value,
                    request_id=request_id,
                    label=f"{label}-{item_key}",
                    key=str(item_key),
                )
                for item_key, item_value in value.items()
            }
        suffix = ".png" if media_type == "image/png" else ".img"
        artifact = self.store_bytes(
            decoded,
            request_id=request_id,
            label=label,
            suffix=suffix,
            media_type=media_type,
        )
        artifact["type"] = "image"
        return artifact

    def _append_jsonl(self, path: Path, record: Mapping[str, Any]) -> None:
        line = json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        with self._lock:
            with path.open("a", encoding="utf-8") as handle:
                handle.write(line)
                handle.write("\n")


CallNext = Callable[[Any], Awaitable[Any]]


class ActionAuditMiddleware(Middleware):
    """Record tool, resource, and prompt actions with extracted binary artifacts."""

    def __init__(self, root: Path):
        self.sink = AuditSink(root)

    async def on_call_tool(self, context: Any, call_next: CallNext) -> Any:
        name = str(context.message.name)
        return await self._record(
            context,
            call_next,
            kind="tool",
            name=name,
            request_payload=getattr(context.message, "arguments", None) or {},
        )

    async def on_read_resource(self, context: Any, call_next: CallNext) -> Any:
        uri = str(context.message.uri)
        return await self._record(
            context,
            call_next,
            kind="resource",
            name=uri,
            request_payload={"uri": uri},
        )

    async def on_get_prompt(self, context: Any, call_next: CallNext) -> Any:
        name = str(context.message.name)
        return await self._record(
            context,
            call_next,
            kind="prompt",
            name=name,
            request_payload=getattr(context.message, "arguments", None) or {},
        )

    async def _record(
        self,
        context: Any,
        call_next: CallNext,
        *,
        kind: str,
        name: str,
        request_payload: Any,
    ) -> Any:
        started = time.perf_counter()
        request_id = _request_id(context)
        record: dict[str, Any] = {
            "record_type": "action",
            "kind": kind,
            "name": name,
            "request_id": request_id,
            "started_at": _utc_now(),
            "request": self.sink.normalize(
                request_payload,
                request_id=request_id,
                label=f"{kind}-{name}-request",
            ),
        }
        try:
            result = await call_next(context)
        except Exception as exc:  # noqa: BLE001 - audit and re-raise arbitrary handler errors
            record["status"] = "failed"
            record["error"] = {"type": type(exc).__name__, "message": str(exc)}
            record["duration_ms"] = round((time.perf_counter() - started) * 1000, 3)
            self.sink.emit_action(record)
            raise

        record["status"] = "error" if bool(getattr(result, "is_error", False)) else "completed"
        record["response"] = self.sink.normalize(
            result,
            request_id=request_id,
            label=f"{kind}-{name}-response",
        )
        record["duration_ms"] = round((time.perf_counter() - started) * 1000, 3)
        self.sink.emit_action(record)
        return result
