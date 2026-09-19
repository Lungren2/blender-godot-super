# ADR 0004: Compose pinned upstream MCP implementations

Status: accepted

## Context

The first Blender observation slice proved the real host boundary, but building a broad
Blender and Godot operation set from scratch would duplicate mature open-source work.

Two MIT projects already provide current-protocol implementations with useful engine
behavior:

- `minihellboy/claude-blender` for Blender;
- `hybridindie/godot-mcp` for Godot.

The goal of this repository is now to provide one MCP endpoint while preserving
engine-native semantics and upstream provenance.

## Decision

Build the MVP as a composition server rather than a reimplementation.

Pin upstream source revisions in `pyproject.toml`. The unified server uses FastMCP 4:

1. build HybridIndie's Godot FastMCP server in-process and mount it directly;
2. proxy Minihellboy's SDK-v2 Blender MCP over stdio and mount the proxy;
3. preserve the upstream tool names, resource URIs, prompts, and structured results;
4. do not introduce a shared Blender/Godot scene ontology;
5. keep the repository's narrow Blender observation server as a separate integration
   test target until the upstream Blender path fully replaces it.

The Godot server must stay in-process for the MVP. Its enabled toolsets are explicit
server-global application state under MCP 2026-07-28. Restarting the child server for
every request would reset that state.

The Blender proxy uses FastMCP's stdio transport with `keep_alive=True`. FastMCP 4.0.1
clones proxy clients while reusing the transport, so the upstream Blender MCP process
stays alive across ordinary calls for the lifetime of the parent. This preserves
process-local upstream state such as `blender://render/latest`. If the child exits,
the transport can reconnect it and that process-local state starts fresh.

## Provenance

The two runtime donors are MIT licensed. Preserve their full license texts and pinned
revision metadata in this repository. Install the matching editor add-ons by copying their
source directories from immutable GitHub archives at the same revisions, rather than
maintaining hand-rewritten local forks.

`CallMeJones/blender-agent-bridge` remains a design reference only because its
implementation is GPLv3 and this repository is MIT.

## Consequences

- The MVP gets the donors' existing tools, resources, prompts, safety behavior, and host
  bridges immediately.
- Upstream updates are deliberate revision bumps rather than silent drift.
- The parent server owns composition and future cross-host status/workflow features.
- Engine-specific behavior remains owned by the engine integration that already
  implements it.
- Cross-host abstractions still require evidence from real Blender and Godot workflows.
