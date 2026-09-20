from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

from super_mcp.astra import ASTRA_ALLOWED_TOOLS
from super_mcp.bootstrap import (
    GODOT_PLUGIN_URI,
    blender_addons_candidates,
    discover_godot_project,
    ensure_gitignore,
    ensure_godot_plugin_enabled,
    render_codex_config_section,
    write_codex_config,
)


def test_codex_config_uses_uvx_profile_and_bounded_tools() -> None:
    section = render_codex_config_section(
        "git+https://github.com/example/tool.git@deadbeef"
    )

    parsed = tomllib.loads(section)
    server = parsed["mcp_servers"]["blender-godot-super"]
    assert server["command"] == "uvx"
    assert server["args"] == [
        "--from",
        "git+https://github.com/example/tool.git@deadbeef",
        "blender-godot-super",
        "--profile",
        "astra",
    ]
    assert server["cwd"] == ".."
    assert server["required"] is True
    assert server["startup_timeout_sec"] == 60
    assert server["tool_timeout_sec"] == 180
    assert server["enabled_tools"] == list(ASTRA_ALLOWED_TOOLS)
    assert "blender_execute" not in server["enabled_tools"]


def test_codex_config_preserves_existing_project_settings(tmp_path: Path) -> None:
    config = tmp_path / ".codex" / "config.toml"
    config.parent.mkdir()
    config.write_text('model_reasoning_effort = "high"\n', encoding="utf-8")

    write_codex_config(tmp_path, "blender-godot-super==1.2.3")

    text = config.read_text(encoding="utf-8")
    assert 'model_reasoning_effort = "high"' in text
    assert "[mcp_servers.blender-godot-super]" in text
    assert "blender-godot-super==1.2.3" in text

    write_codex_config(tmp_path, "blender-godot-super==1.2.3")
    assert config.read_text(encoding="utf-8") == text


def test_codex_config_refuses_manual_section_without_force(tmp_path: Path) -> None:
    config = tmp_path / ".codex" / "config.toml"
    config.parent.mkdir()
    config.write_text(
        '[mcp_servers.blender-godot-super]\ncommand = "custom"\n',
        encoding="utf-8",
    )

    with pytest.raises(FileExistsError):
        write_codex_config(tmp_path, "blender-godot-super==1.2.3")

    write_codex_config(
        tmp_path,
        "blender-godot-super==1.2.3",
        force=True,
    )
    parsed = tomllib.loads(config.read_text(encoding="utf-8"))
    assert parsed["mcp_servers"]["blender-godot-super"]["command"] == "uvx"


def test_gitignore_is_idempotent(tmp_path: Path) -> None:
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text(".godot/\n", encoding="utf-8")

    ensure_gitignore(tmp_path)
    ensure_gitignore(tmp_path)

    assert gitignore.read_text(encoding="utf-8") == ".godot/\n.super-mcp/\n"


def test_godot_plugin_enable_adds_and_extends_editor_plugins(tmp_path: Path) -> None:
    fresh = tmp_path / "fresh.godot"
    fresh.write_text("config_version=5\n", encoding="utf-8")
    assert ensure_godot_plugin_enabled(fresh) is True
    assert GODOT_PLUGIN_URI in fresh.read_text(encoding="utf-8")
    assert ensure_godot_plugin_enabled(fresh) is False

    existing = tmp_path / "existing.godot"
    existing.write_text(
        'config_version=5\n\n[editor_plugins]\n\n'
        'enabled=PackedStringArray("res://addons/other/plugin.cfg")\n',
        encoding="utf-8",
    )
    assert ensure_godot_plugin_enabled(existing) is True
    text = existing.read_text(encoding="utf-8")
    assert "res://addons/other/plugin.cfg" in text
    assert GODOT_PLUGIN_URI in text


def test_godot_project_discovery_requires_one_project(tmp_path: Path) -> None:
    assert discover_godot_project(tmp_path) is None

    project = tmp_path / "game"
    project.mkdir()
    (project / "project.godot").write_text("config_version=5\n", encoding="utf-8")
    assert discover_godot_project(tmp_path) == project

    second = tmp_path / "prototype"
    second.mkdir()
    (second / "project.godot").write_text("config_version=5\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="Multiple Godot projects"):
        discover_godot_project(tmp_path)


def test_blender_addons_detection_prefers_env_then_latest_version(tmp_path: Path) -> None:
    explicit = tmp_path / "scripts"
    assert blender_addons_candidates(
        home=tmp_path,
        platform="linux",
        environ={"BLENDER_USER_SCRIPTS": str(explicit)},
    ) == [explicit / "addons"]

    base = tmp_path / ".config" / "blender"
    (base / "4.5").mkdir(parents=True)
    (base / "4.3").mkdir()
    assert blender_addons_candidates(
        home=tmp_path,
        platform="linux",
        environ={},
    ) == [
        base / "4.5" / "scripts" / "addons",
        base / "4.3" / "scripts" / "addons",
    ]


def test_pyproject_exposes_install_and_runtime_commands() -> None:
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    scripts = pyproject["project"]["scripts"]

    assert scripts["blender-godot-super"] == "super_mcp.launch:main"
    assert scripts["blender-godot-super-init"] == "super_mcp.bootstrap:main"
    assert scripts["blender-godot-super-astra"] == "super_mcp.astra:main"
    assert scripts["blender-godot-super-tunnel"] == "super_mcp.tunnel:main"
