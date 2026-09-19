"""Create a deterministic Blender document for bridge integration tests."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import bpy


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    separator = sys.argv.index("--") if "--" in sys.argv else len(sys.argv)
    return parser.parse_args(sys.argv[separator + 1 :])


def main() -> None:
    args = _args()

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    scene = bpy.context.scene
    scene.name = "SuperFixture"

    bpy.ops.mesh.primitive_cube_add(location=(0.0, 0.0, 0.0))
    cube = bpy.context.object
    cube.name = "SuperCube"

    camera_data = bpy.data.cameras.new("SuperCameraData")
    camera = bpy.data.objects.new("SuperCamera", camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera

    light_data = bpy.data.lights.new(name="SuperKeyData", type="AREA")
    light = bpy.data.objects.new(name="SuperKey", object_data=light_data)
    scene.collection.objects.link(light)

    bpy.context.view_layer.objects.active = cube
    cube.select_set(True)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(args.output))


if __name__ == "__main__":
    main()
