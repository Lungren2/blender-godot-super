---
name: game-difficulty
description: Use when tuning challenge, failure, enemy pressure, onboarding, mastery, difficulty curves, or accessibility of challenge. Focuses on balance, fairness, transparency, depth, and learnable failure.
---

# Difficulty design

## Source anchor

Playlist lesson: Brackeys, "Difficulty in Video Games - Game Design"
https://www.youtube.com/watch?v=bxp4G-oJATM

Playlist:
https://www.youtube.com/playlist?list=PLPV2KyIb3jR5kPzHBi90byfhPfPqaDW9s

The lesson frames difficulty as a design problem. The procedure below adapts that lens to iterative development.

## Define who is being challenged

Read the "Difficulty model" and current hypotheses in `GAME_DESIGN.md`.

State which player knowledge or skill the challenge assumes. Do not tune a difficulty number without knowing what the player is expected to learn or demonstrate.

The right challenge depends on the intended audience and the point in the game's learning curve.

## Keep challenge achievable

A challenge should demand attention or mastery without making success feel arbitrary.

When difficulty feels wrong, separate these causes:

- the required skill is appropriate but the numbers are off;
- the rule or telegraph was not learned;
- the player lacks a needed tool;
- the encounter asks for too many things at once;
- randomness dominates meaningful choice;
- recovery is too weak;
- failure costs too much time;
- the challenge is simply below the player's current mastery.

Tune the smallest cause first.

## Make failure fair

A failure is useful when the player can understand why it happened and can form a different plan.

Check that:

- important threats have readable warnings;
- game rules remain consistent;
- consequences follow actions the player could perceive;
- random events do not create unavoidable failure;
- the player has a viable response to the situation;
- the next attempt can use knowledge from the previous one.

Do not call surprise or obscurity "difficulty."

## Make failure transparent

After failure, the player should be able to answer at least one of:

- What did I miss?
- What should I do earlier?
- What option did I ignore?
- What skill do I need to practice?
- What resource did I misuse?

If the answer is only "have better luck" or "already know the hidden rule," fix communication before raising challenge.

## Prefer depth over complexity

Do not add rules merely to make the game harder.

Prefer a small rule set that creates many meaningful situations through timing, positioning, combinations, resource pressure, enemy behavior, or tradeoffs.

Increase challenge by recombining learned elements before introducing new complexity.

## Tune before redesigning

Change one dimension at a time when possible:

- timing;
- speed;
- density;
- damage;
- health;
- spacing;
- resource availability;
- recovery window;
- telegraph duration;
- checkpoint cost.

Run the encounter after each meaningful tuning change.

Do not rewrite a combat or progression system when a parameter change can test the same hypothesis.

## Test several player states

At minimum, consider:

- a first-time player who follows the intended learning path;
- a competent player using the expected strategy;
- a skilled player exploiting the system;
- a player recovering from a mistake.

Use real play, not only unit tests or simulated state.

## Use adaptive difficulty only for a named problem

Dynamic difficulty adjustment can help some games, but do not use it to hide unclear rules, bad pacing, or poorly tuned encounters.

If adaptive behavior is added, define what signal changes difficulty, what bounds apply, and what player experience it protects.

## Engine execution handoff

Use `$godot-game-development` first. Expose or reuse tuning values, adjust encounter composition, timing, spacing, recovery, telegraphs, resources, and room geometry, then run the complete encounter after each meaningful change.

Use `$blender-game-assets` only when challenge readability depends on source silhouette, attack pose, animation anticipation, weapon shape, or other asset-level communication. Do not solve numerical or encounter-balance problems in Blender.

## Record the result

Update `GAME_DESIGN.md` when the project establishes a durable difficulty rule, target, or learning sequence.

For experiments, record the observation and result without turning temporary tuning values into permanent design law.
