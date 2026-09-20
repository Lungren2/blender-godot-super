---
name: game-design-foundations
description: Use when deciding whether a mechanic, level, rule, interaction, or feedback change fits the intended player experience. Focuses on player purpose, communication, anticipation, consistency, and appeal.
---

# Game design foundations

## Source anchor

Playlist lesson: Brackeys, "Basic Principles of Game Design"
https://www.youtube.com/watch?v=G8AT01tuyrk

Playlist:
https://www.youtube.com/playlist?list=PLPV2KyIb3jR5kPzHBi90byfhPfPqaDW9s

The lesson is the design lens. The procedure below adapts it to this repository's iterative workflow.

## Start with the intended experience

Read `GAME_DESIGN.md`.

Do not judge a feature as good in the abstract. Judge whether it supports the intended experience, core fantasy, design pillars, and current player verbs.

Before adding a mechanic, answer:

- What role does the player have here?
- What purpose does the action serve?
- What decision or expression does the player own?
- What changes in the world because the player acted?
- Why does this belong in this game rather than merely being technically possible?

If the player has no meaningful effect, question whether the interaction needs to exist.

## Check the three design pillars

Use three lenses from the lesson.

### Player

Give the player purpose and agency. The player should drive the game forward through understandable actions and decisions.

Do not turn play into a sequence of instructions the player follows without consequence.

### Communication

The game should prepare the player for important events and respond clearly after actions.

Check:

- anticipation before important hazards, attacks, transitions, or rewards;
- immediate feedback after input or impact;
- consistent cause and effect;
- readable state changes;
- rules that behave the way the player has learned to expect.

If the game deliberately breaks a familiar rule, teach the new rule and apply it consistently.

### Appeal

The game needs a readable hierarchy of what matters. Do not make every object, effect, sound, mechanic, or message demand equal attention.

Prefer a few elements that work together over a pile of independently interesting features.

## Preserve subconscious expectations unless breaking them has value

When the player shoots, collides, picks something up, activates a control, takes damage, or reaches a goal, give enough sensory and systemic response that the result makes sense.

Physics, sound, animation, UI, and game rules do not have to be realistic. They should be internally coherent.

The game may cheat internally when the player experience stays consistent and understandable.

## Look for combinations, not feature count

Before adding another mechanic, test whether existing mechanics can interact in a new way.

A small set of understandable rules with useful combinations usually gives more design depth than many isolated mechanics.

Do not create content merely to increase the number of features.

## Test the principle in play

Make the smallest change that can answer the question.

Run the game and observe:

- whether the player knows what to do;
- whether the player understands what happened;
- whether an important event has enough anticipation;
- whether the result matches learned rules;
- whether the screen and audio make the important element clear;
- whether the mechanic creates an actual decision or only another required step.

Use computer use for visible feedback and MCP for exact engine state.

## Engine execution handoff

Use `$godot-game-development` to express purpose and communication through scene ownership, node state, signals, animation, UI, audio, tunable properties, and runtime feedback. Prefer changing an existing node or behavior before adding a new system.

Use `$blender-game-assets` when the communication problem depends on source silhouette, pose, proportion, material breakup, or source animation. Validate the result in Godot at the gameplay camera distance.

If the issue is a gameplay rule or response rather than source asset readability, keep the change in Godot.

## Record durable rules

When a principle has survived playtesting, update the relevant part of `GAME_DESIGN.md`:

- intended experience;
- design pillars;
- player verbs;
- established rules.

Do not record speculative ideas as established rules.
