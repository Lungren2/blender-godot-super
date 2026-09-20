from __future__ import annotations

import pytest

from super_mcp.astra import (
    ASTRA_ALLOWED_TOOLS,
    ASTRA_DEVELOPER_INSTRUCTIONS,
    build_mcp_tool,
    build_responses_profile,
)


def test_astra_profile_uses_tunnel_and_excludes_escape_hatches() -> None:
    tool = build_mcp_tool(tunnel_id="tunnel_test")

    assert tool["tunnel_id"] == "tunnel_test"
    assert "server_url" not in tool
    assert tool["allowed_tools"] == list(ASTRA_ALLOWED_TOOLS)
    assert "blender_execute" not in tool["allowed_tools"]
    assert "godot_scene_edit_delete_node" not in tool["allowed_tools"]
    assert "godot_scene_edit_reload_scene" not in tool["allowed_tools"]
    assert set(tool["require_approval"]["never"]["tool_names"]) == set(ASTRA_ALLOWED_TOOLS)


def test_astra_profile_uses_server_url() -> None:
    tool = build_mcp_tool(server_url="https://example.test/mcp")

    assert tool["server_url"] == "https://example.test/mcp"
    assert "tunnel_id" not in tool


def test_astra_profile_requires_exactly_one_target() -> None:
    with pytest.raises(ValueError, match="exactly one"):
        build_mcp_tool()
    with pytest.raises(ValueError, match="exactly one"):
        build_mcp_tool(tunnel_id="t", server_url="https://example.test/mcp")


def test_responses_profile_adds_computer_feedback_loop() -> None:
    profile = build_responses_profile(tunnel_id="tunnel_test")

    assert profile["model"] == "gpt-6-astra"
    assert profile["tools"][0]["type"] == "mcp"
    assert profile["tools"][1] == {"type": "computer"}
    assert "inspect another screenshot" in profile["instructions"]
    assert "check_repo_hygiene.py --include-untracked" in profile["instructions"]
    assert profile["instructions"] == ASTRA_DEVELOPER_INSTRUCTIONS
