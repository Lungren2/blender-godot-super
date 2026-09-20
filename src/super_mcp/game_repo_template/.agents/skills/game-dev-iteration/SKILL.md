---
name: game-dev-iteration
description: Use for player-facing game work such as mechanics, levels, enemies, balance, UI, assets, or feel. Controls prototype, playtest, production, and stop decisions. Do not use for pure repository maintenance with no player-facing effect.
---

# Human-paced game development

Treat game development as a sequence of design questions, playable experiments, observations, and decisions. Code and assets are means to answer those questions.

## Before changing the game

Read `GAME_DESIGN.md`.

For meaningful player-facing work, identify:

- what the player is doing;
- what the player is trying to achieve;
- what the player should feel;
- what decision, skill, or understanding the change exercises;
- what feedback tells the player what happened;
- what design question the next iteration needs to answer.

If the task changes the intended experience and the design question is not already recorded, add a concise entry under "Current hypotheses" in `GAME_DESIGN.md`.

Classify the work as one of:

- exploration: the idea has not earned permanent architecture yet;
- production: the behavior has survived enough iteration to justify durable implementation;
- maintenance: measured friction in proven production code needs removal.

Do not silently turn exploration into production.

## Work in short feedback loops

Use this loop:

1. Inspect the current playable state.
2. Checkpoint reversible editor state where useful.
3. Make one conceptual change.
4. Run the relevant scene or game.
5. Inspect semantic state through MCP when needed.
6. Inspect the visible result through computer use.
7. Record observations before choosing another fix.
8. Keep, revise, or revert.
9. Repeat only while the current design question still needs evidence.

A conceptual change may touch several files when they are inseparable, but do not batch unrelated design changes before playtesting.

Once the game can answer the current question, stop implementation and evaluate it.

## Use each tool for the job it is good at

Use shell, filesystem, and git for source code, project files, tests, and reviewable changes.

Use the Blender/Godot MCP for exact engine state and bounded editor operations.

Use computer use for what a player or artist can actually see: editor state, game feel, composition, UI, animation, feedback, and runtime behavior.

Do not claim a visual or gameplay result from code inspection alone.

For Blender assets, establish silhouette, scale, and purpose first. Import or preview them in Godot early. Judge them in the actual game camera, lighting, environment, and gameplay context before spending time on detail.

## Prefer the cheapest useful experiment

Before creating a new subsystem, check whether the problem can be solved with:

- an existing Godot feature;
- a scene, resource, signal, animation, shader, or editor setting;
- an existing project utility;
- a small local script;
- composition of existing behavior;
- an existing asset or a small edit to one.

For uncertain design, temporary duplication or local code is acceptable when it makes the question cheaper to answer.

Do not generalize from one consumer.

## Artificially impose the scarcity a human developer has

Assume every permanent line of code will have to be understood by a small team for years.

Prefer, in order:

1. no change;
2. data or editor configuration;
3. a small local change;
4. reuse and composition;
5. a small reusable abstraction;
6. a new subsystem.

Use the more complex option only when simpler options are insufficient.

Do not refactor stable code merely because it can be cleaner. Refactor when there is concrete evidence of recurring bugs, repeated modification cost, diverging duplication, design constraints, poor observability, performance problems, difficult testing, or confusing ownership.

## Spend quality where it compounds

Use the project's quality budget in `GAME_DESIGN.md`.

Core systems used constantly or depended on by many features should be dependable and boring. Typical examples are input, core movement, save/load, scene transitions, asset import, and foundational combat state.

A one-off encounter, boss gimmick, scripted moment, or local visual trick may stay local if it is understandable and contained.

Do not force different systems into a shared abstraction for symmetry.

## Observe before diagnosing

Write observations as facts about play.

Prefer:

- "The projectile is not visible before impact at the normal camera distance."
- "Three rooms in a row maintain maximum enemy density."
- "The player can win by holding one attack without changing position."

Avoid turning the first impression into a diagnosis such as "combat is bad" or "pacing is wrong."

Choose the smallest next change that can test the diagnosis.

## Pull in the relevant design skill

Use the specialized skill that matches the design question:

- `$game-design-foundations` for player purpose, communication, consistency, and the intended experience;
- `$game-difficulty` for challenge, fairness, failure, mastery, and difficulty curves;
- `$game-pacing` for intensity, recovery, novelty, progression, and sequence-level rhythm;
- `$game-storytelling` for narrative delivered through play, environment, consequence, dialogue, or exposition;
- `$game-combat` for combat options, constraints, clarity, intentions, encounters, and feel;
- `$game-visuals` for composition, lighting, color, motion, readability, feedback, and in-game asset review.

Use more than one only when the task genuinely crosses those concerns.

## Promote ideas only after evidence

When an experiment repeatedly proves useful, decide whether it deserves production treatment.

Production treatment may include reusable scenes or resources, cleaner interfaces, tests, editor tooling, stronger persistence, performance work, or documentation.

Delete failed experiments after their lesson is recorded.

Update `GAME_DESIGN.md` when a decision becomes durable. Keep implementation trivia out of that file.

## Stop condition

Stop when:

- the requested behavior works;
- the current design question has enough evidence to decide;
- the result has been observed in the playable game when player-visible;
- relevant editor state has been saved;
- persistence has been checked when it matters;
- appropriate tests pass;
- temporary clutter from the experiment has been removed.

Do not keep polishing, refactoring, abstracting, or adding adjacent features merely because more output is possible.

## Source anchor

The six design lenses used by the specialized skills follow Brackeys' Game Design playlist:
https://www.youtube.com/playlist?list=PLPV2KyIb3jR5kPzHBi90byfhPfPqaDW9s

This workflow is the repository's operational adaptation for Codex, Blender, and Godot. It is not a transcript of the playlist.
