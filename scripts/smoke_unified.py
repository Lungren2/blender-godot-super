"""Verify that the unified MCP advertises both upstream engine surfaces."""

from __future__ import annotations

import asyncio

from fastmcp import Client

from super_mcp.server import build_server


async def run() -> None:
    async with Client(build_server()) as client:
        tools = {tool.name for tool in await client.list_tools()}
        resources = {str(resource.uri) for resource in await client.list_resources()}

    required_tools = {"blender_ping", "godot_get_server_info"}
    required_resources = {"blender://scene", "godot://project/info"}

    missing_tools = required_tools - tools
    missing_resources = required_resources - resources
    if missing_tools or missing_resources:
        raise RuntimeError(
            f"Unified MCP is missing tools={sorted(missing_tools)} "
            f"resources={sorted(missing_resources)}"
        )

    print(f"Unified MCP ready: {len(tools)} tools, {len(resources)} static resources")


if __name__ == "__main__":
    asyncio.run(run())
