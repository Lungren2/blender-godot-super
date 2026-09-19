"""Blender-specific MCP resources."""

from __future__ import annotations

from typing import Any, Protocol

from mcp.server import MCPServer


class BlenderSceneReader(Protocol):
    async def inspect_scene(self) -> dict[str, Any]:
        """Return current Blender scene state."""


def register_blender_resources(
    server: MCPServer,
    scene_reader: BlenderSceneReader,
) -> None:
    """Register Blender resources without introducing a generic host abstraction."""

    @server.resource(
        "blender://scene",
        name="blender_scene",
        description="Current structured state of the active Blender scene.",
        mime_type="application/json",
    )
    async def read_blender_scene() -> dict[str, Any]:
        return await scene_reader.inspect_scene()
