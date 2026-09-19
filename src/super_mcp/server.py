"""MCP composition root."""

from __future__ import annotations

from mcp.server import MCPServer

from super_mcp.hosts.blender import BlenderBridgeClient
from super_mcp.resources.blender import BlenderSceneReader, register_blender_resources


def build_server(scene_reader: BlenderSceneReader | None = None) -> MCPServer:
    """Build the current MCP server.

    The dependency is injectable so protocol tests can exercise MCP behavior without
    pretending a fake host proves the production host contract.
    """

    server = MCPServer(
        "blender-godot-super",
        instructions=(
            "Read engine state through MCP resources. The first supported live host "
            "surface is the Blender scene resource."
        ),
    )
    register_blender_resources(server, scene_reader or BlenderBridgeClient())
    return server


mcp = build_server()


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
