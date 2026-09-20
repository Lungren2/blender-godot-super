"""Install project-owned game-development methodology for Codex."""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path, PurePosixPath

SKILL_NAMES = (
    "game-dev-iteration",
    "godot-game-development",
    "blender-game-assets",
    "game-design-foundations",
    "game-difficulty",
    "game-pacing",
    "game-storytelling",
    "game-combat",
    "game-visuals",
)

_AGENTS_START = "<!-- blender-godot-super:game-development:start -->"
_AGENTS_END = "<!-- blender-godot-super:game-development:end -->"


def _template(relative: str) -> str:
    parts = PurePosixPath(relative).parts
    return files("super_mcp").joinpath("game_repo_template", *parts).read_text(
        encoding="utf-8"
    )


def _write_managed_file(
    destination: Path,
    content: str,
    *,
    force: bool,
    label: str,
) -> str:
    normalized = content.rstrip() + "\n"
    if not destination.exists():
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(normalized, encoding="utf-8")
        return f"Installed {label}: {destination}"

    current = destination.read_text(encoding="utf-8")
    if current == normalized:
        return f"Found current {label}: {destination}"

    if not force:
        return (
            f"Preserved customized {label}: {destination} "
            "(use --force to refresh managed methodology files)"
        )

    destination.write_text(normalized, encoding="utf-8")
    return f"Refreshed {label}: {destination}"


def _install_agents_append(project_root: Path, *, force: bool) -> str:
    destination = project_root / "AGENTS.md"
    managed = _template("AGENTS.append.md").strip()

    if _AGENTS_START not in managed or _AGENTS_END not in managed:
        raise RuntimeError("Bundled AGENTS append is missing managed markers")

    if not destination.exists():
        destination.write_text(managed + "\n", encoding="utf-8")
        return f"Installed game-development AGENTS guidance: {destination}"

    text = destination.read_text(encoding="utf-8")
    start = text.find(_AGENTS_START)
    end = text.find(_AGENTS_END)

    if start == -1 and end == -1:
        separator = "" if not text.strip() else "\n\n"
        destination.write_text(
            text.rstrip() + separator + managed + "\n",
            encoding="utf-8",
        )
        return f"Appended game-development AGENTS guidance: {destination}"

    if start == -1 or end == -1 or end < start:
        raise RuntimeError(
            f"{destination} has an incomplete blender-godot-super managed AGENTS block"
        )

    end += len(_AGENTS_END)
    current_block = text[start:end].strip()
    if current_block == managed:
        return f"Found current game-development AGENTS guidance: {destination}"

    if not force:
        return (
            f"Preserved customized game-development AGENTS guidance: {destination} "
            "(use --force to refresh the managed block)"
        )

    prefix = text[:start].rstrip()
    suffix = text[end:].strip()
    parts = [part for part in (prefix, managed, suffix) if part]
    destination.write_text("\n\n".join(parts) + "\n", encoding="utf-8")
    return f"Refreshed game-development AGENTS guidance: {destination}"


def _install_game_design(project_root: Path) -> str:
    destination = project_root / "GAME_DESIGN.md"
    if destination.exists():
        return f"Preserved project-owned game design record: {destination}"

    destination.write_text(
        _template("GAME_DESIGN.md").rstrip() + "\n",
        encoding="utf-8",
    )
    return f"Created project-owned game design record: {destination}"


def install_game_methodology(project_root: Path, *, force: bool = False) -> list[str]:
    """Install skills, AGENTS guidance, and a durable game-design record."""

    messages: list[str] = []

    for skill_name in SKILL_NAMES:
        relative = f".agents/skills/{skill_name}/SKILL.md"
        destination = project_root.joinpath(*PurePosixPath(relative).parts)
        messages.append(
            _write_managed_file(
                destination,
                _template(relative),
                force=force,
                label=f"Codex skill {skill_name}",
            )
        )

    messages.append(_install_agents_append(project_root, force=force))
    messages.append(_install_game_design(project_root))
    return messages
