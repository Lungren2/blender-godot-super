# Agent operating contract

## Scope

This repository implements one MCP system with Blender and Godot integrations. Shared infrastructure is a goal; shared engine semantics must be demonstrated rather than assumed.

## Work order

1. Read the relevant architecture or ADR before changing a boundary.
2. Exercise real host behavior before introducing a broad common abstraction.
3. Keep MCP protocol discovery distinct from any future application capability catalog.
4. Prefer resources for addressable read-oriented state.
5. Preserve engine-native semantics when a common vocabulary would be artificial.
6. Pair mutations with verification artifacts or observations.
7. Preserve undo/preview semantics for editor mutations.
8. Add or update contract tests before widening the advertised surface.

## Repository boundaries

- `src/super_mcp/catalog`: reserved for capability metadata and discovery if later justified.
- `src/super_mcp/contracts`: shared contracts proven by real host behavior.
- `src/super_mcp/resources`: MCP resource composition.
- `src/super_mcp/prompts`: reusable workflows and agent procedures.
- `src/super_mcp/evidence`: artifact/evidence support once concrete forms require it.
- `src/super_mcp/transport`: host bridge transport only.
- `src/super_mcp/hosts`: server-side host-specific adapters and later shared host boundaries.
- `integrations/*`: code that must run inside Blender or Godot.

Do not put domain policy into transport code. Do not make engine add-ons the source of truth for MCP-facing schemas.

## Abstraction rule

A fake implementation may test an established contract; it must not be used as the primary evidence that a new host abstraction is correct.

Do not force Blender and Godot through a shared scene/object/node ontology until real slices show equivalent semantics.

## Tool-surface rule

Do not expose one MCP tool per engine operation by default.

A discovery-first application gateway remains a candidate for later breadth. Do not build it merely because the repository has reserved catalog directories.

## Verification

Use local checks first. CI is terminal verification, not an interactive development shell. Keep commits bounded and coherent.
