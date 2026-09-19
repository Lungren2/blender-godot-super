# Third-party notices

This project intentionally reuses existing MCP implementations instead of reimplementing
their engine integrations.

## hybridindie/godot-mcp

- Upstream: https://github.com/hybridindie/godot-mcp
- Imported dependency: `godot-editor-mcp`
- Pinned revision: `daf1cf649f41fc95c403e03859d0461a5b272333`
- License: MIT
- Copyright: Copyright (c) 2026 Johnny D
- Local use: the FastMCP server is mounted in-process so its bridge lifecycle and
  server-global toolset gating persist across requests.

The full upstream MIT license is preserved in
`licenses/hybridindie-godot-mcp-MIT.txt`.

## minihellboy/claude-blender

- Upstream: https://github.com/minihellboy/claude-blender
- Imported dependency: `claude-blender`
- Pinned revision: `5087d87212e0acf3225307c2b3512659c425cc5e`
- License: MIT
- Copyright: Copyright (c) 2024 Claude Code
- Local use: the SDK-v2 MCP server is proxied over stdio by the unified FastMCP server.\n  The matching Blender add-on is copied from the same pinned GitHub archive by\n  `scripts/install_integrations.py`.

The full upstream MIT license is preserved in
`licenses/minihellboy-claude-blender-MIT.txt`.

## Design references not copied

`CallMeJones/blender-agent-bridge` is GPLv3. Its registry, discovery, safety,
preview, and evidence ideas may inform independently written code, but its implementation
is not copied into this MIT repository.
