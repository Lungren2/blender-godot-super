"""Exercise mutation, visual evidence, save, restart, and persistence in both editors."""

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

from super_mcp.astra import ASTRA_GODOT_TOOLSETS
from super_mcp.installations import BLENDER, GODOT, install

ROOT = Path(__file__).resolve().parents[1]
STARTUP_TIMEOUT_SECONDS = 75.0
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

config/name="SuperPersistenceSmoke"
run/main_scene="res://Smoke.tscn"
config/features=PackedStringArray("4.7")

[display]

window/size/viewport_width=320
window/size/viewport_height=180

[rendering]

renderer/rendering_method="gl_compatibility"
renderer/rendering_method.mobile="gl_compatibility"

[editor_plugins]

enabled=PackedStringArray("res://addons/godot_mcp/plugin.cfg")
""",
        encoding="utf-8",
    )
    (project / "Smoke.tscn").write_text(
        """[gd_scene format=3]

[node name="Smoke" type="Control"]
layout_mode = 3
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2

[node name="Backdrop" type="ColorRect" parent="."]
layout_mode = 0
offset_right = 320.0
offset_bottom = 180.0
color = Color(0.08, 0.1, 0.16, 1)
""",
        encoding="utf-8",
    )


def _tail(path: Path, limit: int = 12000) -> str:
    if not path.exists():
        return ""
    return path.read_text(errors="replace")[-limit:]


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


async def _port_ready(port: int) -> bool:
    try:
        _reader, writer = await asyncio.open_connection("127.0.0.1", port)
    except OSError:
        return False
    writer.close()
    await writer.wait_closed()
    return True


async def _wait_for_hosts(
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
        if not await _port_ready(blender_port):
            await asyncio.sleep(POLL_INTERVAL_SECONDS)
            continue
        try:
            blender_state, godot_state = await asyncio.gather(
                _read_json_resource(client, "blender://scene"),
                _read_json_resource(client, "godot://project/info"),
            )
        except (MCPError, ResourceError, RuntimeError, TypeError, ValueError) as exc:
            last_error = repr(exc)
            await asyncio.sleep(POLL_INTERVAL_SECONDS)
            continue
        if godot_state.get("error"):
            last_error = f"Godot resource error: {godot_state}"
            await asyncio.sleep(POLL_INTERVAL_SECONDS)
            continue
        return blender_state, godot_state
    raise TimeoutError(
        "Timed out waiting for both real hosts.\n"
        f"Last MCP error: {last_error}\n"
        f"--- Blender log ---\n{_tail(blender_log)}\n"
        f"--- Godot log ---\n{_tail(godot_log)}"
    )


async def _call(
    client: Client[Any],
    name: str,
    arguments: dict[str, Any] | None = None,
) -> Any:
    result = await client.call_tool(name, arguments or {})
    if result.is_error:
        raise RuntimeError(f"{name} returned an MCP error: {result.content}")
    return result


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


async def _start_blender(
    blender_bin: Path,
    *,
    xvfb_run: str,
    addons_dir: Path,
    port: int,
    log_path: Path,
    blend_file: Path | None = None,
    preserve_scene: bool = False,
) -> asyncio.subprocess.Process:
    command = [xvfb_run, "-a", str(blender_bin), "--factory-startup"]
    if blend_file is not None:
        command.append(str(blend_file))
    command.extend(
        [
            "--python",
            str(ROOT / "tests" / "integration" / "blender" / "serve_upstream_addon.py"),
            "--",
            "--addons-dir",
            str(addons_dir),
            "--port",
            str(port),
        ]
    )
    if preserve_scene:
        command.append("--preserve-scene")
    output = await asyncio.to_thread(log_path.open, "wb")
    try:
        return await asyncio.create_subprocess_exec(
            *command,
            stdout=output,
            stderr=asyncio.subprocess.STDOUT,
            start_new_session=True,
        )
    finally:
        await asyncio.to_thread(output.close)


async def _start_godot(
    godot_bin: Path,
    *,
    xvfb_run: str,
    project: Path,
    bridge_url: str,
    log_path: Path,
) -> asyncio.subprocess.Process:
    output = await asyncio.to_thread(log_path.open, "wb")
    try:
        return await asyncio.create_subprocess_exec(
            xvfb_run,
            "-a",
            str(godot_bin),
            "--editor",
            "--path",
            str(project),
            stdout=output,
            stderr=asyncio.subprocess.STDOUT,
            env={**os.environ, "GODOT_MCP_BRIDGE_URL": bridge_url},
            start_new_session=True,
        )
    finally:
        await asyncio.to_thread(output.close)


def _assert_nonempty_file(path: Path) -> None:
    assert path.is_file() and path.stat().st_size > 100


def _scene_contains(path: Path, needle: str) -> bool:
    return needle in path.read_text(encoding="utf-8")


def _collect_tree_names(node: Any) -> set[str]:
    if not isinstance(node, dict):
        return set()
    names: set[str] = set()
    name = node.get("name")
    if isinstance(name, str):
        names.add(name)
    children = node.get("children", [])
    if isinstance(children, list):
        for child in children:
            names.update(_collect_tree_names(child))
    return names


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


def _assert_audit(audit_dir: Path) -> None:
    actions = _load_jsonl(audit_dir / "actions.jsonl")
    artifacts = _load_jsonl(audit_dir / "artifacts.jsonl")
    completed_names = [
        str(record["name"])
        for record in actions
        if record.get("status") == "completed"
    ]
    required = {
        "blender_checkpoint",
        "blender_add_object",
        "blender_render",
        "blender_save",
        "godot_scene_edit_create_node",
        "godot_editor_capture_screenshot",
        "godot_scene_edit_save_scene",
        "blender://scene",
        "godot://scene/tree",
    }
    missing = sorted(required - set(completed_names))
    assert not missing, f"Audit log is missing required completed actions: {missing}"

    blender_save = max(
        index for index, name in enumerate(completed_names) if name == "blender_save"
    )
    godot_save = max(
        index
        for index, name in enumerate(completed_names)
        if name == "godot_scene_edit_save_scene"
    )
    last_blender_read = max(
        index for index, name in enumerate(completed_names) if name == "blender://scene"
    )
    last_godot_tree = max(
        index for index, name in enumerate(completed_names) if name == "godot://scene/tree"
    )
    assert last_blender_read > blender_save
    assert last_godot_tree > godot_save

    png_artifacts = [
        record for record in artifacts if record.get("media_type") == "image/png"
    ]
    assert len(png_artifacts) >= 2
    for artifact in png_artifacts:
        path = Path(str(artifact["path"]))
        assert path.is_file()
        assert path.stat().st_size > 100


async def _run(blender_bin: Path, godot_bin: Path) -> None:
    xvfb_run = shutil.which("xvfb-run")
    if xvfb_run is None:
        raise FileNotFoundError("xvfb-run is required for the persistence smoke")

    blender_port = _free_port()
    godot_port = _free_port()
    godot_url = f"ws://127.0.0.1:{godot_port}"
    os.environ["BLENDER_HOST"] = "127.0.0.1"
    os.environ["BLENDER_PORT"] = str(blender_port)
    os.environ["GODOT_MCP_BRIDGE_URL"] = godot_url
    os.environ["GODOT_MCP_DEFAULT_TOOLSETS"] = ASTRA_GODOT_TOOLSETS

    from super_mcp.server import build_server

    with tempfile.TemporaryDirectory(prefix="super-persistence-") as temp:
        root = Path(temp)
        blender_addons = root / "blender-addons"
        godot_project = root / "godot-project"
        audit_dir = root / "audit"
        blend_file = root / "persisted.blend"
        blender_render = root / "blender-visual.png"

        _write_godot_project(godot_project)
        install(BLENDER, blender_addons / "claude_blender")
        install(GODOT, godot_project / "addons" / "godot_mcp")

        async with Client(build_server(audit_dir=audit_dir)) as client:
            tools = {tool.name for tool in await client.list_tools()}
            required_tools = {
                "blender_add_object",
                "blender_render",
                "blender_save",
                "godot_scene_edit_create_node",
                "godot_scene_edit_save_scene",
                "godot_editor_capture_screenshot",
            }
            assert required_tools <= tools

            blender_log_1 = root / "blender-1.log"
            godot_log_1 = root / "godot-1.log"
            blender = await _start_blender(
                blender_bin,
                xvfb_run=xvfb_run,
                addons_dir=blender_addons,
                port=blender_port,
                log_path=blender_log_1,
            )
            godot = await _start_godot(
                godot_bin,
                xvfb_run=xvfb_run,
                project=godot_project,
                bridge_url=godot_url,
                log_path=godot_log_1,
            )
            try:
                await _wait_for_hosts(
                    client,
                    blender=blender,
                    blender_port=blender_port,
                    blender_log=blender_log_1,
                    godot=godot,
                    godot_log=godot_log_1,
                )

                await _call(client, "blender_checkpoint", {"label": "persistence-smoke"})
                await _call(
                    client,
                    "blender_add_object",
                    {
                        "object_type": "cube",
                        "name": "AstraPersistedCube",
                        "location": [2.0, 0.0, 0.0],
                    },
                )
                await _call(
                    client,
                    "blender_frame_camera",
                    {"targets": ["AstraPersistedCube"], "margin": 1.3},
                )
                await _call(
                    client,
                    "blender_render",
                    {
                        "filepath": str(blender_render),
                        "engine": "BLENDER_EEVEE_NEXT",
                        "samples": 4,
                        "resolution_x": 320,
                        "resolution_y": 180,
                    },
                )
                _assert_nonempty_file(blender_render)
                await _call(client, "blender_save", {"filepath": str(blend_file)})
                _assert_nonempty_file(blend_file)

                await _call(
                    client,
                    "godot_scene_edit_open_scene",
                    {"scene_path": "res://Smoke.tscn"},
                )
                await _call(
                    client,
                    "godot_scene_edit_create_node",
                    {
                        "parent_path": ".",
                        "node_type": "ColorRect",
                        "node_name": "AstraPersistedPanel",
                    },
                )
                for prop, value in (
                    ("offset_left", 40.0),
                    ("offset_top", 30.0),
                    ("offset_right", 280.0),
                    ("offset_bottom", 150.0),
                ):
                    await _call(
                        client,
                        "godot_scene_edit_set_node_property",
                        {
                            "node_path": "AstraPersistedPanel",
                            "property": prop,
                            "value": value,
                        },
                    )
                await _call(
                    client,
                    "godot_scene_edit_select_nodes",
                    {"node_paths": ["AstraPersistedPanel"]},
                )
                await _call(client, "godot_editor_capture_screenshot")
                await _call(client, "godot_scene_edit_save_scene")
            finally:
                await _terminate(godot)
                await _terminate(blender)

            blender_log_2 = root / "blender-2.log"
            godot_log_2 = root / "godot-2.log"
            blender = await _start_blender(
                blender_bin,
                xvfb_run=xvfb_run,
                addons_dir=blender_addons,
                port=blender_port,
                log_path=blender_log_2,
                blend_file=blend_file,
                preserve_scene=True,
            )
            godot = await _start_godot(
                godot_bin,
                xvfb_run=xvfb_run,
                project=godot_project,
                bridge_url=godot_url,
                log_path=godot_log_2,
            )
            try:
                blender_state, _godot_state = await _wait_for_hosts(
                    client,
                    blender=blender,
                    blender_port=blender_port,
                    blender_log=blender_log_2,
                    godot=godot,
                    godot_log=godot_log_2,
                )
                blender_names = {item["name"] for item in blender_state["objects"]}
                assert "AstraPersistedCube" in blender_names

                await _call(
                    client,
                    "godot_scene_edit_open_scene",
                    {"scene_path": "res://Smoke.tscn"},
                )
                tree = await _read_json_resource(client, "godot://scene/tree")
                assert "AstraPersistedPanel" in _collect_tree_names(tree.get("tree"))
            finally:
                await _terminate(godot)
                await _terminate(blender)

        assert _scene_contains(godot_project / "Smoke.tscn", "AstraPersistedPanel")
        _assert_audit(audit_dir)
        print(
            "Persistence smoke passed: both editors mutated, emitted visual evidence, "
            "saved, restarted, and reloaded persisted state through one MCP."
        )


def main() -> None:
    args = _args()
    asyncio.run(_run(args.blender.resolve(), args.godot.resolve()))


if __name__ == "__main__":
    main()
