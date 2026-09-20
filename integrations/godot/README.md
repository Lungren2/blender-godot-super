# Godot integration

Production Godot support comes from the pinned MIT-licensed `hybridindie/godot-mcp` implementation. This repository does not maintain a separate Godot editor plug-in.

Install the matching upstream plug-in into a Godot project with:

```bash
uv run python scripts/install_integrations.py --godot-project /path/to/godot/project
```

The upstream revision is pinned in `pyproject.toml` and `src/super_mcp/installations.py`. Attribution is recorded in `THIRD_PARTY_NOTICES.md`.

Godot's MCP server is mounted in-process by `src/super_mcp/server.py` so its bridge lifecycle and toolset state persist across calls.
