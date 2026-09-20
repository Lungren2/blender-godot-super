---
name: game-pacing
description: Use when shaping intensity, recovery, progression, encounter order, reward cadence, novelty, repetition, or the rhythm of a level or full gameplay loop.
---

# Pacing design

## Source anchor

Playlist lesson: Brackeys, "Keeping players Interested - Pacing in Game Design"
https://www.youtube.com/watch?v=ftiHgyFt72M

Playlist:
https://www.youtube.com/playlist?list=PLPV2KyIb3jR5kPzHBi90byfhPfPqaDW9s

The lesson treats pacing as a way to hold player interest. The procedure below adapts that lens to iterative development.

## Inspect the sequence before adding content

Read the current gameplay loop and "Pacing model" in `GAME_DESIGN.md`.

When a section drags or overwhelms, first inspect the order, duration, and contrast of existing content.

Do not assume the fix is another enemy, room, reward, cutscene, or mechanic.

## Think in intensity over time

Map the representative play sequence in plain terms.

Mark stretches such as:

- learning;
- anticipation;
- pressure;
- peak challenge;
- reward;
- exploration;
- recovery;
- surprise;
- repetition.

The exact labels can vary. The point is to see whether the experience stays at one intensity for too long.

Constant pressure becomes tiring. Constant calm becomes flat.

## Use contrast deliberately

Look for useful contrast between:

- pressure and recovery;
- complexity and simplicity;
- confined and open space;
- novelty and familiarity;
- action and reflection;
- scarcity and reward;
- fast decisions and slower planning.

A recovery beat should still serve the game. It may let the player explore, prepare, practice, absorb story, make a build choice, or enjoy a reward.

## Respect learning pace

Introduce enough novelty to keep attention, but give the player time to understand and reuse what was learned.

Before introducing another mechanic or enemy pattern, ask whether the current one has had a chance to become legible and useful.

Prefer:

teach -> safe use -> pressured use -> combination -> variation

over introducing several unrelated rules in a short span.

## Check reward cadence

Rewards can be mechanical, informational, visual, narrative, spatial, or expressive.

Do not use rewards only as a timer that fires every few minutes. Make them land after effort, discovery, mastery, or a meaningful transition when possible.

Check whether the player gets enough evidence of progress without flattening every moment into constant stimulation.

## Rearrange before rebuilding

For pacing problems, cheap experiments include:

- remove an encounter;
- move a reward;
- shorten traversal;
- insert a safe room;
- delay a new mechanic;
- combine two weak beats;
- separate two peaks;
- change spawn timing;
- change the order of rooms;
- reduce repeated exposition.

Try sequence changes before building a new system.

## Play the whole relevant span

Pacing cannot be judged from one isolated encounter.

Run the complete level, room sequence, onboarding stretch, or gameplay loop that contains the issue.

Use computer use to observe actual waiting, repetition, visual density, and transition time.

Record observations before changing the sequence again.

## Periodically replay the full supported loop

Local improvements can damage the larger rhythm.

At meaningful milestones, play through the full current loop and check:

- whether onboarding reaches interesting play quickly;
- whether intensity has useful variation;
- whether repeated content still earns its time;
- whether rewards arrive after meaningful effort;
- whether new systems crowd out older ones;
- whether the ending of a session creates a useful sense of completion or curiosity.

## Engine execution handoff

Use `$godot-game-development` for encounter order, spawn timing, transitions, checkpoint or reward placement, mechanic activation, dialogue timing, and running the complete relevant sequence.

Use `$blender-game-assets` only when the pacing diagnosis depends on source environment density, navigation landmarks, room-kit proportions, or visual transitions between spaces. Test a small assembled environment in Godot before building more assets.

## Record pacing decisions

Update the "Pacing model" in `GAME_DESIGN.md` when a sequence or rhythm becomes intentional and durable.

Record failed pacing experiments under "Rejected experiments and lessons" when they teach something reusable.
