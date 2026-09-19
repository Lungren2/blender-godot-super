# blender-godot-super

A shared MCP foundation for agent-driven Blender and Godot workflows.

This repository is intentionally scaffold-first. Engine integrations are adapters around a shared contract, discovery, resource, prompt, and evidence model rather than separate collections of ad-hoc tools.

## Design goals

- Target the MCP 2026-07-28 protocol generation through the Python SDK v2 line.
- Keep the model-facing surface small and discoverable.
- Treat read-only state as resources where possible.
- Treat repeatable agent procedures as prompts/workflows rather than tool descriptions.
- Give mutations explicit safety, preview, undo, and evidence semantics.
- Keep Blender and Godot host code thin. Shared behavior belongs in the MCP core.
- Make verification part of every meaningful mutation path.

## Repository shape

```text
src/super_mcp/                  shared MCP server and domain model
integrations/blender/           Blender add-on and host bridge
integrations/godot/             Godot editor plugin and host bridge
docs/                           architecture, decisions, protocol notes
tests/                          unit, contract, and integration suites
scripts/                        developer and verification entry points
```

See `docs/scaffold-plan.md` for the implementation sequence and `docs/architecture.md` for intended boundaries.

## Status

Scaffold only. No engine mutation tools are implemented yet.
