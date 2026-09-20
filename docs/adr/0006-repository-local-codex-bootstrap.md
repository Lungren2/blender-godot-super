# ADR 0006: Repository-local Codex bootstrap

Status: accepted

## Context

Codex supports project-scoped MCP configuration in `.codex/config.toml`. A game repository should be able to opt into `blender-godot-super` without cloning this repository or editing user-global Codex configuration.

The editor integrations have different scopes. Godot plug-ins belong in the game project. Blender add-ons belong in the user's Blender configuration.

## Decision

- Add a `blender-godot-super-init` command for a consumer repository.
- Write a managed `[mcp_servers.blender-godot-super]` section to `.codex/config.toml`.
- Launch the MCP with `uvx` over stdio. When the initializer itself came from Git, pin the generated config to the resolved commit recorded in package metadata.
- Set `cwd = "."` because Codex resolves project MCP working directories from the repository session root.
- Apply the bounded Astra tool allow-list through Codex `enabled_tools`.
- Use a 60-second startup timeout and 180-second tool timeout for first-run resolution, imports, and renders.
- Install the pinned Godot plug-in into the detected or selected Godot project and enable it in `project.godot`.
- Detect the newest Blender user add-ons directory when possible. Otherwise print a `--blender-addons` follow-up command.
- Add `.super-mcp/` to the consumer repository's `.gitignore`.
- Preserve unrelated Codex configuration and refuse to replace a manual MCP section unless `--force` is supplied.

## Consequences

A consuming repository can commit its Codex MCP configuration and Godot integration. Codex CLI, the IDE extension, and ChatGPT desktop can read the same project-scoped MCP entry after the repository is trusted.

The Blender add-on remains user-local because Blender does not load it from the game repository. Enabling `Claude Blender` remains a one-time Blender preference action.

The initializer requires `uvx`. The one-line setup command already uses `uvx`, so the game repository does not need its own Python environment for this MCP.
