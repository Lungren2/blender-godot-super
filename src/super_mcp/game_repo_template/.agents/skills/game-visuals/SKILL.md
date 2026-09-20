---
name: game-visuals
description: Use for game art direction, asset review, composition, lighting, color, animation, VFX, UI readability, visual feedback, or deciding whether a Blender asset works in the actual game.
---

# Visual design for playable games

## Source anchor

Playlist lesson: Brackeys, "How to MAKE YOUR GAME LOOK GOOD!"
https://www.youtube.com/watch?v=nvbQ9_bzx1k

Playlist:
https://www.youtube.com/playlist?list=PLPV2KyIb3jR5kPzHBi90byfhPfPqaDW9s

The lesson focuses on getting strong results through composition, lighting, movement, and color rather than relying on expensive assets. The procedure below adapts that lens to Blender, Godot, and computer-use iteration.

## Judge visuals in the game

Read the "Visual language" and quality budget in `GAME_DESIGN.md`.

Do not finish an asset in Blender and only then discover whether it works.

For gameplay assets:

1. establish purpose, silhouette, and scale;
2. create the cheapest useful version;
3. import or preview it in Godot;
4. inspect it through the actual gameplay camera and lighting;
5. adjust readability and hierarchy;
6. add detail only after it works in context.

The game view is the acceptance environment.

## Start with composition

Each important view should make the current gameplay information easy to find.

Check:

- where the player's eye lands first;
- whether the player character is readable;
- whether threats separate from the background;
- whether the route or objective is understandable;
- whether foreground objects block important information;
- whether UI competes with the world;
- whether decorative detail steals attention.

Change placement, framing, scale, and negative space before adding more effects.

## Use lighting to communicate

Lighting should help with form, depth, navigation, mood, and hierarchy.

Ask:

- What should be brightest or darkest?
- Does the player separate from the environment?
- Are hazards hidden unintentionally?
- Does the critical path receive enough visual support?
- Is the mood still readable during movement?
- Does lighting survive the normal gameplay camera rather than only a staged screenshot?

Prefer a small intentional lighting setup over many lights with no clear job.

## Use color as a system

Define what important colors mean.

Use color to separate:

- player and enemies;
- safe and dangerous states;
- interactable and decorative objects;
- factions or resource types;
- foreground and background.

Do not rely on color alone for mandatory information. Support it with shape, motion, value, iconography, sound, or position when practical.

Avoid using maximum saturation everywhere. Reserve strong accents for information that deserves attention.

## Add movement where it communicates state

Animation, particles, camera response, UI motion, and environmental movement should help the player understand action and state.

Use motion for things such as:

- anticipation;
- impact;
- readiness;
- damage;
- pickup confirmation;
- navigation;
- danger;
- recovery.

Do not animate every element simply because movement makes a scene look busy.

## Make effects carry information first

For VFX and feedback, build in this order:

1. clarity: the player can see what happened;
2. style: the effect matches the game's visual language;
3. secondary feel: camera, distortion, particles, sound, or extra response.

If the clarity layer fails, more particles usually make the result harder to read.

Protect enemy telegraphs, the player, important UI, navigation surfaces, and other critical information from effect noise.

## Prefer a coherent style over expensive assets

Simple geometry, textures, or sprites can work when composition, lighting, color, shape language, and motion agree.

Do not solve visual inconsistency by raising asset complexity everywhere.

Pick a few repeated visual rules and use them consistently.

## Inspect representative gameplay, not beauty shots

Use computer use to capture the game while it is actually being played.

Review representative states such as:

- normal traversal;
- combat under load;
- low health or failure;
- rewards or pickups;
- busy rooms;
- dark rooms;
- menus or HUD during play.

When useful, compare screenshots at small size or in grayscale to expose weak hierarchy.

## Spend polish according to exposure

Prioritize visuals the player sees often or relies on for decisions:

- player movement;
- enemies and telegraphs;
- hit feedback;
- core environment kit;
- HUD;
- pickups and rewards;
- repeated transitions.

A rare prop does not deserve the same polish budget as the movement animation seen every second.

## Engine execution handoff

Use `$godot-game-development` for final composition in the game camera, WorldEnvironment and lighting, engine materials and shaders, particles, UI, camera response, runtime visibility, and acceptance screenshots.

Use `$blender-game-assets` for source geometry, silhouette, proportion, topology, UVs when required, source materials, rigs, and source animation. Import early and let the running Godot scene decide whether more Blender detail is worth adding.

When the result differs between Blender and Godot, treat Godot as the acceptance environment and fix the problem in the tool that owns it.

## Record the visual language

Update `GAME_DESIGN.md` when a visual rule becomes durable, such as palette, shape language, lighting rule, feedback convention, or readability target.

Do not turn temporary experiment colors or effects into project-wide rules until they work in context.
