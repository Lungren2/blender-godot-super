# ADR 0007: Human-paced game development methodology

Status: accepted

## Context

The unified MCP gives Codex and GPT-6 Astra strong execution capabilities across source code, Blender, Godot, and visible desktop state.

Capability alone does not produce a good long-term indie workflow. A model can keep generating code, abstractions, assets, and polish without the fatigue or maintenance pressure that naturally pushes a human developer to stop, play the game, delete weak ideas, or leave stable code alone.

The target workflow needs to make design evidence and iteration cadence explicit.

Brackeys' Game Design playlist provides six useful design lenses:

1. basic design principles;
2. difficulty;
3. pacing;
4. storytelling;
5. combat;
6. visual presentation.

Codex repository skills are a good place for these workflows because Codex discovers versioned project skills under `.agents/skills` and loads their full instructions only when a task matches the skill description.

## Decision

The consumer-repo bootstrap installs seven game-development skills.

Six specialist skills match the playlist topics:

- `game-design-foundations`;
- `game-difficulty`;
- `game-pacing`;
- `game-storytelling`;
- `game-combat`;
- `game-visuals`.

A seventh skill, `game-dev-iteration`, owns the cross-cutting development loop:

1. read the current design record;
2. identify the player-facing question;
3. distinguish exploration, production, and maintenance;
4. inspect the current playable state;
5. make the smallest useful conceptual change;
6. run and observe the game;
7. record observations before diagnoses;
8. keep, revise, or revert;
9. promote ideas to durable architecture only after evidence;
10. stop when the requested behavior and design question are verified.

The orchestration skill also imposes artificial scarcity. It tells the agent to prefer existing engine features, data, local changes, and composition before new infrastructure, and to avoid refactoring stable code without measured friction.

The bootstrap appends a managed game-development block to the target repository's `AGENTS.md`. The block tells the agent when to use the game-development skills and how to divide work between shell/git, MCP, and computer use.

The bootstrap creates `GAME_DESIGN.md` only when it does not already exist. That document records durable design intent and evidence:

- core fantasy;
- intended experience;
- design pillars;
- player verbs;
- current gameplay loop;
- established rules;
- quality budget;
- difficulty, pacing, narrative, combat, and visual models;
- current hypotheses;
- playtest observations;
- decisions that earned permanence;
- rejected experiments and lessons;
- open design questions.

`GAME_DESIGN.md` becomes project-owned after creation. The bootstrap never overwrites it, including when `--force` is used.

Skill files and the managed `AGENTS.md` block remain bootstrap-owned methodology. A normal rerun preserves local edits. `--force` refreshes those managed files and the managed AGENTS block.

The methodology uses three evidence channels:

- shell, filesystem, tests, and git for source and repository state;
- Blender/Godot MCP for exact semantic engine state and bounded editor operations;
- computer use for visible editor state and actual gameplay presentation.

Player-visible results must be observed in the running game when practical. Code completion alone is not proof of design quality.

## Source boundary

The Brackeys playlist and its linked source material provide the design topics and several underlying principles. The repository-specific iteration cadence, maintenance constraints, tool routing, quality budget, promotion rules, and stop condition are an operational adaptation for model-driven indie development.

The skills must not present adapted workflow rules as quotations or transcripts from the videos.

The source record is preserved in `docs/research/brackeys-game-design-playlist.md`.

## Consequences

New game repositories receive design behavior along with engine capability.

A model is expected to alternate between implementer, player, and evaluator roles instead of staying in continuous implementation mode.

The design record gives later sessions durable context without turning a game design document into a code inventory.

The separation between project-owned design history and refreshable methodology allows the bootstrap to improve without erasing what the team learned about the game.

The methodology adds files to consumer repositories, but uses Codex's progressive skill loading so only relevant specialist instructions need to enter context for a given task.

## Verification

Unit tests cover installation, idempotence, preservation of customized skills, managed AGENTS refresh, and the rule that `GAME_DESIGN.md` is never overwritten.

CI builds the wheel and asserts that every Markdown template needed by the `uvx` installer is present in the packaged artifact.
