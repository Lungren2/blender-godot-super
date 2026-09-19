# Agent operating contract

## Scope

This repository implements one MCP system with Blender and Godot host adapters. Do not create parallel engine-specific architectures unless a host constraint requires it.

## Work order

1. Read the relevant architecture or ADR before changing a boundary.
2. Prefer a small contract change before host-specific implementation.
3. Keep discovery/catalog behavior separate from execution.
4. Pair mutations with verification evidence.
5. Preserve undo/preview semantics for editor mutations.
6. Add or update contract tests before widening the advertised capability surface.

## Repository boundaries

- `src/super_mcp/catalog`: capability metadata and discovery.
- `src/super_mcp/contracts`: canonical request/result and safety contracts.
- `src/super_mcp/resources`: MCP resource projections of host state.
- `src/super_mcp/prompts`: reusable workflows and agent procedures.
- `src/super_mcp/evidence`: screenshots, diagnostics, diffs, runtime observations.
- `src/super_mcp/transport`: host bridge transport only.
- `src/super_mcp/hosts`: host-neutral adapter interfaces and routing.
- `integrations/*`: code that must run inside Blender or Godot.

Do not put domain policy into transport code. Do not make engine add-ons the source of truth for MCP schemas.

## Tool-surface rule

Do not expose one MCP tool per engine operation by default. The normal surface should remain discovery-first: host/server status, catalog search, contract/schema lookup, capability invocation, and evidence capture/inspection.

Specialized direct tools require a measured reason to exist.

## Verification

Use local checks first. CI is terminal verification, not an interactive development shell. Keep commits bounded and coherent.
