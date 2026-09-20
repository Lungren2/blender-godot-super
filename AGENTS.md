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

Preserve the pinned donors' working tool-surface strategies: Blender's direct tools and Godot's gated toolsets.

Do not add another search/schema/invoke gateway merely because the repository has reserved catalog directories. Add one only if measured model behavior shows that the composed donor surface needs it.

## Research record

The raw architecture discussion is preserved verbatim in `docs/research/architecture-debate-transcript.md` and `docs/research/ecosystem-survey-transcript.md`. Read them when revisiting host boundaries, capability discovery, resource/tool ownership, evidence, or tool-surface scaling.

Those transcripts are source material, not settled decisions. ADRs and current implementation state remain authoritative where they diverge.

## Automated development loop

For unattended or long-horizon mutation work:

1. Inspect host state before editing.
2. Create an undo/checkpoint boundary before risky Blender changes and preserve Godot dry-run/undo semantics.
3. Prefer bounded donor tools; do not use arbitrary Blender Python execution in unattended profiles.
4. Use MCP reads for semantic truth. Use computer-use screenshots for visible UI truth. Inspect a screenshot before acting when the UI state is unknown, and inspect another after a short group of UI actions.
5. Verify mutations with observable evidence such as resources, renders, screenshots, runtime output, or tests.
6. Save editor state explicitly.
7. Restart the affected editor when persistence is part of the acceptance criteria, then verify the saved state through MCP again.
8. Keep the parent action/artifact audit enabled so the executed trajectory can be reviewed independently of model reasoning.
9. After functional verification, run `uv run python scripts/check_repo_hygiene.py --include-untracked` and inspect git status. Remove generated clutter and move misplaced new files into established directories. Do not reorganize unrelated code as a cleanup exercise.

## Verification

Use local checks first. CI is terminal verification, not an interactive development shell. Keep commits bounded and coherent.
