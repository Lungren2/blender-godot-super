I dug through the current ecosystem with a fairly strict definition of “modern.” The bar I used was MCP **2026-07-28**, not merely “uses MCP somewhere.” That revision removed the initialization/session model, introduced per-request protocol metadata and `server/discover`, and the current TypeScript v2 / Python v2 SDK lines implement it. ([GitHub](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2026-07-28/changelog.mdx?utm_source=chatgpt.com "modelcontextprotocol/docs/specification/2026-07-28/changelog.mdx at main · modelcontextprotocol/modelcontextprotocol · GitHub"))

There’s a pretty clear answer for **Godot**. **Blender is more interesting: the best protocol implementation and the best engineered agent interface are currently two different projects.**

### My shortlist

| ProjectCurrent MCPWhy it caught my attentionMain reservation |                                      |                                  |                                                                                                                                                          |                                                                            |
| ------------------------------------------------------------ | ------------------------------------ | -------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| **Blender — use now**                                        | **minihellboy/claude-blender**       | **2026-07-28 / Python SDK v2**   | Resources, workflow prompts, structured output, tool annotations, visual feedback loops, checkpoints/undo, separate Blender bridge, real project skills  | Young project; alpha, only \~10 commits, Blender testing says 4.3          |
| **Blender — architecture benchmark**                         | **CallMeJones/blender-agent-bridge** | **Legacy MCP surface currently** | Exceptional tool-discovery architecture, 5-tool gateway over 240 contracts, resources/evidence, reversible previews, security contracts, extensive tests | Its current smoke test still uses `initialize` and protocol `2024-11-05`   |
| **Godot — strongest match**                                  | **hybridindie/godot-mcp**            | **2026-07-28 / FastMCP 4**       | Gated toolsets, prompts, resources, skills, safety classes, dry-runs, undo, runtime probe, debugging workflows, typed contracts, serious test discipline | Huge underlying capability surface, although it handles that intelligently |
| **Godot — leaner alternative**                               | **mcintalmo/godot-engine-mcp**       | **2026-07-28 / Python SDK v2**   | Excellent Editor/CLI/LSP architecture, EditorUndoRedoManager, multimodal screenshots, semantic references/renames, strict schemas                        | Much newer/smaller ecosystem                                               |
| **Godot — execution-heavy alternative**                      | **Vollkorn-Games/godot-mcp**         | **2026-07-28 / TS SDK v2**       | Real-engine testing, interactive playtesting, batched test sequences, cached tool lists, old-client fallback                                             | More “large capable toolbox” than carefully authored agent interface       |

## Godot: `hybridindie/godot-mcp` is the one I’d pick

This one is unusually close to what you’re describing.

[hybridindie/godot-mcp](https://github.com/hybridindie/godot-mcp?utm_source=chatgpt.com)

It pins **FastMCP 4.0.1**, which is built around MCP 2026-07-28 and the v2 SDK architecture. FastMCP 4 explicitly supports the new sessionless protocol while retaining compatibility with older clients. ([GitHub](https://github.com/hybridindie/godot-mcp/blob/main/pyproject.toml "godot-mcp/pyproject.toml at main · hybridindie/godot-mcp · GitHub"))

More importantly, somebody has actually thought about **how an agent should interact with Godot**.

There are 181 capabilities, but it does **not** dump 181 tools into the model context. `core` and read-only `inspection` stay exposed; another 27 toolsets are gated. The agent discovers what exists and enables domains when needed. That directly addresses the tool-selection/context degradation problem you’ve been concerned about in agent systems. ([GitHub](https://github.com/hybridindie/godot-mcp?utm_source=chatgpt.com "GitHub - hybridindie/godot-mcp: Combination of Godot Addon and MCP server for AI driven development · GitHub"))

Its intended workflow is explicitly:

> discovery → planning/safety classification → enable relevant surface → mutation → verification → runtime testing

That manifests in actual architecture rather than README rhetoric. It has `godot_get_server_info`, `godot_list_toolsets`, safety-class discovery, `dry_run`, debug macros, runtime assertions, scene inspection and screenshot feedback. ([GitHub](https://github.com/hybridindie/godot-mcp/blob/main/README.md?utm_source=chatgpt.com "godot-mcp/README.md at main · hybridindie/godot-mcp · GitHub"))

The MCP primitives are also being used properly instead of treating MCP as glorified function calling. It exposes `godot://` resources for project/scene/node state and MCP prompts for workflows such as `build_scene`, `play_test`, `script_edit`, `debug_scene`, `author_resource`, `export_build`, and `batch_refactor`. It then adds optional agent skills above those primitives. ([GitHub](https://github.com/hybridindie/godot-mcp?utm_source=chatgpt.com "GitHub - hybridindie/godot-mcp: Combination of Godot Addon and MCP server for AI driven development · GitHub"))

That layering is excellent:

**Godot state → resources**
**atomic capabilities → tools**
**repeatable procedure → prompts**
**agent behaviour/domain knowledge → skills**

That’s much closer to how I think an MCP should be designed.

There’s also evidence of normal engineering discipline: typed Pydantic boundaries, an explicit WebSocket bridge contract, structured error envelopes rather than leaking tracebacks, reconnect behaviour, version gating against Godot versions, \~304 tests documented in the current setup, strict mypy, Ruff and separate contract/integration/unit testing. ([GitHub](https://github.com/hybridindie/godot-mcp?utm_source=chatgpt.com "GitHub - hybridindie/godot-mcp: Combination of Godot Addon and MCP server for AI driven development · GitHub"))

**This is the Godot MCP I’d install first.**

### `mcintalmo/godot-engine-mcp` is also worth watching closely

[mcintalmo/godot-engine-mcp](https://github.com/mcintalmo/godot-engine-mcp?utm_source=chatgpt.com)

This has a smaller surface, but the architecture may appeal to you even more.

It uses three complementary integration paths: a live editor WebSocket bridge, headless Godot CLI fallback, and the actual Godot GDScript LSP for definitions, references, hover docs and semantic renames. ([GitHub](https://github.com/mcintalmo/godot-engine-mcp?utm_source=chatgpt.com "GitHub - mcintalmo/godot-engine-mcp · GitHub"))

The editor path uses `EditorUndoRedoManager` rather than simply writing `.tscn` files behind Godot's back. It also exposes 2D/3D viewport captures and physics queries to the model. Offline operations fall through to actual `godot --headless` execution and `--check-only` validation. ([GitHub](https://github.com/mcintalmo/godot-engine-mcp/blob/main/README.md?utm_source=chatgpt.com "godot-engine-mcp/README.md at main · mcintalmo/godot-engine-mcp · GitHub"))

Its dependencies explicitly require `mcp>=2.0.0`, and the project describes itself against the 2026-07-28 stateless protocol. ([GitHub](https://github.com/mcintalmo/godot-engine-mcp/blob/main/pyproject.toml "godot-engine-mcp/pyproject.toml at main · mcintalmo/godot-engine-mcp · GitHub"))

For an **IDE-like coding agent**, the editor + compiler + semantic LSP architecture is extremely compelling.

## Blender: `minihellboy/claude-blender` is the strict match

[minihellboy/claude-blender](https://github.com/minihellboy/claude-blender?utm_source=chatgpt.com)

This was the Blender project I found that satisfies both halves of your requirement without hand-waving about the protocol.

Its `pyproject.toml` actually depends on:

`mcp>=2.0.0,<3`

and the project explicitly targets **2026-07-28**. ([GitHub](https://github.com/minihellboy/claude-blender/blob/main/pyproject.toml?utm_source=chatgpt.com "claude-blender/pyproject.toml at main · minihellboy/claude-blender · GitHub"))

It exposes **28 tools, three resources and workflow prompts**, plus tool annotations and structured output. The resources include live scene state, object details and the latest visual render. ([GitHub](https://github.com/minihellboy/claude-blender?utm_source=chatgpt.com "GitHub - minihellboy/claude-blender: AI-powered Blender control via Claude Code using MCP (Model Context Protocol) · GitHub"))

More interestingly, the author has started encoding agent procedure separately from raw Blender operations. The repository includes workflows such as `/blender-iterate`, `/blender-studio-shot`, and `/blender-turntable`; `blender-iterate` is explicitly a render → critique → adjust feedback loop. ([GitHub](https://github.com/minihellboy/claude-blender?utm_source=chatgpt.com "GitHub - minihellboy/claude-blender: AI-powered Blender control via Claude Code using MCP (Model Context Protocol) · GitHub"))

It also has some sane host engineering. Blender API calls are run through `bpy.app.timers` on Blender's main thread because `bpy` isn't thread-safe, while the MCP process lives separately and communicates with Blender through a JSON-RPC TCP bridge. That gives you process isolation and lets the MCP process restart without taking Blender with it. ([GitHub](https://github.com/minihellboy/claude-blender/blob/main/README.md?utm_source=chatgpt.com "claude-blender/README.md at main · minihellboy/claude-blender · GitHub"))

Visual operations return images inline, risky work can be preceded by `blender_checkpoint`, undo is a first-class tool, and rendering temporarily changes settings rather than leaving those changes behind. ([GitHub](https://github.com/minihellboy/claude-blender?utm_source=chatgpt.com "GitHub - minihellboy/claude-blender: AI-powered Blender control via Claude Code using MCP (Model Context Protocol) · GitHub"))

That is the beginning of a real **observe → act → verify** interface rather than `execute_python(script)` with an MCP sticker on it.

The catch is maturity. It's currently marked alpha, has only about ten commits, and advertises Blender 4.0+ while saying it was tested on 4.3. ([GitHub](https://github.com/minihellboy/claude-blender?utm_source=chatgpt.com "GitHub - minihellboy/claude-blender: AI-powered Blender control via Claude Code using MCP (Model Context Protocol) · GitHub"))

So I like the *direction* considerably more than I trust it yet.

## The Blender project I'd steal design ideas from

This surprised me: **CallMeJones/blender-agent-bridge** is considerably more engineered than most Blender MCPs I found.

[CallMeJones/blender-agent-bridge](https://github.com/CallMeJones/blender-agent-bridge?utm_source=chatgpt.com)

Its normal model-facing MCP contains **exactly five tools**:

`blender_bridge_status`
`blender_tool_catalog`
`search_blender_tools`
`get_blender_tool_schema`
`invoke_blender_tool`

Behind that sits roughly **240 canonical Blender contracts**. The model searches for capabilities, obtains the schema of the chosen operation, then invokes it. ([GitHub](https://github.com/CallMeJones/blender-agent-bridge?utm_source=chatgpt.com "GitHub - CallMeJones/blender-agent-bridge: Safe, scene-aware MCP bridge for Blender with reversible editing and visual evidence. · GitHub"))

That is much better than advertising hundreds of schemas up front.

Its canonical `ToolSpec` isn't just name + JSON schema either. Contracts carry mutation, confirmation, preview, network, filesystem and output metadata, ownership, exposure mode and routing groups. Generated registry views prevent those definitions drifting across layers. ([GitHub](https://github.com/CallMeJones/blender-agent-bridge/blob/main/docs/ADDING_A_TOOL.md?utm_source=chatgpt.com "blender-agent-bridge/docs/ADDING_A_TOOL.md at main · CallMeJones/blender-agent-bridge · GitHub"))

And its testing guide is frankly excellent. It tests gateway reachability, schema lookup, wrapper recursion, prompt/resource pagination, visual artifacts as MCP resources, response sizing, prompt-prefix cache stability, reversible edits, security boundaries, tool-routing behaviour across real models, and regression ownership. ([GitHub](https://github.com/CallMeJones/blender-agent-bridge/blob/main/docs/TESTING_GUIDE.md?utm_source=chatgpt.com "blender-agent-bridge/docs/TESTING_GUIDE.md at main · CallMeJones/blender-agent-bridge · GitHub"))

This is **exactly** the kind of engineering I think you were asking me to look for.

Unfortunately, I wouldn't call it latest-spec yet. Its current testing documentation still tells developers to smoke-test the MCP server by sending an `initialize` request using protocol version `2024-11-05`. MCP 2026-07-28 explicitly removed that handshake. ([GitHub](https://github.com/CallMeJones/blender-agent-bridge/blob/main/docs/TESTING_GUIDE.md?utm_source=chatgpt.com "blender-agent-bridge/docs/TESTING_GUIDE.md at main · CallMeJones/blender-agent-bridge · GitHub"))

So I would treat it as a **design reference or migration candidate**, not the strict answer to your requirement.

## What I would actually put in your stack

For **Godot**, I'd use **hybridindie/godot-mcp** without much hesitation. It has both the protocol foundation and the agent-interface design I want.

For **Blender**, I'd currently use **minihellboy/claude-blender**, but I'd keep **Blender Agent Bridge** open beside it as the architecture to converge toward. In fact, the ideal Blender server right now is almost:

**minihellboy's MCP v2 protocol layer + CallMeJones's registry/gateway/contracts/evidence architecture.**

That's also a useful benchmark for Eco/ACF-style tooling: **don't confuse capability count with agent affordance quality**. HybridIndie's gated toolsets and CallMeJones's search/schema/invoke gateway are two strong solutions to the same underlying problem—give the agent a large operational surface without forcing the model to reason over the whole surface on every turn. ([GitHub](https://github.com/hybridindie/godot-mcp?utm_source=chatgpt.com "GitHub - hybridindie/godot-mcp: Combination of Godot Addon and MCP server for AI driven development · GitHub"))

One project I **wouldn't** choose despite initially liking it is NPGameDev's Godot MCP Toolkit. Its tool discovery, token-budget work, security and tests are strong, but its bridge currently pins the old `@modelcontextprotocol/sdk` 1.x line rather than the v2 server package. Given your requirement, that knocks it out.

If you want, I can go one level deeper next and **rip apart the architecture of these four repos specifically**, then derive what an ideal Blender/Godot MCP interface should look like—tool taxonomy, resources, prompts, screenshots/vision feedback, undo semantics, discovery and agent SOP. That comparison would probably be more useful than just choosing a repo.
