# ADR 0002: Discovery-first tool surface

Status: superseded by ADR 0004

## Historical decision

The initial scaffold proposed a small application-level gateway for status, discovery, schema lookup, invocation, and evidence instead of advertising many direct engine operations.

## Why it changed

The chosen upstream implementations already have working model-facing tool strategies:

- Godot uses gated FastMCP toolsets.
- Blender exposes a moderate direct tool set.

Adding another search/schema/invoke protocol before measuring a real problem would duplicate working behavior and make the MVP harder to reason about.

## Current rule

Preserve the donor tool names and MCP resources. Keep MCP protocol discovery separate from any future application capability catalog. Add another discovery layer only if real agent runs show that the combined tool set harms tool selection or context use.

ADR 0004 defines the current composition decision.
