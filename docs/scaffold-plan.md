# MVP and follow-on plan

The project now favors upstream composition over rebuilding mature Blender and Godot MCP
implementations.

## MVP composition

Current implementation:

1. pin `minihellboy/claude-blender` and `hybridindie/godot-mcp` to immutable Git
   revisions;
2. mount HybridIndie's FastMCP Godot server in-process;
3. proxy Minihellboy's SDK-v2 Blender server over stdio;
4. expose both engine-native tool/resource surfaces through one FastMCP parent;
5. install the matching editor add-ons from the same pinned revisions;
6. preserve full MIT notices and revision provenance;
7. retain the repository-owned Blender observation slice as an independent real-host
   regression test.

Exit condition: one MCP client can list both engine families through
`blender-godot-super`, and the corresponding editor add-ons can connect to their real
hosts.

## MVP verification

The composition contract must prove at least:

- `blender_ping` is visible;
- `godot_get_server_info` is visible;
- `blender://scene` is visible;
- `godot://project/info` is visible;
- mounted child names are not accidentally prefixed or rewritten;
- the pinned add-on installer extracts only the requested upstream subtree.

Live host verification remains engine-specific.

## Next: real dual-host smoke

Run Blender and Godot against the same parent MCP and prove:

- Blender scene observation comes from the open blend file;
- Godot project/scene observation comes from the open editor;
- one client can alternate between both without restarting the parent;
- Godot toolset enabling persists across calls;
- host disconnects remain attributable to the correct engine.

Do not introduce shared scene semantics during this step.

## Then: harden the composition seam

After the dual-host smoke:

- replace the short-lived Blender proxy if process-local state becomes material;
- add parent-level host/version diagnostics;
- lock dependency resolution for reproducible installs;
- add explicit upstream refresh tooling and provenance checks;
- validate install behavior on supported operating systems.

## Then: workflows and evidence

Reuse donor capabilities to prove real workflows before inventing new abstractions:

- Blender inspect -> mutate -> render/screenshot -> evaluate;
- Godot inspect -> mutate -> undo/redo -> viewport/runtime verification;
- cross-host workflows only where a user task genuinely spans both applications.

Artifact/evidence contracts should be extracted from those real outputs.

## Later: capability-surface scaling

Only introduce another application-level discovery gateway if measurements show the
combined tool surface harms context use or tool selection.

Godot already has gated toolsets. Blender currently has a moderate direct surface. Keep
those mechanisms until there is evidence they are insufficient.

## Non-goals for the MVP

- universal Blender/Godot scene ontology;
- generic HostAdapter dispatcher;
- copied GPLv3 Blender Agent Bridge implementation;
- arbitrary cross-engine capability translation;
- replacing donor undo/safety models with a new shared model.
