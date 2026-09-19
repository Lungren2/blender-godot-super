# Scaffold plan

The repository starts with architecture boundaries before feature breadth.

## Phase 0 — repository scaffold

Current pass:

- establish Python package and development-tool baseline;
- separate shared MCP core from in-engine integrations;
- reserve catalog, contract, resource, prompt, evidence, transport, and host boundaries;
- add host plugin skeletons;
- document the intended model-facing surface.

No engine capability should be implemented in this phase.

## Phase 1 — protocol and contract spine

Build the smallest end-to-end vertical slice:

1. MCP server boots on the v2 SDK line.
2. Server/host status is available.
3. One canonical capability contract can be registered.
4. Catalog search can find it.
5. Schema lookup returns its contract.
6. Invocation routes through a host adapter.
7. A structured result can reference evidence/resources.

Use a fake host before Blender or Godot so protocol behavior is testable without GUI applications.

Exit condition: contract tests prove discovery → schema → invocation → result using the actual MCP server.

## Phase 2 — bridge lifecycle

Implement host connection semantics independently for Blender and Godot.

Shared requirements:

- explicit host identity and version;
- project/document identity;
- request correlation;
- cancellation and timeout;
- reconnect behavior;
- bounded message sizes;
- clear structured host errors.

Blender-specific requirement: dispatch `bpy` work safely on Blender's main thread.

Godot-specific requirement: editor mutations integrate with `EditorUndoRedoManager` where representable as editor actions.

Exit condition: a fake capability can cross each real bridge and return a typed result.

## Phase 3 — observation and evidence

Prioritize perception before broad mutation.

Implement resources/evidence for host/project summary, scene/object/node inspection, diagnostics, Blender render or viewport capture, Godot viewport capture, and runtime/engine output where available.

Exit condition: an agent can inspect a project and receive machine-readable state plus visual evidence without arbitrary code execution.

## Phase 4 — first mutation loops

Choose a tiny set of reversible capabilities per engine. Each must prove validated input, safety metadata, preview where useful, mutation, undo or explicit non-undoable status, and post-mutation evidence.

Do not expand breadth until the loop is reliable.

## Phase 5 — workflows/prompts

Encode repeated procedures above atomic capabilities: inspect scene, edit and visually verify, diagnose runtime/editor error, create a bounded asset/scene, and compare before/after evidence.

Prompts orchestrate existing capabilities; they must not become hidden alternate APIs.

## Phase 6 — capability expansion

Only now expand the catalog. Prefer canonical domain capabilities over raw engine API mirrors. Add direct specialized MCP tools only when measurements show the discovery gateway is insufficient for a frequent workflow.

## Validation layers

```text
unit          pure contract/catalog/routing behavior
contract      MCP request/response and schema guarantees
integration   real Blender/Godot bridge behavior
smoke         packaged client -> MCP -> host -> evidence loop
```

CI should cover unit and contract tests by default. GUI-host integration belongs in explicit jobs once deterministic runners exist.
