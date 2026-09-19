# blender-godot-super

One MCP endpoint for Blender and Godot.

The MVP composes two existing MIT-licensed MCP implementations instead of rebuilding their engine integrations:

- Blender: `minihellboy/claude-blender` at `5087d87212e0acf3225307c2b3512659c425cc5e`
- Godot: `hybridindie/godot-mcp` at `daf1cf649f41fc95c403e03859d0461a5b272333`

The parent server runs on FastMCP 4 / MCP 2026-07-28. Godot is mounted in-process so its bridge lifecycle and enabled toolsets persist across calls. Blender is proxied through its SDK-v2 stdio server. Tool names and resource URIs stay engine-specific.

## Install

Install the Python environment:

```bash
uv sync --dev
```

Install the pinned editor integrations. You can install either side or both:

```bash
uv run python scripts/install_integrations.py \
  --blender-addons /path/to/blender/<version>/scripts/addons \
  --godot-project /path/to/godot/project
```

The installer downloads immutable GitHub archives at the revisions above and copies only the upstream add-on directories. Use `--force` when replacing an existing installation.

In Blender, enable the `Claude Blender` add-on. Its local bridge listens on `127.0.0.1:9876` by default.

In Godot, enable `Godot MCP` under Project Settings > Plugins. The plug-in connects to the Python bridge on `127.0.0.1:9080` by default and reconnects if the MCP server starts later.

## Run one MCP server

Run the unified server over stdio:

```bash
uv run blender-godot-super
```

A client configuration can point at the repository directly:

```json
{
  "mcpServers": {
    "blender-godot-super": {
      "command": "uv",
      "args": [
        "run",
        "--project",
        "/absolute/path/to/blender-godot-super",
        "blender-godot-super"
      ]
    }
  }
}
```

Check that both upstream MCPs compose successfully:

```bash
uv run python scripts/smoke_unified.py
```

With the editors connected, the same MCP client can use resources such as:

```text
blender://scene
godot://project/info
godot://scene/current
godot://scene/tree
godot://node/selected
```

Blender tools retain their `blender_*` names. Godot keeps its `godot_*` names and starts with its normal gated toolset policy. Use `godot_list_toolsets` and `godot_enable_toolset` when broader Godot operations are needed.

## Architecture rule

Unified means one install and one MCP endpoint. It does not mean Blender objects and Godot nodes are forced into one domain model.

Resources remain engine-specific, mutations retain the native editor's undo and safety behavior, and cross-engine abstractions are added only after real workflows show equivalent semantics.

The repository's earlier narrow Blender observation bridge remains as an integration-test path while the upstream composition MVP settles.

## Attribution

See `THIRD_PARTY_NOTICES.md` and `licenses/` for upstream revisions and full MIT notices. The GPLv3 `CallMeJones/blender-agent-bridge` project is used only as a design reference; its implementation is not copied here.

## Known MVP limitation

Minihellboy's `blender://render/latest` resource stores its last capture path in the Blender MCP process. The current Blender proxy may create a fresh backend process for a later request, so that one resource is not reliable yet. Render and screenshot tools still return their visual result directly, and Blender editor state remains in Blender.
