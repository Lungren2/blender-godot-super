# Scaffold plan

The repository starts with architecture boundaries before capability breadth, but shared contracts are learned from real host behavior rather than invented against a fake implementation.

## Phase 0 — repository scaffold

Complete:

- establish Python package and development-tool baseline;
- separate shared MCP core from in-engine integrations;
- reserve resource, prompt, evidence, transport, and host boundaries;
- add host plugin skeletons;
- document the intended model-facing surface.

## Phase 1A — Blender observation slice

Build the smallest real end-to-end path first:

1. a current MCP server starts on the Python SDK v2 line;
2. it advertises a read-oriented `blender://scene` resource;
3. the server connects only to a loopback Blender bridge;
4. bridge I/O remains off the Blender API thread;
5. a Blender application timer drains queued work on the main thread;
6. the add-on inspects the active scene through `bpy`;
7. the resource returns structured scene state to the MCP client;
8. bridge-unavailable and malformed-response failures remain distinguishable.

The first resource should report only useful facts that Blender can provide directly, such as:

- Blender version;
- current blend-file/document identity;
- scene name;
- object names and types;
- active object;
- camera.

No mutation belongs in this slice.

Exit condition: with Blender running and the add-on enabled, an MCP client can read `blender://scene` and receive state originating from the actual open Blender document.

## Phase 1B — Godot observation slice

Repeat the same infrastructural exercise against the real Godot editor.

Prefer a Godot-specific resource such as `godot://scene` rather than forcing it through a shared scene schema.

Capture facts the Godot editor naturally exposes, such as:

- Godot version;
- project identity;
- edited scene path;
- root node;
- node names/types;
- editor selection.

Exit condition: an MCP client can read the resource and receive state originating from the actual editor.

## Phase 1C — compare and extract contracts

Only after both real hosts work:

- compare connection lifecycle and host identity;
- compare resource addressing and state freshness;
- compare structured error requirements;
- compare cancellation/timeout behavior;
- identify genuinely shared transport and routing contracts;
- identify concepts that must remain host-specific.

Then introduce interfaces for the common boundary.

A fake host is added here as a deterministic implementation of the learned contract for tests.

## Phase 2 — observation and evidence

Expand perception before mutation.

Add resources or artifacts for:

- scene/object/node inspection;
- diagnostics;
- Blender render or viewport capture;
- Godot viewport capture;
- runtime/engine output where available.

Do not introduce a universal evidence hierarchy until multiple real artifact types demonstrate the need. Start with small typed artifact references containing URI, media type, provenance, and role.

## Phase 3 — first reversible mutation loops

Choose a tiny set of reversible capabilities per engine.

Each capability must prove:

- validated input;
- explicit side-effect/safety metadata;
- mutation through the host's native editor model;
- undo or explicit non-undoable status;
- post-mutation observation or artifact capture.

Godot editor mutations should use `EditorUndoRedoManager` where representable. Blender mutations must preserve editor-safe main-thread execution and establish an undo strategy before breadth expands.

## Phase 4 — workflows and prompts

Encode repeated procedures above proven primitives:

- inspect scene;
- edit and visually verify;
- diagnose runtime/editor errors;
- create a bounded asset or scene;
- compare before/after artifacts.

Prompts orchestrate existing primitives. They must not become hidden alternate APIs.

## Phase 5 — capability discovery

Evaluate whether the growing operation surface warrants an application-level discovery gateway.

If measurements show that a large static MCP tool surface harms context use or selection quality, introduce catalog search, schema lookup, and generic invocation deliberately.

Keep this separate from MCP protocol discovery such as `server/discover`.

## Phase 6 — capability expansion

Only now expand breadth.

Prefer engine-native semantics unless a shared abstraction has demonstrated equivalent meaning in both hosts.

## Validation layers

```text
unit          pure serialization, routing, and helper behavior
contract      MCP-visible resources/tools and structured failure guarantees
integration   real Blender/Godot bridge behavior
smoke         packaged client -> MCP -> host -> real host state
```

CI covers unit and contract tests that can run headlessly. Real GUI-host integration belongs in explicit jobs once deterministic runners exist.
