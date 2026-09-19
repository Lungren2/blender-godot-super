# Blender integration

This directory contains only code that must execute inside Blender.

Planned responsibilities:

- add-on lifecycle and connection state;
- main-thread dispatch for `bpy` work;
- host capability implementation behind shared contracts;
- editor-aware undo/preview hooks;
- render or viewport evidence capture.

MCP registration, capability schemas, discovery policy, and workflow prompts belong in `src/super_mcp`.
