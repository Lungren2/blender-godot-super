# Architecture

## Current MVP boundary

`blender-godot-super` is one MCP endpoint composed from two pinned upstream engine
servers.

```text
agent / MCP client
        |
        | stdio, or Responses API
        | via Secure MCP Tunnel
        v
+---------------------------+
| blender-godot-super       |
| FastMCP 4 parent          |
| optional audit middleware |
+-------------+-------------+
              |
       +------+------+
       |             |
       v             v
 Blender MCP      Godot MCP
 stdio proxy      in-process mount
       |             |
       v             v
 Blender add-on   Godot plug-in
       |             |
       v             v
     bpy          Editor API
```

The Blender runtime comes from `minihellboy/claude-blender`. The Godot runtime comes
from `hybridindie/godot-mcp`. Exact revisions and licenses are recorded in
`THIRD_PARTY_NOTICES.md` and pinned in `pyproject.toml`.

The parent owns composition and cross-host guidance. It does not redefine the donors'
engine semantics.

## MCP primitive ownership

Preserve the engine-native MCP surfaces unless a cross-host abstraction has demonstrated
value:

- Blender tools retain `blender_*` names and Blender resources retain `blender://` URIs.
- Godot tools retain `godot_*` names and Godot resources retain `godot://` URIs.
- Read-oriented state should remain resources where the donor already models it that way.
- Mutations retain the donor's native safety and undo behavior.
- Prompts remain reusable procedures rather than hidden alternate APIs.

Unified means one client connection and one installation path. It does not imply a shared
scene/object/node ontology.

## Child lifecycle

Godot is mounted in-process. HybridIndie's MCP keeps enabled toolsets as explicit
server-global application state, so its server must survive across calls.

Blender is proxied through its SDK-v2 stdio server with `keep_alive=True`. FastMCP
reuses that transport across ordinary proxy requests, so the child MCP process and its
process-local state survive for the parent lifetime. If the subprocess dies, the
transport may reconnect it; Blender editor state remains in Blender while child-local
state starts fresh.

## Automation transport and evidence

The default transport remains stdio. The launcher also supports loopback-only Streamable HTTP for private automation. Public/private-network traversal is kept outside the MCP process and can be provided by OpenAI Secure MCP Tunnel.

GPT-6 Astra policy is a client-edge profile, not an engine abstraction. The generated Responses API MCP definition uses `allowed_tools` to import a bounded subset and deliberately omits arbitrary Blender Python plus destructive Godot scene operations.

When auditing is enabled, parent middleware records tool calls, resource reads, and prompt renders before they cross into either mounted donor. Binary image outputs are materialized as content-addressed artifacts so a long agent trajectory can be inspected from observable actions and evidence.

## Installation boundary

The Python packages are installed directly from immutable Git revisions.

The matching editor add-ons are copied from immutable GitHub archives by
`scripts/install_integrations.py`. The installer copies the upstream subdirectories
without reimplementing them.

This keeps attribution and refreshes mechanical while avoiding a second maintained copy of
large upstream source trees.

## Shared infrastructure

Shared infrastructure should be introduced only where both real hosts need it. Likely
candidates include:

- parent-level host status and diagnostics;
- explicit host/document/project identities;
- artifact references and provenance;
- cross-host workflow prompts;
- common installation and version reporting.

A generic `HostAdapter.invoke(...)`, universal scene vocabulary, or
search/schema/invoke gateway is not part of the MVP.

## Capability breadth

The donors currently solve breadth differently:

- Godot uses FastMCP toolset gating.
- Blender exposes a moderate direct tool surface.

Keep those working mechanisms until measurements show the unified surface needs another
discovery layer. MCP protocol discovery such as `server/discover` remains distinct from
any future application capability catalog.

## Verification layers

```text
unit          composition helpers and installer/archive behavior
contract      one MCP client sees both upstream surfaces
integration   live Blender/Godot editor bridges
smoke         packaged client -> unified MCP -> live host state
persistence   mutate -> visual evidence -> save -> restart -> persisted-state read
```

The earlier repository-owned Blender observation bridge remains as a real-host integration
test while the upstream composition path settles.
