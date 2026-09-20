---
name: godot-game-development
description: Use when translating a game-design decision into concrete Godot scenes, scripts, resources, signals, animation, runtime checks, UI, shaders, physics, navigation, or project structure. Use after the design question is clear. Do not use it to invent game direction.
---

# Execute game design in Godot

Use this skill after `$game-dev-iteration` or a specialist design skill has identified the player-facing question.

The goal is to implement the smallest Godot change that can answer that question, then run the game and observe it.

## Tool boundary in this repository

Use the current bounded MCP surface deliberately.

Use Godot MCP for live editor state and bounded scene operations:

- inspect project, active scene, scene tree, selection, node properties, and groups;
- open scenes;
- create and rename nodes;
- set node properties;
- attach scripts;
- connect signals;
- add nodes to groups;
- select nodes;
- save scenes;
- run and capture the game;
- run tests.

Use shell and repository editing for source files such as GDScript, shaders, JSON, configuration, tests, and data files that are meant to be version controlled.

Use computer use for editor workflows or visible runtime behavior that the bounded MCP does not expose directly.

Do not edit `.tscn` text by hand merely because it is possible when the same structural change can be made through the live editor MCP. Scene files contain engine-owned structure and are easier to damage with blind text editing.

The current unattended profile intentionally does not expose every donor toolset. If a task clearly needs a missing Godot capability, first see whether source editing, existing scene-edit tools, or computer use can solve it. Widen the MCP profile only when a repeated workflow proves the missing toolset is worth importing.

## Start by inspecting the existing project pattern

Before adding a node, script, Resource, singleton, or subsystem:

1. inspect the active scene and relevant parent scene;
2. inspect existing neighboring nodes and scripts;
3. search the repository for an existing convention that solves a similar problem;
4. identify whether the change belongs to one instance, one reusable scene, shared data, or truly global state;
5. preserve the existing convention unless it is causing measured friction.

Do not create a new architectural pattern because another pattern looks cleaner in isolation.

## Choose the smallest Godot representation

Use ordinary Godot composition before custom infrastructure.

Prefer these options in roughly this order when they fit:

1. an exported property or existing node property;
2. a child node configured in the scene;
3. a small script on the node that owns the behavior;
4. a signal between objects that should not own each other;
5. a reusable scene for a repeated entity or behavior bundle;
6. a Resource for shared or reusable data;
7. a project-wide singleton only when state or service ownership is genuinely global.

A new manager, service layer, event bus, or framework must solve a repeated ownership problem. One feature is not enough evidence.

## Scenes are composition units

Use scenes for things that have identity, lifecycle, or repeated composition such as:

- player characters;
- enemies;
- projectiles;
- pickups;
- rooms;
- interactables;
- reusable UI panels;
- effects that own multiple nodes.

Keep scene roots meaningful. Let child nodes represent engine concerns such as collision, visuals, audio, animation, detection, or UI.

When the same entity appears more than once, prefer instancing a reusable scene over copying a large node subtree by hand.

Do not split tiny behavior into separate scenes merely to increase reuse that has not appeared yet.

## Put behavior near the node that owns it

A player movement script belongs with the player. A door interaction script belongs with the door. A room-specific scripted event may belong with that room.

Move behavior outward only when ownership is clearly shared.

Prefer direct references within one stable scene when the relationship is structural and obvious.

Prefer signals when the sender should announce an event without owning the receiver. Godot's signal model is useful when objects may move within the scene tree or be instantiated dynamically.

Avoid a project-wide event bus for local relationships.

## Use Resources for game data that needs identity and reuse

Use a Resource or data file when values need to be shared, authored independently, swapped between instances, or tuned without duplicating script logic.

Typical candidates include:

- weapon definitions;
- enemy archetype values;
- item definitions;
- encounter configuration;
- movement tuning profiles;
- damage or status-effect definitions;
- upgrade data.

Do not turn every exported property into a Resource. Local values should remain local.

Separate behavior from tuning when designers need to compare or reuse configurations.

## Expose tuning before rewriting behavior

For iteration-sensitive mechanics, make the important values easy to change without restructuring code.

Examples:

- movement acceleration and deceleration;
- dodge duration and recovery;
- telegraph duration;
- attack cooldown;
- projectile speed;
- spawn interval;
- encounter density;
- camera smoothing;
- hit-stop duration;
- UI feedback timing.

Change one important tuning dimension at a time when testing a design hypothesis.

Do not hide tuning constants across many scripts if they are repeatedly adjusted together.

## Use signals for outcomes and loose coupling

Good signal candidates describe events that have already happened or meaningful state transitions:

- `health_changed`;
- `died`;
- `attack_started`;
- `attack_finished`;
- `pickup_collected`;
- `objective_completed`;
- `room_cleared`.

Use MCP to connect signals when the connection belongs in the scene. Use code connections when instances are created dynamically or the relationship itself is dynamic.

Do not use signals as a substitute for ordinary function calls inside one tightly owned object.

## Use animation to communicate state, not only decorate it

Use `AnimationPlayer` for authored property animation, event timing, audio tracks, and simple state transitions.

Use `AnimationTree` when the game needs blended or state-driven animation playback across a set of animations. Keep the imported animation source in `AnimationPlayer` and use `AnimationTree` to control transitions and blending.

For combat and interaction, use animation timing to support:

- anticipation;
- active frames;
- recovery;
- hit confirmation;
- movement state;
- readiness;
- state changes.

Keep gameplay-critical timing observable in code or data. Do not bury every game rule inside animation tracks if it makes behavior hard to test or reason about.

When the bounded MCP cannot author the required animation graph safely, use computer use in the Godot animation editor or edit a clear source representation when one exists. Verify the result in runtime afterwards.

## Build combat with readable ownership

A practical small-game combat entity often separates concerns through child nodes rather than a large combat framework.

Depending on 2D or 3D, useful pieces may include:

- `CharacterBody2D` or `CharacterBody3D` for controlled movement;
- `Area2D` or `Area3D` for hit and detection regions;
- `CollisionShape2D` or `CollisionShape3D` for collision geometry;
- `AnimationPlayer` and optionally `AnimationTree` for readable state timing;
- audio and visual-effect children for feedback;
- a script on the owning entity for the local state machine.

Use groups for broad categories only when many unrelated systems genuinely need that category.

Do not solve one attack with a universal combat framework.

## Implement anticipation as a concrete sequence

When a design skill says an attack needs more anticipation:

1. inspect the enemy scene and current attack state;
2. identify the visible telegraph node, animation, material, sprite, mesh, audio cue, or pose;
3. expose the anticipation duration as one tunable value if it is not already easy to tune;
4. move damage activation after the telegraph;
5. make the telegraph visible at the normal gameplay camera distance;
6. run the actual encounter;
7. observe whether the player can read the threat before impact;
8. tune duration or presentation before adding another warning channel.

Do not start by rewriting the enemy AI.

## Implement difficulty as data and encounter composition first

When difficulty needs adjustment, first inspect:

- enemy count;
- timing;
- spacing;
- movement speed;
- recovery windows;
- telegraph duration;
- resource availability;
- room geometry;
- checkpoint cost;
- dominant player strategy.

Prefer changing existing data or scene composition before adding adaptive systems.

Run the complete encounter after each meaningful change.

## Implement pacing through sequence edits first

When pacing is wrong, manipulate existing content before creating more content.

Practical Godot changes may include:

- reorder instantiated room scenes;
- move a reward or checkpoint;
- change spawn timing;
- shorten a transition;
- delay activation of a mechanic;
- remove an encounter;
- add a small recovery area;
- move dialogue or UI interruption away from a pressure peak.

Run the full relevant sequence, not only the modified room.

## Implement story in the playable scene

Before adding dialogue or lore, ask whether the required information can be conveyed through:

- scene state;
- prop placement;
- NPC behavior;
- a changed environment;
- an objective consequence;
- animation;
- audio;
- optional interaction.

Use script or data files for dialogue and narrative state when that keeps authored content reviewable.

Keep mandatory gameplay information out of optional lore channels.

## Implement visual feedback with the cheapest Godot layer that works

Choose the layer that owns the feedback:

- node transform or visibility;
- `AnimationPlayer`;
- material or shader parameter;
- particles;
- audio;
- UI;
- camera response;
- short-lived effect scene.

Do not add all feedback channels at once. Establish clarity first, then style.

For shaders, edit the shader source through the repository when practical, then inspect the material in the running game. For complex visual-editor-only setup, use computer use and verify afterwards.

## Treat imported 3D content as source assets plus game wrappers

Godot's 3D importer creates engine scenes from Blender or glTF source files. Avoid treating the imported scene as the final gameplay scene when the game needs scripts, hitboxes, navigation, extra effects, or gameplay-specific children.

A common pattern is:

1. keep the Blender or glTF file as the imported visual source;
2. create a Godot scene that instances that imported scene;
3. put gameplay nodes, scripts, collision overrides, AnimationTree, effects, and state around it;
4. reimport the source asset without destroying the gameplay wrapper.

Prefer changing source geometry in Blender rather than accumulating import overrides for problems that belong to the model.

## Validate every player-facing change in runtime

After a meaningful change:

1. save the relevant scenes;
2. use `godot_runtime_run_and_capture` when it covers the scenario;
3. use computer use when interaction, timing, animation, or camera presentation matters;
4. inspect runtime errors or test failures;
5. inspect exact node state through MCP if the visible result is ambiguous;
6. adjust one thing and rerun.

A scene that saves successfully is not proof that the mechanic works.

## Avoid common model-generated Godot mistakes

Do not:

- create an autoload for local state;
- create a global event bus for one or two scene relationships;
- add a generic state-machine framework before repeated state logic exists;
- duplicate tuning constants across scripts when they are actively tuned together;
- manually rewrite large `.tscn` structures when live editor tools can make the change;
- keep adding nodes after the current hypothesis is already testable;
- infer game feel from script correctness;
- redesign neighboring systems during a local mechanic iteration.

## Finish with a Godot-specific check

Before stopping, confirm the parts relevant to the task:

- the intended scene owns the behavior;
- reusable content is actually reused;
- signals connect at the right ownership boundary;
- important tuning values are easy to adjust;
- player-visible state was observed in runtime;
- scenes are saved;
- scripts parse and tests pass where applicable;
- no new global system was introduced without repeated need;
- `GAME_DESIGN.md` records any durable design decision or reusable lesson.

## Primary references

Godot scenes and nodes:
https://docs.godotengine.org/en/stable/getting_started/step_by_step/

Signals and dynamic instancing:
https://docs.godotengine.org/en/stable/tutorials/scripting/instancing_with_signals.html

Animation and AnimationTree:
https://docs.godotengine.org/en/stable/tutorials/animation/
https://docs.godotengine.org/en/stable/tutorials/animation/animation_tree.html

3D import pipeline:
https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/

Pinned MCP donor:
https://github.com/hybridindie/godot-mcp
