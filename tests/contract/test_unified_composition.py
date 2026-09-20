import pytest
from fastmcp import Client, FastMCP

from super_mcp.server import build_server, compose_servers


@pytest.mark.asyncio
async def test_composes_engine_native_components_without_renaming() -> None:
    blender = FastMCP("blender-test")

    @blender.tool
    async def blender_ping() -> str:
        return "blender"

    @blender.resource("blender://scene")
    async def blender_scene() -> str:
        return '{"host":"blender"}'

    godot = FastMCP("godot-test")

    @godot.tool
    async def godot_get_server_info() -> str:
        return "godot"

    @godot.resource("godot://project/info")
    async def godot_project_info() -> str:
        return '{"host":"godot"}'

    server = compose_servers(blender, godot)

    async with Client(server) as client:
        tools = {tool.name for tool in await client.list_tools()}
        resources = {str(resource.uri) for resource in await client.list_resources()}
        blender_state = await client.read_resource("blender://scene")
        godot_state = await client.read_resource("godot://project/info")

    assert {"blender_ping", "godot_get_server_info"} <= tools
    assert {"blender://scene", "godot://project/info"} <= resources
    assert blender_state[0].text == '{"host":"blender"}'
    assert godot_state[0].text == '{"host":"godot"}'


@pytest.mark.asyncio
async def test_production_server_lists_pinned_upstream_components() -> None:
    server = build_server()

    async with Client(server) as client:
        tools = {tool.name for tool in await client.list_tools()}
        resources = {str(resource.uri) for resource in await client.list_resources()}

    assert "blender_ping" in tools
    assert "godot_get_server_info" in tools
    assert "blender://scene" in resources
    assert "godot://project/info" in resources
