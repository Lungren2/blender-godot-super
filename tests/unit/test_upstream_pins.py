import tomllib
from pathlib import Path

from super_mcp.installations import BLENDER, GODOT

ROOT = Path(__file__).resolve().parents[2]


def test_editor_installer_revisions_match_runtime_dependencies() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())
    dependencies = project["project"]["dependencies"]

    by_name = {dependency.split(" @ ", 1)[0]: dependency for dependency in dependencies}

    blender_dependency = by_name["claude-blender"]
    assert BLENDER.repository in blender_dependency
    assert BLENDER.revision in blender_dependency

    godot_dependency = by_name["godot-editor-mcp"]
    assert GODOT.repository in godot_dependency
    assert GODOT.revision in godot_dependency


def test_third_party_license_files_are_present() -> None:
    assert (ROOT / "licenses" / "minihellboy-claude-blender-MIT.txt").is_file()
    assert (ROOT / "licenses" / "hybridindie-godot-mcp-MIT.txt").is_file()
