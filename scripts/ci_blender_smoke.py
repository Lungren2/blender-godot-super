"""Exercise blender://scene against real Blender documents."""

from __future__ import annotations

import argparse
import asyncio
import json
import socket
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

from mcp import Client

from super_mcp.server import build_server

ROOT = Path(__file__).resolve().parents[1]
BRIDGE_HOST = "127.0.0.1"
BRIDGE_PORT = 8765
STARTUP_TIMEOUT_SECONDS = 15.0


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--blender", type=Path, required=True)
    parser.add_argument("--external-fixture", type=Path, required=True)
    return parser.parse_args()


def _run_blender(blender: Path, *args: str) -> None:
    subprocess.run([str(blender), *args], check=True)


def _make_fixture(blender: Path, output: Path) -> None:
    _run_blender(
        blender,
        "--background",
        "--factory-startup",
        "--python",
        str(ROOT / "tests" / "integration" / "blender" / "make_fixture.py"),
        "--",
        "--output",
        str(output),
    )


def _wait_for_bridge(process: subprocess.Popen[bytes], log_path: Path) -> None:
    deadline = time.monotonic() + STARTUP_TIMEOUT_SECONDS

    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(
                "Blender exited before the bridge became ready.\n"
                + log_path.read_text(errors="replace")
            )

        try:
            with socket.create_connection(
                (BRIDGE_HOST, BRIDGE_PORT),
                timeout=0.25,
            ):
                return
        except OSError:
            time.sleep(0.1)

    raise TimeoutError(
        "Timed out waiting for the Blender bridge.\n"
        + log_path.read_text(errors="replace")
    )


async def _read_scene() -> dict[str, Any]:
    async with Client(build_server(), raise_exceptions=True) as client:
        result = await client.read_resource("blender://scene")

    if len(result.contents) != 1:
        raise RuntimeError("blender://scene returned an unexpected number of contents")

    text = getattr(result.contents[0], "text", None)
    if not isinstance(text, str):
        raise TypeError("blender://scene did not return text JSON")

    payload = json.loads(text)
    if not isinstance(payload, dict):
        raise TypeError("blender://scene JSON must be an object")
    return payload


def _inspect_document(blender: Path, document: Path) -> dict[str, Any]:
    with tempfile.NamedTemporaryFile(prefix="super-blender-", suffix=".log") as log:
        log_path = Path(log.name)
        process = subprocess.Popen(
            [
                str(blender),
                "--background",
                str(document),
                "--python",
                str(ROOT / "tests" / "integration" / "blender" / "serve_bridge.py"),
            ],
            stdout=log,
            stderr=subprocess.STDOUT,
        )

        try:
            _wait_for_bridge(process, log_path)
            return asyncio.run(_read_scene())
        finally:
            process.terminate()
            try:
                process.wait(timeout=5.0)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5.0)


def _assert_generated_fixture(payload: dict[str, Any]) -> None:
    assert payload["host"]["kind"] == "blender"
    assert payload["scene"]["name"] == "SuperFixture"
    assert payload["scene"]["active_object"] == "SuperCube"
    assert payload["scene"]["camera"] == "SuperCamera"

    names = {item["name"] for item in payload["scene"]["objects"]}
    assert {"SuperCube", "SuperCamera", "SuperKey"} <= names


def _assert_external_fixture(payload: dict[str, Any], fixture: Path) -> None:
    assert payload["host"]["kind"] == "blender"
    assert Path(payload["document"]["filepath"]).name == fixture.name
    assert payload["scene"]["name"]
    assert payload["scene"]["objects"]


def main() -> None:
    args = _args()

    with tempfile.TemporaryDirectory(prefix="super-blender-fixture-") as temp_dir:
        generated = Path(temp_dir) / "generated.blend"
        _make_fixture(args.blender, generated)

        generated_payload = _inspect_document(args.blender, generated)
        _assert_generated_fixture(generated_payload)

        external_payload = _inspect_document(args.blender, args.external_fixture)
        _assert_external_fixture(external_payload, args.external_fixture)

    print("Blender integration smoke passed for generated and external .blend files.")


if __name__ == "__main__":
    main()
