import json

import pytest

from super_mcp.hosts.blender import (
    BlenderBridgeClient,
    BlenderBridgeProtocolError,
    BlenderBridgeRemoteError,
)


def test_rejects_non_loopback_host() -> None:
    with pytest.raises(ValueError, match="loopback-only"):
        BlenderBridgeClient(host="192.0.2.10")


def test_decodes_successful_response() -> None:
    payload = json.dumps(
        {
            "id": "request-1",
            "ok": True,
            "result": {"scene": {"name": "Scene"}},
        }
    ).encode()

    result = BlenderBridgeClient._decode_response(payload, expected_id="request-1")

    assert result == {"scene": {"name": "Scene"}}


def test_rejects_mismatched_response_id() -> None:
    payload = json.dumps({"id": "other", "ok": True, "result": {}}).encode()

    with pytest.raises(BlenderBridgeProtocolError, match="did not match"):
        BlenderBridgeClient._decode_response(payload, expected_id="request-1")


def test_preserves_remote_error_category() -> None:
    payload = json.dumps(
        {
            "id": "request-1",
            "ok": False,
            "error": {"code": "host_error", "message": "boom"},
        }
    ).encode()

    with pytest.raises(BlenderBridgeRemoteError, match="host_error: boom"):
        BlenderBridgeClient._decode_response(payload, expected_id="request-1")
