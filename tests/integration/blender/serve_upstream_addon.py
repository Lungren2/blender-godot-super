"""Start Minihellboy's real add-on inside a live Blender editor process."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import bpy


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--addons-dir", type=Path, required=True)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--run-seconds", type=float, default=120.0)
    parser.add_argument(
        "--preserve-scene",
        action="store_true",
        help="Serve the loaded .blend instead of replacing it with the CI fixture.",
    )

    argv = sys.argv
    return parser.parse_args(argv[argv.index("--") + 1 :] if "--" in argv else [])


def _make_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    scene = bpy.context.scene
    scene.name = "SuperDualBlender"

    bpy.ops.mesh.primitive_cube_add(location=(0.0, 0.0, 0.0))
    cube = bpy.context.active_object
    assert cube is not None
    cube.name = "SuperDualCube"

    bpy.ops.object.camera_add(location=(4.0, -4.0, 3.0))
    camera = bpy.context.active_object
    assert camera is not None
    camera.name = "SuperDualCamera"
    scene.camera = camera

    bpy.ops.object.light_add(type="AREA", location=(2.0, -2.0, 4.0))
    light = bpy.context.active_object
    assert light is not None
    light.name = "SuperDualKey"

    bpy.ops.object.select_all(action="DESELECT")
    cube.select_set(True)
    bpy.context.view_layer.objects.active = cube


def main() -> None:
    args = _args()
    sys.path.insert(0, str(args.addons_dir))

    import claude_blender

    claude_blender.register()
    if not args.preserve_scene:
        _make_scene()
    claude_blender._setup_handler()

    server = claude_blender.get_server()
    server.port = args.port
    if not server.start():
        raise RuntimeError(server.last_error or "Claude Blender server failed to start")

    deadline = time.monotonic() + args.run_seconds

    def quit_when_done() -> float | None:
        if time.monotonic() < deadline:
            return 0.5
        server.stop()
        bpy.ops.wm.quit_blender()
        return None

    bpy.app.timers.register(quit_when_done, first_interval=0.5)


if __name__ == "__main__":
    main()
