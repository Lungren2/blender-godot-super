# ADR 0001: Shared core with host adapters

Status: accepted for scaffold

## Decision

Blender and Godot integrations share one MCP-facing core. Engine-specific code implements host capabilities behind canonical contracts.

## Why

Two independent MCP implementations would duplicate discovery, safety, evidence, prompt, and protocol behavior and would drift over time. The useful distinction is host capability, not MCP architecture.

## Consequences

- shared contracts must avoid leaking one engine's object model into the other;
- host-specific capabilities remain valid when a common abstraction would be artificial;
- integration directories stay thin;
- protocol upgrades happen once.
