"""Exercise one unified MCP against live Blender and Godot editor processes."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import shutil
import signal
import socket
import tempfile
import time
from pathlib import Path
from typing import Any

from fastmcp import Client
from fastmcp.exceptions import ResourceError
from mcp.shared.exceptions import MCPError

from super_mcp.installations import BLENDER, GODOT, install

ROOT = Path(__file__).resolve().parents[1]
STARTUP_TIMEOUT_SECONDS = 60.0
POLL_INTERVAL_SECONDS = 0.5


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--blender", type=Path, required=True)
    parser.add_argument("--godot", type=Path, required=True)
    return parser.parse_args()


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def _write_godot_project(project: Path) -> None:
    project.mkdir(parents=True, exist_ok=True)
    (project / "project.godot").write_text(
        """config_version=5

[application]

config/name="SuperDualSmoke"
config/features=PackedStringArray("4.7")

[editor_plugins]

enabled=PackedStringArray("res://addons/godot_mcp/plugin.cfg")
"""
    )


def _tail(path: Path, limit: int = 12000) -> str:
    if not path.exists():
        return ""
    text = path.read_text(errors="replace")
    return text[-limit:]


def _assert_running(
    process: asyncio.subprocess.Process,
    *,
    name: str,
    log_path: Path,
) -> None:
    if process.returncode is not None:
        raise RuntimeError(
            f"{name} exited early with code {process.returncode}.\n{_tail(log_path)}"
        )


async def _read_json_resource(client: Client[Any], uri: str) -> dict[str, Any]:
    result = await client.read_resource(uri)
    if len(result) != 1:
        raise RuntimeError(f"{uri} returned {len(result)} contents")

    text = getattr(result[0], "text", None)
    if not isinstance(text, str):
        raise TypeError(f"{uri} did not return text JSON")

    payload = json.loads(text)
    if not isinstance(payload, dict):
        raise TypeError(f"{uri} JSON must be an object")
    return payload


async def _blender_port_ready(port: int) -> bool:
    try:
        _reader, writer = await asyncio.open_connection("127.0.0.1", port)
    except OSError:
        return False

    writer.close()
    await writer.wait_closed()
    return True


async def _wait_for_live_resources(
    client: Client[Any],
    *,
    blender: asyncio.subprocess.Process,
    blender_port: int,
    blender_log: Path,
    godot: asyncio.subprocess.Process,
    godot_log: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    deadline = time.monotonic() + STARTUP_TIMEOUT_SECONDS
    last_error = ""

    while time.monotonic() < deadline:
        _assert_running(blender, name="Blender", log_path=blender_log)
        _assert_running(godot, name="Godot", log_path=godot_log)

        if not await _blender_port_ready(blender_port):
            await asyncio.sleep(POLL_INTERVAL_SECONDS)
            continue

        try:
            blender_result, godot_result = await asyncio.gather(
                _read_json_resource(client, "blender://scene"),
                _read_json_resource(client, "godot://project/info"),
            )
        except (MCPError, ResourceError, RuntimeError, TypeError, ValueError) as exc:
            last_error = repr(exc)
            await asyncio.sleep(POLL_INTERVAL_SECONDS)
            continue

        if godot_result.get("error"):
            last_error = f"Godot resource error: {godot_result}"
            await asyncio.sleep(POLL_INTERVAL_SECONDS)
            continue

        return blender_result, godot_result

    raise TimeoutError(
        "Timed out waiting for both real hosts through the unified MCP.\n"
        f"Last MCP error: {last_error}\n"
        f"--- Blender log ---\n{_tail(blender_log)}\n"
        f"--- Godot log ---\n{_tail(godot_log)}"
    )


async def _terminate(process: asyncio.subprocess.Process) -> None:
    if process.returncode is not None:
        return

    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return

    try:
        await asyncio.wait_for(process.wait(), timeout=10.0)
        return
    except TimeoutError:
        pass

    if process.returncode is None:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            return
        await process.wait()


async def _run(blender_bin: Path, godot_bin: Path) -> None:
    blender_port = _free_port()
    godot_port = _free_port()
    godot_url = f"ws://127.0.0.1:{godot_port}"

    os.environ["BLENDER_HOST"] = "127.0.0.1"
    os.environ["BLENDER_PORT"] = str(blender_port)
    os.environ["GODOT_MCP_BRIDGE_URL"] = godot_url

    from super_mcp.server import build_server

    xvfb_run = shutil.which("xvfb-run")
    if xvfb_run is None:
        raise FileNotFoundError("xvfb-run is required for the live Blender editor smoke")

    with tempfile.TemporaryDirectory(prefix="super-dual-host-") as temp:
        root = Path(temp)
        blender_addons = root / "blender-addons"
        godot_project = root / "godot-project"
        blender_log = root / "blender.log"
        godot_log = root / "godot.log"

        _write_godot_project(godot_project)
        install(BLENDER, blender_addons / "claude_blender")
        install(GODOT, godot_project / "addons" / "godot_mcp")

        with blender_log.open("wb") as blender_out, godot_log.open("wb") as godot_out:
            async with Client(build_server()) as client:
                blender = await asyncio.create_subprocess_exec(
                    xvfb_run,
                    "-a",
                    str(blender_bin),
                    "--factory-startup",
                    "--python",
                    str(
                        ROOT
                        / "tests"
                        / "integration"
                        / "blender"
                        / "serve_upstream_addon.py"
                    ),
                    "--",
                    "--addons-dir",
                    str(blender_addons),
                    "--port",
                    str(blender_port),
                    stdout=blender_out,
                    stderr=asyncio.subprocess.STDOUT,
                    start_new_session=True,
                )
                godot = await asyncio.create_subprocess_exec(
                    str(godot_bin),
                    "--headless",
                    "--editor",
                    "--path",
                    str(godot_project),
                    stdout=godot_out,
                    stderr=asyncio.subprocess.STDOUT,
                    env={**os.environ, "GODOT_MCP_BRIDGE_URL": godot_url},
                    start_new_session=True,
                )

                try:
                    blender_state, godot_state = await _wait_for_live_resources(
                        client,
                        blender=blender,
                        blender_port=blender_port,
                        blender_log=blender_log,
                        godot=godot,
                        godot_log=godot_log,
                    )

                    _assert_running(blender, name="Blender", log_path=blender_log)
                    _assert_running(godot, name="Godot", log_path=godot_log)

                    assert blender_state["name"] == "SuperDualBlender"
                    assert blender_state["object_count"] == 3
                    blender_names = {item["name"] for item in blender_state["objects"]}
                    assert blender_names == {
                        "SuperDualCube",
                        "SuperDualCamera",
                        "SuperDualKey",
                    }

                    assert godot_state["name"] == "SuperDualSmoke"
                    assert str(godot_state["godot_version"]).startswith("4.7.2")
                    assert godot_state["project_path"]

                    print(
                        "Dual-editor smoke passed: live Blender and Godot state were "
                        "read through one unified MCP client while both editors ran."
                    )
                finally:
                    await _terminate(godot)
                    await _terminate(blender)


def main() -> None:
    args = _args()
    asyncio.run(_run(args.blender.resolve(), args.godot.resolve()))


if __name__ == "__main__":
    main()
