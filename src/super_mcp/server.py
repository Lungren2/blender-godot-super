"""Unified MCP composition root."""

from __future__ import annotations

import importlib
import os
import sys
from collections.abc import Callable
from typing import cast

from fastmcp import FastMCP
from fastmcp.client.transports import StdioTransport
from fastmcp.server import create_proxy
from mcp.server import MCPServer

from super_mcp.hosts.blender import BlenderBridgeClient
from super_mcp.resources.blender import BlenderSceneReader, register_blender_resources


def build_blender_observation_server(
    scene_reader: BlenderSceneReader | None = None,
) -> MCPServer:
    """Build the repository's narrow Blender observation server.

    This remains available for the existing real-host contract and integration tests.
    Production uses :func:`build_server`, which composes the upstream Blender and
    Godot MCP implementations behind one endpoint.
    """

    server = MCPServer(
        "blender-godot-super-observation",
        instructions="Read the current Blender scene through blender://scene.",
    )
    resolved_reader = scene_reader if scene_reader is not None else BlenderBridgeClient()
    register_blender_resources(server, resolved_reader)
    return server


def build_blender_proxy() -> FastMCP:
    """Proxy the pinned claude-blender MCP package over stdio."""

    transport = StdioTransport(
        command=sys.executable,
        args=["-m", "claude_blender_mcp.server"],
        env=dict(os.environ),
        keep_alive=True,
    )
    return create_proxy(transport, name="Blender upstream")


def build_godot_server() -> FastMCP:
    """Build the pinned hybridindie Godot MCP in-process.

    In-process composition preserves its server-global toolset gating and bridge
    lifecycle across MCP requests. Dynamic loading keeps this repository's strict
    typing boundary independent of the upstream package's missing PEP 561 marker.
    """

    config_module = importlib.import_module("mcp_server.config")
    server_module = importlib.import_module("mcp_server.server")

    server_config_type = vars(config_module)["ServerConfig"]
    create_server = cast(Callable[..., FastMCP], vars(server_module)["create_server"])
    return create_server(config=server_config_type.from_env())


def compose_servers(blender: FastMCP, godot: FastMCP) -> FastMCP:
    """Expose Blender and Godot components through one MCP server."""

    server = FastMCP(
        "blender-godot-super",
        instructions=(
            "One MCP endpoint for Blender and Godot. Keep engine-native names and "
            "resources: blender_* / blender:// for Blender and godot_* / godot:// "
            "for Godot. For Blender, inspect first with blender://scene or "
            "blender_get_scene, use blender_checkpoint before risky edits, and verify "
            "with blender_screenshot or blender_render. For Godot, call "
            "godot_get_server_info and godot_list_toolsets first, enable required "
            "toolsets before calling hidden tools, and prefer godot:// resources for "
            "read-only state."
        ),
    )
    server.mount(blender)
    server.mount(godot)
    return server


def build_server() -> FastMCP:
    """Build the production unified MCP server from pinned upstream implementations."""

    return compose_servers(build_blender_proxy(), build_godot_server())


mcp = build_server()


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
