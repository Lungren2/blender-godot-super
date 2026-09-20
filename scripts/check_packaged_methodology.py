"""Verify that the installable wheel contains the game methodology templates."""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

from super_mcp.methodology import SKILL_NAMES


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("wheel", type=Path)
    return parser


def main() -> None:
    args = _parser().parse_args()
    required = {
        "super_mcp/game_repo_template/AGENTS.append.md",
        "super_mcp/game_repo_template/GAME_DESIGN.md",
        *{
            f"super_mcp/game_repo_template/.agents/skills/{name}/SKILL.md"
            for name in SKILL_NAMES
        },
    }

    with zipfile.ZipFile(args.wheel) as wheel:
        names = set(wheel.namelist())

    missing = sorted(required - names)
    if missing:
        for path in missing:
            print(f"wheel-methodology: missing {path}")
        raise SystemExit(1)

    print(f"Wheel methodology OK ({len(required)} templates).")


if __name__ == "__main__":
    main()
