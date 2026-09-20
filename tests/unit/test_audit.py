from __future__ import annotations

import base64
import json
from pathlib import Path

from super_mcp.audit import AuditSink


def test_audit_sink_extracts_image_and_redacts_secrets(tmp_path: Path) -> None:
    sink = AuditSink(tmp_path)
    png = b"\x89PNG\r\n\x1a\nfixture"
    normalized = sink.normalize(
        {
            "type": "image",
            "data": base64.b64encode(png).decode("ascii"),
            "mimeType": "image/png",
        },
        request_id="request-1",
        label="render",
    )

    artifact_path = Path(normalized["$artifact"])
    assert artifact_path.read_bytes() == png
    assert normalized["media_type"] == "image/png"

    secrets = sink.normalize(
        {"api_key": "secret-value", "nested": {"authorization": "Bearer secret"}},
        request_id="request-2",
        label="request",
    )
    assert secrets == {"api_key": "<redacted>", "nested": {"authorization": "<redacted>"}}

    manifest = [json.loads(line) for line in sink.artifacts_path.read_text().splitlines()]
    assert manifest[0]["sha256"] == normalized["sha256"]
    assert manifest[0]["bytes"] == len(png)


def test_audit_sink_externalizes_large_text(tmp_path: Path) -> None:
    sink = AuditSink(tmp_path)
    normalized = sink.normalize(
        "x" * (33 * 1024),
        request_id="request-3",
        label="large-output",
    )

    artifact_path = Path(normalized["$artifact"])
    assert artifact_path.read_text() == "x" * (33 * 1024)
