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

## GPT-6 Astra and Secure MCP Tunnel

For a local automated loop, run the parent as a loopback Streamable HTTP server with the Astra runtime profile:

```bash
uv run blender-godot-super --transport http --profile astra
```

The endpoint is `http://127.0.0.1:8000/mcp` by default. HTTP mode refuses non-loopback binds. The Astra profile seeds the bounded Godot toolsets used by the development loop and writes the action/artifact audit under `.super-mcp/audit`.

To expose that private endpoint to the OpenAI Responses API, install OpenAI's current `tunnel-client`, set its runtime credential, and create a Secure MCP Tunnel profile:

```bash
export CONTROL_PLANE_API_KEY=...
uv run blender-godot-super-tunnel init --tunnel-id tunnel_...
uv run blender-godot-super-tunnel doctor
uv run blender-godot-super-tunnel run
```

The MCP server and `tunnel-client` run as separate foreground processes. The server itself never reads or stores the OpenAI control-plane credential.

Generate the bounded Responses API MCP tool object for GPT-6 Astra:

```bash
uv run blender-godot-super-astra --tunnel-id tunnel_...
```

For a full Responses configuration fragment that combines the MCP with OpenAI's native computer tool and the repository dev-loop instructions:

```bash
uv run blender-godot-super-astra --tunnel-id tunnel_... --responses-profile
```

The application running computer use must keep the desktop session alive, return a current screenshot when UI state is unknown, and return another screenshot after short action groups. The MCP remains the source for semantic Blender/Godot state; computer use verifies what is actually visible in the editors.

For an already secured remote MCP endpoint, use `--server-url https://.../mcp` instead.

The Astra `allowed_tools` profile imports inspection, reversible mutations, explicit saves, runtime/test operations, and visual verification. It intentionally excludes `blender_execute` and destructive Godot scene operations such as delete/reload/close.

## Action and artifact audit

Pass `--audit-dir PATH` to either transport to enable parent-level logging. `--profile astra` enables it by default at `.super-mcp/audit`.

The audit contains:

- `actions.jsonl`: tool calls, resource reads, prompt renders, arguments, status, duration, and normalized results;
- `artifacts.jsonl`: content-addressed artifact metadata;
- `artifacts/`: extracted image/binary outputs and large text payloads.

Known secret-shaped keys such as API keys, authorization fields, passwords, secrets, and tokens are redacted. The audit still contains project/tool data and should be treated as sensitive development evidence. The default `.super-mcp/` directory is git-ignored.

The real dual-editor CI path now exercises the wider loop: mutate Blender and Godot, capture a Blender render and an OS-level screenshot of the live Godot editor desktop, save both, terminate both editors, restart them, and verify the saved object/node through the MCP after restart. The same run asserts that the audit contains the mutation, visual, save, and post-restart observation trajectory.

Repository maintenance is a separate bounded pass after the requested behavior works. Run `uv run python scripts/check_repo_hygiene.py --include-untracked` during an agent loop. CI runs the tracked-files version. The check rejects generated caches/editor artifacts, unexpected top-level files, and Python code placed outside the established source/script/test/integration directories.

## Architecture rule

Unified means one install and one MCP endpoint. It does not mean Blender objects and Godot nodes are forced into one domain model.

Resources remain engine-specific, mutations retain the native editor's undo and safety behavior, and cross-engine abstractions are added only after real workflows show equivalent semantics.

The repository's earlier narrow Blender observation bridge remains as an integration-test path while the upstream composition MVP settles.

## Attribution

See `THIRD_PARTY_NOTICES.md` and `licenses/` for upstream revisions and full MIT notices. The GPLv3 `CallMeJones/blender-agent-bridge` project is used only as a design reference; its implementation is not copied here.

## Process lifetime

The Blender stdio transport is explicitly kept alive for the lifetime of the parent process. That preserves Minihellboy's MCP-process state, including `blender://render/latest`, across ordinary calls through the unified server. If the child process exits, FastMCP reconnects it and process-local state starts fresh.
