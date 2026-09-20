from __future__ import annotations

from pathlib import Path

from super_mcp.methodology import SKILL_NAMES, install_game_methodology


def test_methodology_installs_skills_agents_and_design_record(tmp_path: Path) -> None:
    agents = tmp_path / "AGENTS.md"
    agents.write_text("# Existing project guidance\n\nKeep this.\n", encoding="utf-8")

    first = install_game_methodology(tmp_path)
    second = install_game_methodology(tmp_path)

    assert any("Appended game-development AGENTS guidance" in message for message in first)
    assert any("Created project-owned game design record" in message for message in first)
    assert any("Found current Codex skill" in message for message in second)

    agents_text = agents.read_text(encoding="utf-8")
    assert agents_text.startswith("# Existing project guidance\n\nKeep this.")
    assert agents_text.count("blender-godot-super:game-development:start") == 1
    assert "$game-dev-iteration" in agents_text

    design = (tmp_path / "GAME_DESIGN.md").read_text(encoding="utf-8")
    assert "## Core fantasy" in design
    assert "## Current hypotheses" in design
    assert "## Rejected experiments and lessons" in design

    for skill_name in SKILL_NAMES:
        skill = tmp_path / ".agents" / "skills" / skill_name / "SKILL.md"
        text = skill.read_text(encoding="utf-8")
        assert f"name: {skill_name}" in text
        assert "description:" in text

    assert (
        "https://www.youtube.com/playlist?list=PLPV2KyIb3jR5kPzHBi90byfhPfPqaDW9s"
        in (
            tmp_path
            / ".agents"
            / "skills"
            / "game-design-foundations"
            / "SKILL.md"
        ).read_text(encoding="utf-8")
    )


def test_methodology_preserves_custom_skill_without_force(tmp_path: Path) -> None:
    install_game_methodology(tmp_path)
    skill = tmp_path / ".agents" / "skills" / "game-combat" / "SKILL.md"
    skill.write_text("custom combat method\n", encoding="utf-8")

    messages = install_game_methodology(tmp_path)
    assert skill.read_text(encoding="utf-8") == "custom combat method\n"
    assert any("Preserved customized Codex skill game-combat" in message for message in messages)

    install_game_methodology(tmp_path, force=True)
    refreshed = skill.read_text(encoding="utf-8")
    assert refreshed.startswith("---\nname: game-combat\n")
    assert "custom combat method" not in refreshed


def test_force_never_overwrites_project_game_design(tmp_path: Path) -> None:
    install_game_methodology(tmp_path)
    design = tmp_path / "GAME_DESIGN.md"
    design.write_text("# My actual game\n\nDo not replace this.\n", encoding="utf-8")

    install_game_methodology(tmp_path, force=True)

    assert design.read_text(encoding="utf-8") == (
        "# My actual game\n\nDo not replace this.\n"
    )


def test_force_refreshes_only_managed_agents_block(tmp_path: Path) -> None:
    agents = tmp_path / "AGENTS.md"
    agents.write_text("# Local rules\n", encoding="utf-8")
    install_game_methodology(tmp_path)

    text = agents.read_text(encoding="utf-8")
    text = text.replace(
        "For player-facing game work, read `GAME_DESIGN.md` before implementation.",
        "customized managed block",
    )
    agents.write_text(text + "\n# Local footer\n", encoding="utf-8")

    messages = install_game_methodology(tmp_path, force=True)
    refreshed = agents.read_text(encoding="utf-8")

    assert "# Local rules" in refreshed
    assert "# Local footer" in refreshed
    assert "customized managed block" not in refreshed
    assert "For player-facing game work" in refreshed
    assert any("Refreshed game-development AGENTS guidance" in message for message in messages)
