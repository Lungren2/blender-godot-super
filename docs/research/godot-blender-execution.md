# Godot and Blender execution source record

This note supports the engine-execution skills installed into consumer game repositories.

The design skills decide what player-facing problem to solve. The engine skills decide how to express the chosen experiment in Godot and Blender without broadening the architecture unnecessarily.

## Godot composition

Official getting-started material treats nodes and scenes as the basic building blocks and introduces signals as the engine mechanism for communication between objects.

Sources:
https://docs.godotengine.org/en/stable/getting_started/step_by_step/
https://docs.godotengine.org/en/stable/tutorials/scripting/instancing_with_signals.html

The signal guidance explicitly notes that signals help decouple objects and avoid fixed scene-tree parent relationships in cases such as runtime instancing.

Repository adaptation:

- keep local behavior on the scene or node that owns it;
- use direct references inside one stable scene when ownership is obvious;
- use signals when the sender should announce an event without owning the receiver;
- do not create a project-wide event bus for a small number of local relationships.

## Godot animation

Godot documents `AnimationPlayer` as the source of animations and `AnimationTree` as the node for advanced blending and state-driven transitions. `AnimationTree` references animations stored in `AnimationPlayer` rather than owning separate animation clips.

Sources:
https://docs.godotengine.org/en/stable/tutorials/animation/
https://docs.godotengine.org/en/stable/tutorials/animation/animation_tree.html

Repository adaptation:

- use authored animation to communicate anticipation, active action, recovery, impact, readiness, and state change;
- keep gameplay-critical timing observable in code or data when hiding the rule in animation tracks would make testing difficult;
- use computer interaction when the bounded MCP does not expose the editor operation needed to author an animation graph.

## Godot 3D import

Godot recommends glTF 2.0 for 3D scenes and also supports direct `.blend` import by invoking Blender and routing the result through the glTF import pipeline.

Sources:
https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/available_formats.html
https://docs.godotengine.org/en/stable/classes/class_editorsceneformatimporterblend.html

Godot's import documentation also describes imported scenes, inherited or wrapper scenes, import configuration, and Advanced Import Settings.

Sources:
https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/
https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/import_configuration.html

Repository adaptation:

- keep Blender or glTF as source visual data;
- wrap imported visuals in a hand-authored Godot scene when gameplay scripts, effects, collision, navigation, or state need to survive source reimport;
- fix geometry and source animation in Blender, and fix gameplay ownership in Godot.

## Godot import hints

Godot supports name suffixes in source 3D files for repeated import behavior, including collision generation, navigation, ignored objects, and animation looping.

Source:
https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/node_type_customization.html

Examples used by the Blender skill include `-col`, `-convcol`, `-colonly`, `-convcolonly`, `-navmesh`, `-noimp`, and loop or cycle animation names.

The same Godot documentation recommends simple primitive collision shapes when possible because detailed mesh collision can cost performance and reliability.

## Blender non-destructive modeling

Blender's manual defines modifiers as non-destructive operations that change evaluated geometry without changing the editable base mesh until the modifier is applied.

Source:
https://docs.blender.org/manual/en/4.5/modeling/modifiers/introduction.html

Repository adaptation:

- keep Mirror, Array, Bevel, Boolean, Subdivision, and similar work non-destructive while a game's visual requirement is still changing;
- apply modifiers only when export, topology cleanup, performance, or a downstream task requires it.

## Blender armatures

Blender's Armature modifier is the standard deformation path for meshes driven by skeletal rigs and supports vertex-group weighting.

Source:
https://docs.blender.org/manual/en/4.5/modeling/modifiers/deform/armature.html

Repository adaptation:

- build only the rig needed by actual gameplay motions;
- validate one representative deformation and animation in Godot before producing a large animation library.

## glTF material and animation boundary

Blender's glTF exporter documents the metal/rough PBR material channels and supported real-time animation data such as object transforms, pose bones, and shape keys.

Source:
https://docs.blender.org/manual/en/4.5/addons/import_export/scene_gltf2.html

Repository adaptation:

- prefer simple PBR-compatible source materials when they are meant to cross the import boundary;
- keep engine-specific shader behavior in Godot;
- do not assume Blender-only material or animation behavior survives import unless the format supports it and the result was checked in Godot.

## Current MCP boundary

The current Astra profile exposes Godot inspection, scene editing, editor screenshot, runtime capture, and testing tools, plus Blender inspection, object operations, materials, modifiers, keyframes, renders, save, checkpoint, and undo.

The bounded profile does not expose arbitrary Blender Python. It also does not enable every Godot donor toolset.

Repository sources:
`src/super_mcp/astra.py`
`docs/architecture.md`

The pinned donors remain the authority for their native tool behavior:
https://github.com/hybridindie/godot-mcp
https://github.com/minihellboy/claude-blender

The execution skills route unsupported specialized editor work through computer use or repository source editing rather than pretending MCP can perform an operation that is not in the bounded profile.
