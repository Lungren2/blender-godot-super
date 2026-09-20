# Blender integration

Production Blender support comes from the pinned MIT-licensed `minihellboy/claude-blender` implementation. Install its matching Blender add-on with:

```bash
uv run python scripts/install_integrations.py --blender-addons /path/to/blender/<version>/scripts/addons
```

The upstream revision is pinned in `pyproject.toml` and `src/super_mcp/installations.py`. Attribution is recorded in `THIRD_PARTY_NOTICES.md`.

## Repository-owned regression bridge

`integrations/blender/addon/blender_godot_super` is the earlier read-only observation bridge. It remains in the repository because CI uses it as an independent real-Blender regression path for `blender://scene`.

It is not the production add-on for the unified MVP.

For that regression path, the add-on listens on `127.0.0.1:8765`, queues requests from the socket thread, and performs all `bpy` inspection on Blender's main thread.

Manual regression smoke:

```bash
uv run python scripts/smoke_blender_resource.py
```
