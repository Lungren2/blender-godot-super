"""Repository layout checks used by CI and long-running development loops."""

from __future__ import annotations

import argparse
import subprocess
from collections.abc import Iterable
from pathlib import PurePosixPath

_ALLOWED_TOP_LEVEL = {
    ".github",
    ".gitignore",
    "AGENTS.md",
    "LICENSE",
    "README.md",
    "THIRD_PARTY_NOTICES.md",
    "docs",
    "integrations",
    "licenses",
    "pyproject.toml",
    "scripts",
    "src",
    "tests",
    "uv.lock",
}

_FORBIDDEN_PARTS = {
    ".cache",
    ".godot",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".super-mcp",
    ".venv",
    "__pycache__",
}

_FORBIDDEN_NAMES = {
    ".DS_Store",
    "Thumbs.db",
}

_FORBIDDEN_SUFFIXES = {
    ".blend1",
    ".blend2",
    ".pyc",
    ".pyo",
}

_PYTHON_TOP_LEVEL = {
    "integrations",
    "scripts",
    "src",
    "tests",
}


def find_layout_violations(paths: Iterable[str]) -> list[str]:
    """Return stable repository-layout violations for tracked or candidate files."""

    violations: list[str] = []
    for raw_path in sorted(set(paths)):
        path = PurePosixPath(raw_path)
        if not path.parts:
            continue

        top = path.parts[0]
        if top not in _ALLOWED_TOP_LEVEL:
            violations.append(f"{raw_path}: unexpected top-level path '{top}'")
            continue

        bad_parts = sorted(set(path.parts) & _FORBIDDEN_PARTS)
        if bad_parts:
            violations.append(
                f"{raw_path}: generated/cache directory must not be committed "
                f"({', '.join(bad_parts)})"
            )

        if path.name in _FORBIDDEN_NAMES or path.suffix in _FORBIDDEN_SUFFIXES:
            violations.append(f"{raw_path}: generated/editor artifact must not be committed")

        if path.suffix == ".py" and top not in _PYTHON_TOP_LEVEL:
            violations.append(
                f"{raw_path}: Python code belongs under src/, scripts/, tests/, or integrations/"
            )

    return violations


def _git_paths(*args: str) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        check=True,
        capture_output=True,
    )
    return [
        item.decode("utf-8")
        for item in result.stdout.split(b"\0")
        if item
    ]


def tracked_paths() -> list[str]:
    return _git_paths("ls-files", "-z")


def untracked_paths() -> list[str]:
    return _git_paths("ls-files", "--others", "--exclude-standard", "-z")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check repository filesystem hygiene.")
    parser.add_argument(
        "--include-untracked",
        action="store_true",
        help="Also check non-ignored untracked files in the current working tree.",
    )
    return parser


def main() -> None:
    args = _parser().parse_args()
    paths = tracked_paths()
    if args.include_untracked:
        paths.extend(untracked_paths())

    violations = find_layout_violations(paths)
    if violations:
        for violation in violations:
            print(f"repo-hygiene: {violation}")
        raise SystemExit(1)

    checked = "tracked and untracked" if args.include_untracked else "tracked"
    print(f"Repository hygiene OK ({checked} files).")


if __name__ == "__main__":
    main()
