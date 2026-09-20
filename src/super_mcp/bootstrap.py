"""Install blender-godot-super into a Codex game repository."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections.abc import Mapping
from importlib import metadata
from pathlib import Path

from super_mcp.astra import ASTRA_ALLOWED_TOOLS
from super_mcp.installations import BLENDER, GODOT, UpstreamIntegration, install

PACKAGE_NAME = "blender-godot-super"
DEFAULT_PACKAGE_SOURCE = "git+https://github.com/Lungren2/blender-godot-super.git@main"
MCP_SERVER_ID = "blender-godot-super"
GODOT_PLUGIN_URI = "res://addons/godot_mcp/plugin.cfg"
_MANAGED_COMMENT = "# Managed by blender-godot-super-init."
_DISCOVERY_SKIP_DIRS = {".git", ".godot", ".super-mcp", ".venv", "node_modules"}


def _toml_string(value: str) -> str:
    return json.dumps(value)


def detect_package_source() -> str:
    """Return a reproducible uv package source for the running installation."""

    try:
        distribution = metadata.distribution(PACKAGE_NAME)
    except metadata.PackageNotFoundError:
        return DEFAULT_PACKAGE_SOURCE

    direct_url = distribution.read_text("direct_url.json")
    if direct_url:
        try:
            payload = json.loads(direct_url)
        except json.JSONDecodeError:
            payload = {}
        vcs_info = payload.get("vcs_info")
        url = payload.get("url")
        if (
            isinstance(vcs_info, dict)
            and vcs_info.get("vcs") == "git"
            and isinstance(url, str)
            and url.startswith(("https://", "http://", "ssh://"))
        ):
            revision = vcs_info.get("commit_id") or vcs_info.get("requested_revision")
            if isinstance(revision, str) and revision:
                return f"git+{url.removeprefix('git+')}@{revision}"

    if distribution.version and distribution.version != "0.0.0":
        return f"{PACKAGE_NAME}=={distribution.version}"
    return DEFAULT_PACKAGE_SOURCE


def render_codex_config_section(package_source: str) -> str:
    """Render the project-scoped Codex MCP section."""

    lines = [
        _MANAGED_COMMENT,
        f"[mcp_servers.{MCP_SERVER_ID}]",
        'command = "uvx"',
        "args = [",
        f"  {_toml_string('--from')},",
        f"  {_toml_string(package_source)},",
        f"  {_toml_string('blender-godot-super')},",
        f"  {_toml_string('--profile')},",
        f"  {_toml_string('astra')},",
        "]",
        'cwd = "."',
        "required = true",
        "startup_timeout_sec = 60",
        "tool_timeout_sec = 180",
        "enabled_tools = [",
    ]
    lines.extend(f"  {_toml_string(name)}," for name in ASTRA_ALLOWED_TOOLS)
    lines.extend(["]", ""])
    return "\n".join(lines)


def _table_header(line: str) -> str:
    return line.split("#", 1)[0].strip()


def _is_target_section_header(line: str) -> bool:
    header = _table_header(line)
    return header in {
        f"[mcp_servers.{MCP_SERVER_ID}]",
        f'[mcp_servers."{MCP_SERVER_ID}"]',
        f"[mcp_servers.'{MCP_SERVER_ID}']",
    }


def _section_bounds(lines: list[str]) -> tuple[int, int] | None:
    start = next(
        (index for index, line in enumerate(lines) if _is_target_section_header(line)),
        None,
    )
    if start is None:
        return None
    end = len(lines)
    for index in range(start + 1, len(lines)):
        header = _table_header(lines[index])
        if header.startswith("[") and header.endswith("]"):
            end = index
            break
    if start > 0 and lines[start - 1].strip() == _MANAGED_COMMENT:
        start -= 1
    return start, end


def write_codex_config(
    project_root: Path,
    package_source: str,
    *,
    force: bool = False,
) -> Path:
    """Add or replace the managed project MCP section."""

    config_path = project_root / ".codex" / "config.toml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    managed = render_codex_config_section(package_source)

    if not config_path.exists():
        config_path.write_text(managed, encoding="utf-8")
        return config_path

    text = config_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    bounds = _section_bounds(lines)
    if bounds is None:
        separator = "" if not text.strip() else "\n\n"
        config_path.write_text(text.rstrip() + separator + managed, encoding="utf-8")
        return config_path

    start, end = bounds
    current = "\n".join(lines[start:end]).rstrip() + "\n"
    if current == managed:
        return config_path
    if not force:
        raise FileExistsError(
            f"{config_path} already defines {MCP_SERVER_ID}; rerun with --force "
            "to replace that section"
        )

    replacement = managed.rstrip().splitlines()
    config_path.write_text(
        "\n".join([*lines[:start], *replacement, *lines[end:]]).rstrip() + "\n",
        encoding="utf-8",
    )
    return config_path


def ensure_gitignore(project_root: Path) -> Path:
    """Ignore local audit and runtime artifacts in the consumer repository."""

    gitignore = project_root / ".gitignore"
    entry = ".super-mcp/"
    if gitignore.exists():
        text = gitignore.read_text(encoding="utf-8")
        if any(line.strip() == entry for line in text.splitlines()):
            return gitignore
        prefix = text.rstrip()
        text = f"{prefix}\n{entry}\n" if prefix else f"{entry}\n"
    else:
        text = f"{entry}\n"
    gitignore.write_text(text, encoding="utf-8")
    return gitignore


def discover_godot_project(project_root: Path) -> Path | None:
    """Find one Godot project below the repository root."""

    direct = project_root / "project.godot"
    if direct.is_file():
        return project_root

    matches: list[Path] = []
    for current, dirnames, filenames in os.walk(project_root):
        dirnames[:] = [
            name
            for name in dirnames
            if name not in _DISCOVERY_SKIP_DIRS and not name.startswith(".")
        ]
        if "project.godot" in filenames:
            matches.append(Path(current))

    unique = sorted(set(matches))
    if not unique:
        return None
    if len(unique) > 1:
        choices = ", ".join(str(path.relative_to(project_root)) for path in unique)
        raise RuntimeError(
            "Multiple Godot projects found. Pass --godot-project explicitly: "
            f"{choices}"
        )
    return unique[0]


def ensure_godot_plugin_enabled(project_file: Path) -> bool:
    """Enable the installed Godot MCP plug-in in project.godot."""

    text = project_file.read_text(encoding="utf-8")
    if GODOT_PLUGIN_URI in text:
        return False

    lines = text.splitlines()
    header = "[editor_plugins]"
    try:
        start = lines.index(header)
    except ValueError:
        suffix = "" if not text.strip() else "\n\n"
        block = f'{header}\n\nenabled=PackedStringArray("{GODOT_PLUGIN_URI}")\n'
        project_file.write_text(text.rstrip() + suffix + block, encoding="utf-8")
        return True

    end = len(lines)
    for index in range(start + 1, len(lines)):
        if lines[index].startswith("[") and lines[index].endswith("]"):
            end = index
            break

    enabled_pattern = re.compile(
        r"^(?P<prefix>\s*enabled\s*=\s*PackedStringArray\()"
        r"(?P<body>.*)"
        r"(?P<suffix>\)\s*)$"
    )
    for index in range(start + 1, end):
        match = enabled_pattern.match(lines[index])
        if match is None:
            continue
        body = match.group("body").strip()
        addition = _toml_string(GODOT_PLUGIN_URI)
        new_body = f"{body}, {addition}" if body else addition
        lines[index] = f"{match.group('prefix')}{new_body}{match.group('suffix')}"
        project_file.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
        return True

    lines.insert(start + 1, f'enabled=PackedStringArray("{GODOT_PLUGIN_URI}")')
    project_file.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return True


def _version_key(name: str) -> tuple[int, ...] | None:
    parts = name.split(".")
    if len(parts) < 2 or not all(part.isdigit() for part in parts):
        return None
    return tuple(int(part) for part in parts)


def blender_addons_candidates(
    *,
    home: Path | None = None,
    platform: str | None = None,
    environ: Mapping[str, str] | None = None,
) -> list[Path]:
    """Return likely Blender user add-on directories, newest version first."""

    resolved_home = home or Path.home()
    resolved_platform = platform or sys.platform
    resolved_env = environ if environ is not None else os.environ

    explicit_scripts = resolved_env.get("BLENDER_USER_SCRIPTS")
    if explicit_scripts:
        return [Path(explicit_scripts).expanduser() / "addons"]

    if resolved_platform == "darwin":
        base = resolved_home / "Library" / "Application Support" / "Blender"
    elif resolved_platform.startswith("win"):
        appdata = resolved_env.get("APPDATA")
        if not appdata:
            return []
        base = Path(appdata) / "Blender Foundation" / "Blender"
    else:
        config_home = Path(
            resolved_env.get("XDG_CONFIG_HOME", str(resolved_home / ".config"))
        )
        base = config_home / "blender"

    if not base.is_dir():
        return []

    version_dirs: list[tuple[tuple[int, ...], Path]] = []
    for child in base.iterdir():
        if not child.is_dir():
            continue
        version = _version_key(child.name)
        if version is not None:
            version_dirs.append((version, child))

    return [
        version_dir / "scripts" / "addons"
        for _version, version_dir in sorted(version_dirs, reverse=True)
    ]


def _install_if_needed(
    spec: UpstreamIntegration, destination: Path, *, force: bool
) -> bool:
    if destination.exists() and not force:
        return False
    install(spec, destination, force=force)
    return True


def _resolve_relative(root: Path, value: Path) -> Path:
    expanded = value.expanduser()
    if expanded.is_absolute():
        return expanded.resolve()
    return (root / expanded).resolve()


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="blender-godot-super-init",
        description="Configure a game repository for Codex + Blender/Godot MCP.",
    )
    parser.add_argument(
        "project",
        nargs="?",
        type=Path,
        default=Path("."),
        help="Repository root. Defaults to the current directory.",
    )
    parser.add_argument(
        "--source",
        help=(
            "uv package source written to .codex/config.toml. Defaults to the exact "
            "Git commit for a VCS install when available."
        ),
    )
    parser.add_argument(
        "--godot-project",
        type=Path,
        help="Godot project directory. Auto-detected when omitted.",
    )
    parser.add_argument(
        "--blender-addons",
        type=Path,
        help="Blender scripts/addons directory. Auto-detected when possible.",
    )
    parser.add_argument("--skip-godot", action="store_true")
    parser.add_argument("--skip-blender", action="store_true")
    parser.add_argument("--no-gitignore", action="store_true")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace the managed Codex MCP section and installed editor integrations.",
    )
    return parser


def main() -> None:
    args = _parser().parse_args()
    project_root = args.project.expanduser().resolve()
    if not project_root.is_dir():
        raise NotADirectoryError(project_root)

    package_source = args.source or detect_package_source()
    config_path = write_codex_config(project_root, package_source, force=args.force)
    print(f"Configured Codex MCP: {config_path}")
    print(f"Pinned MCP package source: {package_source}")

    if not args.no_gitignore:
        gitignore = ensure_gitignore(project_root)
        print(f"Ensured local artifacts are ignored: {gitignore}")

    if not args.skip_godot:
        godot_project: Path | None
        if args.godot_project is not None:
            godot_project = _resolve_relative(project_root, args.godot_project)
        else:
            godot_project = discover_godot_project(project_root)
        if godot_project is None:
            print("Godot project not found; skipped Godot plug-in installation.")
        else:
            project_file = godot_project / "project.godot"
            if not project_file.is_file():
                raise FileNotFoundError(project_file)
            destination = godot_project / "addons" / "godot_mcp"
            changed = _install_if_needed(GODOT, destination, force=args.force)
            state = "Installed" if changed else "Found existing"
            print(f"{state} Godot MCP plug-in: {destination}")
            if ensure_godot_plugin_enabled(project_file):
                print(f"Enabled Godot MCP plug-in in {project_file}")

    if not args.skip_blender:
        blender_addons: Path | None
        if args.blender_addons is not None:
            blender_addons = _resolve_relative(project_root, args.blender_addons)
        else:
            candidates = blender_addons_candidates()
            blender_addons = candidates[0] if candidates else None

        if blender_addons is None:
            print(
                "Blender add-ons directory not found. Re-run with "
                "--blender-addons /path/to/scripts/addons after Blender is installed."
            )
        else:
            destination = blender_addons / "claude_blender"
            changed = _install_if_needed(BLENDER, destination, force=args.force)
            state = "Installed" if changed else "Found existing"
            print(f"{state} Blender add-on: {destination}")
            print("Enable 'Claude Blender' once in Blender Preferences > Add-ons.")

    print("Repo setup complete. Trust the project in Codex, then run /mcp to verify.")


if __name__ == "__main__":
    main()
