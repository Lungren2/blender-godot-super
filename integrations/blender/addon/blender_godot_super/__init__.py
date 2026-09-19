"""Blender add-on entry point for blender-godot-super."""

from __future__ import annotations

from .bridge import start_bridge, stop_bridge

bl_info = {
    "name": "Blender Godot Super MCP Bridge",
    "author": "Lungren2",
    "version": (0, 1, 0),
    "blender": (4, 3, 0),
    "location": "Preferences > Add-ons",
    "description": "Host bridge for the blender-godot-super MCP server",
    "category": "Development",
}


def register() -> None:
    start_bridge()


def unregister() -> None:
    stop_bridge()
