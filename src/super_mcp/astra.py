"""GPT-6 Astra MCP profile helpers for the OpenAI Responses API."""

from __future__ import annotations

import argparse
import json
from typing import Any

ASTRA_GODOT_TOOLSETS = "scene_edit,editor,runtime,testing"

ASTRA_ALLOWED_TOOLS: tuple[str, ...] = (
    "blender_ping",
    "blender_version",
    "blender_get_scene",
    "blender_get_object",
    "blender_checkpoint",
    "blender_add_object",
    "blender_modify_object",
    "blender_create_material",
    "blender_modifier",
    "blender_duplicate",
    "blender_organize",
    "blender_frame_camera",
    "blender_set_keyframe",
    "blender_set_frame_range",
    "blender_screenshot",
    "blender_render",
    "blender_save",
    "blender_undo",
    "godot_health_check",
    "godot_get_server_info",
    "godot_list_toolsets",
    "godot_enable_toolset",
    "godot_disable_toolset",
    "godot_list_tools_by_safety_class",
    "godot_inspection_get_project_info",
    "godot_inspection_get_active_scene",
    "godot_inspection_get_scene_tree",
    "godot_inspection_get_selected_node",
    "godot_inspection_get_node_properties",
    "godot_inspection_get_node_property",
    "godot_inspection_get_node_groups",
    "godot_scene_edit_open_scene",
    "godot_scene_edit_create_node",
    "godot_scene_edit_rename_node",
    "godot_scene_edit_set_node_property",
    "godot_scene_edit_attach_script",
    "godot_scene_edit_connect_signal",
    "godot_scene_edit_add_to_group",
    "godot_scene_edit_save_scene",
    "godot_scene_edit_save_all_scenes",
    "godot_scene_edit_list_open_scenes",
    "godot_scene_edit_select_nodes",
    "godot_editor_capture_screenshot",
    "godot_runtime_run_and_capture",
    "godot_runtime_is_playing",
    "godot_testing_run_tests",
)

ASTRA_AUTO_APPROVED_TOOLS = ASTRA_ALLOWED_TOOLS


def build_mcp_tool(
    *,
    tunnel_id: str | None = None,
    server_url: str | None = None,
) -> dict[str, Any]:
    """Build the Responses API MCP tool definition for the bounded Astra profile."""

    if (tunnel_id is None) == (server_url is None):
        raise ValueError("Provide exactly one of tunnel_id or server_url")
    tool: dict[str, Any] = {
        "type": "mcp",
        "server_label": "blender_godot_super",
        "server_description": (
            "Unified live Blender and Godot development server. Inspect before mutation, "
            "checkpoint reversible Blender work, save editor state explicitly, and verify "
            "changes with renders, screenshots, runtime output, and persisted-state reads."
        ),
        "allowed_tools": list(ASTRA_ALLOWED_TOOLS),
        "require_approval": {"never": {"tool_names": list(ASTRA_AUTO_APPROVED_TOOLS)}},
    }
    if tunnel_id is not None:
        tool["tunnel_id"] = tunnel_id
    if server_url is not None:
        tool["server_url"] = server_url
    return tool


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Print the GPT-6 Astra Responses API MCP tool definition."
    )
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--tunnel-id")
    target.add_argument("--server-url")
    parser.add_argument("--compact", action="store_true")
    return parser


def main() -> None:
    args = _parser().parse_args()
    payload = build_mcp_tool(tunnel_id=args.tunnel_id, server_url=args.server_url)
    if args.compact:
        print(json.dumps(payload, separators=(",", ":")))
    else:
        print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
