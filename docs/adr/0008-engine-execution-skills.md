# ADR 0008: Engine execution skills under the design method

Status: accepted

## Context

ADR 0007 gives Codex a human-paced design method and six design lenses. Those skills explain what to evaluate, but a model can still choose poor implementation paths when translating a design decision into Godot or Blender work.

For example, "make the attack easier to read" could become a new combat framework instead of a short telegraph edit, and "improve the prop" could become a detailed Blender model before its silhouette has been tested in the game.

The game methodology needs a separate execution layer that teaches tool ownership and common engine patterns without turning the design skills into large engine manuals.

## Decision

Add two repository skills beneath the design layer:

- `godot-game-development` translates a proven design question into Godot scenes, scripts, data, signals, animation, runtime checks, UI, shaders, and project structure;
- `blender-game-assets` translates an asset requirement into Blender blockout, modeling, materials, modifiers, rigging, animation, collision/import intent, and repeated Godot validation.

The design skills retain responsibility for the player-facing problem. Their engine handoff sections tell Codex which execution skill owns the next step.

The Godot skill prefers normal engine composition before custom infrastructure. It treats scenes as reusable composition units, keeps behavior near the node that owns it, uses signals at loose ownership boundaries, uses Resources or other data representations only when values genuinely need reuse or independent authoring, and requires runtime observation for player-visible changes.

The Blender skill starts from the Godot use site and gameplay camera. It blockouts before detailing, keeps modifiers non-destructive while requirements are uncertain, separates source geometry from gameplay ownership, and validates one representative asset in Godot before producing a family of assets.

The Blender-to-Godot pipeline supports two deliberate choices:

- direct `.blend` import for fast local iteration when the development environment can require Blender;
- glTF or GLB for portable or controlled import artifacts.

Imported source visuals should usually be wrapped by a hand-authored Godot scene when game-specific scripts, effects, collision, navigation, or state must survive source reimport.

The current bounded MCP profile remains the execution boundary. The skills must not imply capabilities the profile does not expose. Use shell/file editing for source files, MCP for supported semantic/editor operations, and computer use for specialized Blender or Godot editor interactions not represented in the bounded MCP.

## Design-to-engine handoff

Each specialist design skill receives a short engine execution section.

Examples:

- difficulty hands off tuning and encounter composition to Godot and uses Blender only when threat readability depends on source pose, silhouette, or animation;
- pacing hands off encounter ordering and timing to Godot and uses Blender only when spatial landmarks or environment density are part of the diagnosis;
- combat hands runtime hit logic, state, and collision ownership to Godot while Blender owns source attack poses, rigs, weapons, and source animation;
- visuals route source geometry and source animation to Blender, then route camera, lighting, engine shaders, UI, effects, and final acceptance to Godot.

## Consequences

Codex receives concrete engine recipes without loading both engine manuals for every design question. Project skills can select a design lens, then load only the execution skill needed for the chosen implementation.

The skills reinforce a stable ownership boundary between source assets and runtime gameplay.

The execution guidance can evolve independently from the Brackeys-derived design lenses because its source record comes from Godot and Blender primary documentation plus the pinned MCP behavior.

## Source record

See `docs/research/godot-blender-execution.md`.
