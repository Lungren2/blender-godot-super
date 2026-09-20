<!-- blender-godot-super:game-development:start -->
## Game development method

For player-facing game work, read `GAME_DESIGN.md` before implementation.

Use `$game-dev-iteration` for mechanics, levels, enemies, balance, UI, assets, feel, or other changes to the player experience. Pull in the matching specialist skill when needed:

- `$game-design-foundations` for player purpose, communication, anticipation, consistency, and intended experience;
- `$game-difficulty` for challenge, fairness, failure, learning, and mastery;
- `$game-pacing` for intensity, recovery, progression, repetition, and encounter order;
- `$game-storytelling` for narrative, environment, dialogue, worldbuilding, and story through play;
- `$game-combat` for combat options, constraints, clarity, enemies, encounters, and feel;
- `$game-visuals` for composition, lighting, color, animation, VFX, UI readability, and asset review.

Treat uncertain design as an experiment. State the player-facing question, make the smallest playable change that can answer it, run the game, observe the result, then keep, revise, or revert. Avoid batching unrelated conceptual changes before playtesting.

Use shell and git for code and repository work. Use Blender/Godot MCP for exact engine state and bounded editor operations. Use computer use for visible editor and game state. Do not claim a visual or gameplay result from code inspection alone.

Prefer existing engine features, project utilities, data, editor configuration, scenes, resources, signals, shaders, and composition before creating new infrastructure. Do not generalize from one consumer. Do not refactor stable code without measured friction.

Exploration may use local, temporary, or duplicated code when that makes a design question cheaper to answer. Promote an idea to reusable production architecture only after playtesting shows that it belongs.

For Blender assets, establish silhouette, scale, and purpose first. Import or preview them in Godot early and judge them in the actual game camera, lighting, and gameplay context before spending time on detail.

Record observations before diagnoses. Update `GAME_DESIGN.md` when a decision becomes durable, when a failed experiment teaches something reusable, or when a new open design question appears. Keep implementation inventories and routine task tracking out of that file.

Stop when the requested behavior works, has been observed in the playable game when player-visible, has been saved and persistence-checked when relevant, and appropriate tests pass. Do not continue polishing or restructuring merely because more output is possible.
<!-- blender-godot-super:game-development:end -->
