import io
import zipfile
from pathlib import Path

import pytest

from super_mcp.installations import _install_from_archive


def _archive() -> bytes:
    payload = io.BytesIO()
    with zipfile.ZipFile(payload, "w") as bundle:
        bundle.writestr("repo-deadbeef/addons/example/plugin.cfg", "[plugin]\n")
        bundle.writestr("repo-deadbeef/addons/example/main.gd", "extends Node\n")
        bundle.writestr("repo-deadbeef/README.md", "ignore me\n")
    return payload.getvalue()


def test_installs_only_requested_subtree(tmp_path: Path) -> None:
    destination = tmp_path / "installed"

    _install_from_archive(
        _archive(),
        source_dir="addons/example",
        destination=destination,
    )

    assert (destination / "plugin.cfg").read_text() == "[plugin]\n"
    assert (destination / "main.gd").read_text() == "extends Node\n"
    assert not (destination / "README.md").exists()


def test_refuses_to_replace_existing_install_without_force(tmp_path: Path) -> None:
    destination = tmp_path / "installed"
    destination.mkdir()

    with pytest.raises(FileExistsError):
        _install_from_archive(
            _archive(),
            source_dir="addons/example",
            destination=destination,
        )
