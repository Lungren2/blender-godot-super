# Architecture

## System boundary

`blender-godot-super` is one MCP server with two host integrations.

```text
agent / MCP client
        |
        v
+---------------------------+
| shared MCP surface        |
| discovery / resources     |
| prompts / evidence        |
+-------------+-------------+
              |
              v
+---------------------------+
| canonical capability      |
| contracts + routing       |
+-------------+-------------+
              |
       +------+------+
       |             |
       v             v
   Blender host   Godot host
   adapter/bridge adapter/bridge
```

The engine adapters implement capabilities. They do not define the public agent interface independently.

## Model-facing surface

The default surface should stay small even as host capability count grows.

Initial target shape:

1. **status** — server and host availability, versions, active project/document.
2. **catalog search** — semantic or filtered discovery of capabilities.
3. **schema lookup** — canonical contract, safety class, side effects, evidence expectations.
4. **invoke** — execute one capability using a validated canonical request.
5. **evidence** — obtain or inspect verification artifacts when they are not already returned inline.

This is a design target, not a commitment to exact tool names.

The catalog can contain hundreds of host capabilities without advertising hundreds of MCP tools at once.

## MCP primitive ownership

Use the protocol primitives deliberately:

- **Tools** perform bounded operations.
- **Resources** expose addressable, read-oriented host/project state and evidence.
- **Prompts** encode reusable procedures such as inspect → mutate → verify.
- **Structured results** carry machine-readable outcomes and references to evidence.

Do not turn every readable value into a tool.

## Capability contract

A canonical capability should eventually describe at least:

- stable capability id and host;
- summary and search metadata;
- typed input/output schema;
- mutability and safety class;
- preview/dry-run support;
- undo semantics;
- editor/runtime preconditions;
- timeout/cancellation behavior;
- expected evidence;
- version/feature requirements;
- resource references produced or consumed.

The contract is the source of truth. Host code implements it.

## Mutation lifecycle

```text
inspect state
  -> discover capability
  -> inspect contract
  -> preview when meaningful
  -> invoke
  -> capture evidence
  -> evaluate result
  -> continue or undo
```

Mutation success is not equivalent to task success. A successful API call without useful evidence is incomplete where visual, runtime, structural, or compiler validation is available.

## Transport boundary

Transport code owns connection lifecycle, request correlation, cancellation/timeouts, serialization, and host liveness. It does not own capability discovery or public schemas.

## Safety

Safety is capability metadata, not prose hidden in tool descriptions. The first contract pass should distinguish read-only, reversible editor mutation, destructive mutation, filesystem/project mutation, and process/network side effects.
