"""Pinned upstream editor integration installer."""

from __future__ import annotations

import argparse
import io
import shutil
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


@dataclass(frozen=True)
class UpstreamIntegration:
    name: str
    repository: str
    revision: str
    source_dir: str

    @property
    def archive_url(self) -> str:
        return f"https://github.com/{self.repository}/archive/{self.revision}.zip"


BLENDER = UpstreamIntegration(
    name="claude-blender",
    repository="minihellboy/claude-blender",
    revision="5087d87212e0acf3225307c2b3512659c425cc5e",
    source_dir="claude_blender/blender_addon",
)
GODOT = UpstreamIntegration(
    name="godot-mcp",
    repository="hybridindie/godot-mcp",
    revision="daf1cf649f41fc95c403e03859d0461a5b272333",
    source_dir="godot/addons/godot_mcp",
)


def _download_archive(spec: UpstreamIntegration) -> bytes:
    request = urllib.request.Request(
        spec.archive_url,
        headers={"User-Agent": "blender-godot-super/0.0.0"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def _install_from_archive(
    archive: bytes,
    *,
    source_dir: str,
    destination: Path,
    force: bool = False,
) -> None:
    if destination.exists():
        if not force:
            raise FileExistsError(f"Destination already exists: {destination}")
        shutil.rmtree(destination)

    destination.mkdir(parents=True, exist_ok=True)
    source_parts = PurePosixPath(source_dir).parts
    copied = 0

    with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
        for info in bundle.infolist():
            if info.is_dir():
                continue
            parts = PurePosixPath(info.filename).parts
            if len(parts) <= len(source_parts):
                continue
            if tuple(parts[1 : 1 + len(source_parts)]) != source_parts:
                continue

            relative = PurePosixPath(*parts[1 + len(source_parts) :])
            if not relative.parts or ".." in relative.parts:
                continue

            target = destination.joinpath(*relative.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(bundle.read(info))
            copied += 1

    if copied == 0:
        shutil.rmtree(destination, ignore_errors=True)
        raise RuntimeError(f"Source directory not found in archive: {source_dir}")


def install(spec: UpstreamIntegration, destination: Path, *, force: bool = False) -> None:
    archive = _download_archive(spec)
    _install_from_archive(
        archive,
        source_dir=spec.source_dir,
        destination=destination,
        force=force,
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Install pinned Blender/Godot editor integrations used by "
            "blender-godot-super."
        )
    )
    parser.add_argument(
        "--blender-addons",
        type=Path,
        help="Blender scripts/addons directory. Installs as <dir>/claude_blender.",
    )
    parser.add_argument(
        "--godot-project",
        type=Path,
        help="Godot project directory containing project.godot.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing installed integration directory.",
    )
    args = parser.parse_args()
    if args.blender_addons is None and args.godot_project is None:
        parser.error("provide --blender-addons, --godot-project, or both")
    return args


def main() -> None:
    args = _parse_args()

    if args.blender_addons is not None:
        destination = args.blender_addons.expanduser().resolve() / "claude_blender"
        install(BLENDER, destination, force=args.force)
        print(f"Installed Blender add-on to {destination}")

    if args.godot_project is not None:
        project = args.godot_project.expanduser().resolve()
        if not (project / "project.godot").is_file():
            raise FileNotFoundError(f"Godot project.godot not found in {project}")
        destination = project / "addons" / "godot_mcp"
        install(GODOT, destination, force=args.force)
        print(f"Installed Godot plug-in to {destination}")


