# Godot integration

This directory contains only code that must execute inside the Godot editor.

Planned responsibilities:

- editor plugin lifecycle and connection state;
- scene-tree and editor operations behind shared contracts;
- `EditorUndoRedoManager` integration for mutations;
- viewport/runtime evidence capture;
- Godot-native validation and runtime probes.

MCP registration, capability schemas, discovery policy, and workflow prompts belong in `src/super_mcp`.
