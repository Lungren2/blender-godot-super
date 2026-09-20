# ADR 0005: Private automation transport and observable agent trajectories

Status: accepted

## Context

The unified MCP now needs to support long-horizon GPT-6 Astra development loops without making the engine integration itself OpenAI-specific.

A local stdio process is sufficient for desktop clients, but the OpenAI Responses API needs an MCP endpoint reachable either through a secured remote URL or Secure MCP Tunnel. Long automated runs also need evidence that can be inspected independently of model reasoning.

## Decision

- Keep stdio as the default transport.
- Add loopback-only Streamable HTTP at the parent MCP boundary.
- Use OpenAI Secure MCP Tunnel outside the server process for private Responses API access.
- Keep OpenAI credentials out of this repository and out of the MCP server.
- Generate an Astra `allowed_tools` profile at the client edge rather than renaming or wrapping donor tools.
- Exclude `blender_execute` and destructive Godot scene tools from that unattended profile.
- Seed only the Godot toolsets needed by the automated development loop.
- Add parent middleware that records tool calls, resource reads, prompt renders, outcomes, durations, and extracted binary/image artifacts.
- Treat mutation verification as a trajectory: inspect/checkpoint, mutate, capture visual evidence, save, restart, then verify persisted host state.
- Keep a real dual-editor CI scenario for that full trajectory.

## Consequences

The MCP remains usable by non-OpenAI clients and preserves engine-native donor semantics. The OpenAI-specific policy is a launch/configuration concern.

Loopback HTTP is not a public deployment mode. Operators must use Secure MCP Tunnel or another authenticated network boundary.

Audit logs contain development data even after known secret-shaped keys are redacted. They are git-ignored by default and must be handled as sensitive evidence.

The bounded Astra profile is intentionally narrower than the full MCP. Widen it only when a real workflow demonstrates that a missing operation is necessary.
