# ADR 0001: Shared core with host adapters

Status: superseded by ADR 0003 and ADR 0004

## Historical decision

The initial scaffold assumed Blender and Godot would share one MCP-facing core and implement engine-specific capabilities behind canonical host contracts.

## Why it changed

Real Blender work showed that shared engine semantics should be extracted only after both hosts demonstrate the same behavior. The MVP later moved further toward reuse by composing mature upstream Blender and Godot MCP implementations rather than rebuilding their operation sets behind a repository-owned host abstraction.

## Still applicable

- Do not force one engine's object model onto the other.
- Keep genuinely shared infrastructure in the parent MCP.
- Upgrade the parent protocol and composition layer in one place.

ADR 0003 defines the reality-first abstraction rule. ADR 0004 defines the current upstream-composition architecture.
