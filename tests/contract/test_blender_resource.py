import json
from typing import Any

import pytest
from mcp import Client

from super_mcp.server import build_blender_observation_server


class StubSceneReader:
    async def inspect_scene(self) -> dict[str, Any]:
        return {
            "host": {"kind": "blender", "version": "test"},
            "document": {"filepath": None, "saved": False},
            "scene": {
                "name": "Scene",
                "active_object": "Cube",
                "camera": "Camera",
                "objects": [
                    {"name": "Camera", "type": "CAMERA"},
                    {"name": "Cube", "type": "MESH"},
                ],
            },
        }


@pytest.mark.asyncio
async def test_server_advertises_2026_protocol_and_blender_scene_resource() -> None:
    server = build_blender_observation_server(StubSceneReader())

    async with Client(server, raise_exceptions=True) as client:
        assert client.protocol_version == "2026-07-28"

        resources = await client.list_resources()
        scene_resources = [
            resource
            for resource in resources.resources
            if str(resource.uri) == "blender://scene"
        ]
        assert len(scene_resources) == 1
        assert scene_resources[0].mime_type == "application/json"


@pytest.mark.asyncio
async def test_reads_blender_scene_as_json_resource() -> None:
    server = build_blender_observation_server(StubSceneReader())

    async with Client(server, raise_exceptions=True) as client:
        result = await client.read_resource("blender://scene")

    assert len(result.contents) == 1
    text = getattr(result.contents[0], "text", None)
    assert isinstance(text, str)

    payload = json.loads(text)
    assert payload["host"]["kind"] == "blender"
    assert payload["scene"]["name"] == "Scene"
    assert payload["scene"]["objects"][1] == {"name": "Cube", "type": "MESH"}
