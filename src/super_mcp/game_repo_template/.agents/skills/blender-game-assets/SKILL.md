---
name: blender-game-assets
description: Use when a game-design decision requires Blender modeling, materials, modifiers, rigging, animation, collision helpers, environment pieces, or repeated Blender-to-Godot asset iteration. Focuses on game-ready assets and in-engine validation rather than isolated beauty renders.
---

# Build game assets in Blender

Use this skill after the gameplay need is clear.

The target is not a beautiful Blender file. The target is an asset that works in the game at the required camera distance, scale, lighting, animation, collision, and performance budget.

## Tool boundary in this repository

The bounded Blender MCP provides:

- scene and object inspection;
- checkpoints and undo;
- primitive object creation;
- object modification;
- material creation and assignment;
- modifiers;
- duplication;
- parenting and collection organization;
- camera framing;
- animation keyframes and frame range;
- screenshots and renders;
- explicit save.

The unattended profile intentionally excludes arbitrary Blender Python.

Use MCP for the operations it exposes. Use computer use for Blender editor work that needs direct mesh editing, UV work, rig editing, weight painting, NLA setup, export dialogs, or other visual-editor operations outside the bounded MCP.

Use shell and repository tools for file placement, naming, version control, import-side Godot files, and automated validation that does not require unsafe Blender scripting.

Do not widen the unattended tool list merely to avoid using Blender's normal editor for a specialized task.

## Start from the in-game requirement

Before touching Blender, read the relevant part of `GAME_DESIGN.md` and inspect the target Godot scene.

Write down the requirements that matter for the asset:

- gameplay purpose;
- expected camera distance and angle;
- approximate world scale;
- silhouette requirement;
- whether it is static, dynamic, skinned, or animated;
- whether collision comes from Godot primitives, imported helpers, or the mesh;
- whether the asset repeats or is unique;
- material and readability needs;
- animation states if any;
- expected import path into Godot.

Do not infer these requirements from what would make the Blender viewport look impressive.

## Block out before detailing

For a new asset:

1. create simple primitives;
2. set rough dimensions and proportions;
3. set the origin and object organization needed by the gameplay use;
4. frame the object and inspect the silhouette;
5. save the `.blend`;
6. import or refresh it in Godot immediately;
7. inspect it in the real gameplay camera;
8. change proportions before adding detail.

For environment kits, test a few pieces assembled into an actual Godot room before producing the full kit.

For animated characters, test the rest pose, root placement, and one critical action before building a large animation set.

## Preserve editability while the design is uncertain

Use non-destructive modifiers when they make iteration cheaper.

Typical uses include:

- Mirror for symmetric forms;
- Array for repeated structure;
- Bevel for readable edges;
- Boolean for blockout and hard-surface iteration;
- Subdivision only when the game presentation needs it;
- Armature for deformation of skinned assets.

Do not apply modifiers early just to make the mesh look finished.

Apply or collapse work only when export, topology cleanup, performance, or a downstream task requires it.

## Use silhouette and proportion as the first visual test

At normal game distance, small topology details disappear.

Before adding detail, check:

- can the player distinguish the asset from related assets;
- are important gameplay-facing parts visible;
- does the object read against the intended background;
- is the orientation obvious;
- does the pose communicate intent;
- does the scale match nearby objects in Godot.

Use Blender renders for controlled inspection, but accept or reject the asset in Godot.

## Keep materials simple until the form works

Start with the smallest material setup that supports the game's visual language.

For assets intended for glTF import, prefer ordinary metal/rough PBR-compatible material inputs when practical. Blender's glTF exporter supports the common base-color, metallic, roughness, normal, occlusion, and emissive workflow.

Do not build a complex Blender-only shader graph when the final look depends on a Godot shader.

If the material's important behavior is engine-specific, keep the Blender material as an authoring/readability approximation and implement the final effect in Godot.

## Use UV work only when the asset needs it

Do not unwrap an early blockout because every final asset eventually might need UVs.

Use computer use for Blender UV editing when the texture workflow, trim sheet, atlas, lightmap, or hand-authored texture requires it.

For simple procedural or solid-color materials, defer UV work until a concrete texture requirement appears.

## Build collision for gameplay, not visual fidelity

Prefer simple Godot collision primitives for dynamic gameplay objects when they approximate the gameplay shape well.

When imported collision helpers are useful, Godot recognizes model-name suffixes such as `-col`, `-convcol`, `-colonly`, and `-convcolonly`. Use simple helper geometry rather than copying the full visual mesh when possible.

For level geometry, collision can be more detailed, but still avoid unnecessary triangles in collision data.

Do not let an artistically detailed mesh define gameplay collision merely because it already exists.

## Use import hints only when they simplify repeated work

Godot can recognize source-object naming hints for collision, navigation, ignored objects, looped animations, and other import behavior.

Use them when they make the Blender source communicate stable import intent.

Examples include:

- `-col` or `-colonly` for collision generation;
- `-convcol` or `-convcolonly` for convex collision;
- `-navmesh` for navigation source geometry;
- `-noimp` for Blender-only helpers that should not enter the game;
- `loop` or `cycle` in animation names when the import should mark an animation as looping.

Do not encode one-off experiments into permanent naming conventions.

## Organize the Blender file around export intent

Use clear collections and names for things that have different game roles.

Separate when useful:

- render geometry;
- collision helpers;
- rig;
- animation helpers;
- Blender-only reference or lighting objects;
- modular pieces.

Keep object origins and hierarchy intentional because they affect placement, animation, instancing, and imported transforms.

Do not create a deep collection hierarchy that the game import does not use.

## Rig only after the gameplay motion requirement is known

Before building a detailed rig, identify the motions the game actually needs.

For a small game asset, the rig needs to support the required deformation and animation workflow, not every possible pose.

Use an Armature modifier for skinned deformation. Keep bone naming and vertex groups stable once animations depend on them.

Test one representative deformation in Godot before producing a large animation library.

If an asset only needs rigid part motion, object or bone transforms may be enough. Do not build a complex deformation rig by default.

## Animate for gameplay readability

Start with the animation states that affect player decisions:

- idle or readiness;
- locomotion;
- anticipation;
- attack or interaction;
- impact or hit reaction;
- recovery;
- death or disable state where needed.

For combat, make the key pose and timing readable at the gameplay camera distance before adding secondary motion.

Use Blender keyframes and frame range where the bounded MCP is sufficient. Use computer use for graph editor, NLA, rig control, or detailed animation editing that needs the Blender UI.

Validate imported animations in Godot. Blender playback alone is not enough.

## Choose the Blender-to-Godot path deliberately

For a solo or tightly controlled local workflow, keeping `.blend` files inside the Godot project can make iteration fast. Godot can call Blender and import the `.blend` through its glTF pipeline, so saving in Blender and returning to Godot can trigger reimport.

Use this when:

- every relevant development machine has a compatible Blender install;
- fast source iteration matters more than decoupling the DCC tool from the project;
- committing `.blend` source files is acceptable.

Use explicit glTF or GLB when:

- the game should not require Blender on every machine;
- CI or collaborators need portable import artifacts;
- exported assets are part of a controlled build pipeline;
- the asset should be consumed independently of the Blender source file.

Godot recommends glTF 2.0 for 3D scenes. Blender's exporter also maps ordinary real-time mesh, PBR material, skeleton, and animation data well to glTF.

Do not keep both `.blend` and generated `.glb` in version control unless the project has a reason to own both.

## Wrap imported visuals in Godot instead of polluting the source asset

Keep gameplay behavior in Godot when it is game-specific.

A practical pattern is:

1. Blender file owns source geometry, rig, source animation, and import hints;
2. Godot imports that source into an engine scene;
3. a hand-authored Godot wrapper scene instances the imported visual;
4. the wrapper owns scripts, runtime hitboxes, effects, audio, navigation, and gameplay state;
5. Blender can reimport without destroying the wrapper's gameplay logic.

Fix geometry and source-animation problems in Blender. Fix gameplay ownership in Godot.

## Execute a tight asset loop

For each meaningful asset iteration:

1. inspect the current Blender object and Godot use site;
2. checkpoint Blender before risky changes;
3. change one visual or functional concept;
4. save the `.blend`;
5. let Godot reimport or export through the chosen pipeline;
6. run the representative gameplay scene;
7. inspect the result with computer use;
8. check scale, silhouette, orientation, animation, material, collision, and readability;
9. revise in the tool that owns the problem;
10. stop when the current design question is answered.

Do not finish a full asset family before one representative asset works in-game.

## Route common design problems to the owning tool

If the problem is proportion, topology, rig deformation, source animation, origin, or source material setup, fix it in Blender.

If the problem is gameplay collision, state, hit logic, camera, runtime effects, UI, engine shader behavior, or scene composition, fix it in Godot.

If the problem is unclear, inspect both the imported source and the runtime result before changing either.

## Avoid common model-generated Blender mistakes

Do not:

- add fine geometry before the silhouette works;
- model details the gameplay camera cannot show;
- use the render camera as the only review angle;
- build complex materials before the engine look is established;
- apply every modifier early;
- build a large rig before one gameplay animation validates the skeleton;
- use dense visual geometry as default collision;
- create a whole modular kit before a small assembled sample works in Godot;
- polish Blender presentation objects that are not part of the game import;
- claim an asset is finished without seeing it in Godot.

## Finish with an asset-specific check

Before stopping, confirm the relevant items:

- world scale is correct in Godot;
- origin and orientation support placement and animation;
- silhouette works at gameplay distance;
- materials survive the import path or have an intentional Godot replacement;
- collision ownership is explicit;
- required animation imports and plays correctly;
- source helpers do not leak into the game unintentionally;
- the `.blend` is saved;
- the representative game scene was run and observed;
- any durable asset-pipeline decision is recorded in `GAME_DESIGN.md` or project guidance.

## Primary references

Godot 3D formats and Blender import:
https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/available_formats.html

Godot import configuration:
https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/import_configuration.html

Godot import naming hints:
https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/node_type_customization.html

Blender modifiers:
https://docs.blender.org/manual/en/4.5/modeling/modifiers/introduction.html

Blender armature modifier:
https://docs.blender.org/manual/en/4.5/modeling/modifiers/deform/armature.html

Blender glTF exporter:
https://docs.blender.org/manual/en/4.5/addons/import_export/scene_gltf2.html

Pinned MCP donor:
https://github.com/minihellboy/claude-blender
