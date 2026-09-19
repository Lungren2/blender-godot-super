# Blender integration

The first real host slice exposes the active Blender scene as `blender://scene`.

## Boundary

The add-on listens only on `127.0.0.1:8765`.

Socket I/O runs away from Blender's main thread, but the I/O thread never accesses `bpy`. Incoming requests are queued. A `bpy.app.timers` callback drains the queue and performs scene inspection on Blender's main thread.

The bridge currently accepts one method:

```text
scene.inspect
```

It is intentionally read-only.

## Manual smoke test

1. Install or symlink `integrations/blender/addon/blender_godot_super` as a Blender add-on.
2. Enable **Blender Godot Super MCP Bridge**.
3. Open any Blender document.
4. From the repository root run:

```bash
uv run python scripts/smoke_blender_resource.py
```

The script uses the MCP Python client in-process, reads `blender://scene`, and prints the resource returned through the actual Blender bridge.

## Deferred

- authentication beyond loopback locality;
- automatic port negotiation;
- mutation and undo;
- screenshots/renders;
- generic host or capability abstractions.
