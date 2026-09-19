# ADR 0002: Discovery-first tool surface

Status: accepted for scaffold

## Decision

Do not advertise the full engine capability catalog as one MCP tool per operation by default.

Use a small stable gateway for status, discovery, contract lookup, invocation, and evidence access. Resources and prompts carry read-state and procedure where those MCP primitives fit better.

## Why

Large static tool surfaces consume context, weaken tool selection, and couple agent behavior to implementation breadth. Blender and Godot can each expose hundreds of useful operations; capability count should not determine model-facing schema count.

## Consequences

- capability metadata and search quality become core infrastructure;
- schemas must be retrievable on demand;
- invocation must preserve strong typing and structured errors;
- frequently used operations may earn direct tools later, based on evidence rather than convenience.
