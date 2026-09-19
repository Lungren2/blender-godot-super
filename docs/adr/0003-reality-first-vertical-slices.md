# ADR 0003: Learn shared contracts from real hosts

Status: accepted

## Context

The initial scaffold proposed proving a full capability round-trip against a fake host before connecting Blender or Godot.

That would verify internal consistency, but it would not verify the assumptions most likely to shape the architecture:

- Blender main-thread execution constraints;
- Godot editor lifecycle and undo semantics;
- host process availability and disconnect behavior;
- project/document identity;
- resource addressing;
- transport cancellation and timeout behavior;
- the real shape of observable state.

A fake host can satisfy an abstraction because both sides are under our control. It cannot tell us whether the abstraction matches the applications we are integrating.

The initial proposal also risked duplicating semantics between read-only capabilities and MCP resources, and it risked inventing an application-level RPC protocol before the need for one had been demonstrated.

## Decision

Build the first vertical slices against real hosts before formalizing a broad shared capability model.

The order is:

1. expose one read-oriented Blender resource through the real add-on bridge;
2. expose the equivalent useful observation through the real Godot editor bridge;
3. compare the two implementations;
4. extract only the shared contracts demonstrated by both;
5. add a fake host as the deterministic test implementation of those learned contracts.

Shared infrastructure is still a goal. Shared domain ontology is not assumed.

Blender- and Godot-specific resource or capability names are preferred until semantics are proven equivalent.

## First slice

The first slice is:

```text
MCP client
    -> MCP 2026-07-28 server
    -> blender://scene
    -> localhost Blender bridge
    -> Blender main-thread dispatcher
    -> bpy scene inspection
    -> structured resource content
    -> MCP client
```

The bridge binds to loopback only. Its I/O thread must not access `bpy`. Blender API work is queued and executed by an application timer on Blender's main thread.

The initial resource is observation-only. No mutation, arbitrary Python execution, generic capability gateway, evidence hierarchy, or cross-engine scene abstraction is introduced.

## Consequences

- Transport and lifecycle problems appear before we generalize them away.
- The first shared abstraction may be smaller than originally planned.
- Some code will initially remain Blender-specific.
- A fake host arrives later, when it can test a contract learned from real behavior rather than define that contract.
- The discovery-first tool gateway remains a candidate architecture, not yet a foundational requirement.
