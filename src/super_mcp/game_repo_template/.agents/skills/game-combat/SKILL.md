---
name: game-combat
description: Use when designing or tuning combat mechanics, enemies, encounters, weapons, movement under pressure, telegraphs, combat feedback, or tactical choice.
---

# Combat design

## Source anchor

Playlist lesson: Brackeys, "What makes Combat Fun?"
https://www.youtube.com/watch?v=DjsFUOffakc

The video points to Mike Birkhead's "What Makes Combat Fun" as its full article:
https://www.gamedeveloper.com/design/opinion-what-makes-combat-fun

Playlist:
https://www.youtube.com/playlist?list=PLPV2KyIb3jR5kPzHBi90byfhPfPqaDW9s

The source model is options, situational constraints, and clarity. The procedure below adapts it to this project's combat loop.

## Name the player's combat intentions

Read the "Combat model" in `GAME_DESIGN.md`.

List the meaningful ways the player can try to achieve the combat goal.

An intention is more useful than a button name. Examples might include:

- poke and retreat;
- isolate one target;
- control a crowd;
- flank;
- interrupt;
- bait an attack;
- spend a scarce resource for safety;
- hold space;
- escape.

If the only viable intention is "repeat the strongest attack," the combat lacks useful choice.

## Check action sequences, not move count

A large move list does not guarantee depth.

Ask whether different intentions produce different sequences of movement, timing, target choice, resource use, positioning, and attacks.

A useful intention should change how the player behaves over several moments, not only which button is pressed once.

## Provide options, then constrain them

Combat becomes interesting when several options are valid but the situation changes which one is attractive.

Use constraints from:

- goals;
- environment;
- opponents;
- time;
- resources;
- positioning;
- visibility;
- ally or objective protection.

Constraints should force adaptation without collapsing the fight into one mandatory answer.

## Preserve clarity

The player must be able to perceive the essence of an option or threat before mastering its purpose.

Check:

- enemy silhouettes and poses;
- attack anticipation;
- hit and miss feedback;
- range and collision readability;
- state changes;
- sound cues;
- recovery windows;
- environmental affordances;
- resource state.

Do not remove discovery by explaining every optimal use. Give enough clarity that the player can experiment and learn.

## Use opponents and spaces to change decisions

Do not make enemy variety a list of health and damage values.

Ask what each opponent changes about the player's intentions.

Do not make arena variety purely decorative. Ask how cover, hazards, chokepoints, open space, elevation, routes, or objectives change combat decisions.

A new enemy or room has earned its place when it creates a different decision pattern.

## Tune feel and decision quality together

Movement response, animation timing, hit stop, recoil, camera response, sound, particles, and enemy reaction can make an action legible and satisfying.

Do not use audiovisual polish to hide a combat loop with no meaningful decisions.

Likewise, do not keep a tactically sound action that feels unresponsive or unreadable.

## Avoid health inflation as the default difficulty tool

When a fight is too easy, first test:

- better opponent combinations;
- timing pressure;
- space constraints;
- more meaningful enemy behavior;
- resource pressure;
- objectives that alter priorities;
- reduced safety of dominant strategies.

Increase health or damage when that specifically improves the intended rhythm, not because it is the cheapest scalar.

## Play several approaches

Test the encounter with more than one plausible intention.

Observe whether:

- one strategy dominates every situation;
- the fight adapts as enemies move or states change;
- the player has time to read important threats;
- mistakes create recoverable consequences where intended;
- movement matters;
- feedback makes success and failure understandable;
- the encounter ends before its decisions become repetitive.

Use computer use for feel and readability. Use MCP for exact state, scene structure, and tuning values.

## Engine execution handoff

Use `$godot-game-development` for runtime movement, hit and detection regions, attack state, damage timing, signals, tunable combat data, AnimationPlayer or AnimationTree control, encounter composition, camera response, effects, and actual collision ownership.

Use `$blender-game-assets` for source attack poses, rigs, weapons, silhouettes, source animation, and import helpers. Validate every combat animation in Godot. Keep hit logic and runtime collision in Godot unless a stable import-helper convention has earned a place in the asset pipeline.

## Record combat rules

Update `GAME_DESIGN.md` when an intention, combat rule, enemy role, or encounter principle becomes durable.

Record rejected combat experiments when they reveal why a seemingly good option did not create useful play.
