The next vertical slice should be **one complete capability round-trip through the real MCP server using a fake host**.

Not Blender. Not Godot. Not transport yet.

The purpose is to make the architectural spine real before either engine starts exerting pressure on it.

I’d define the slice as:

```text
MCP client
   ↓
server/discovery
   ↓
catalog search
   ↓
capability schema
   ↓
invoke
   ↓
HostAdapter
   ↓
FakeHost
   ↓
CapabilityResult
   ↓
evidence/resource reference
   ↓
MCP client
```

The fake capability can be deliberately boring, something like `scene.get_summary`. What matters is that it exercises every abstraction we expect future Blender/Godot capabilities to use.

### What I’d implement

First, establish the canonical domain model.

```text
src/super_mcp/contracts/
├── capability.py
├── invocation.py
├── result.py
├── safety.py
└── evidence.py
```

The important object is something roughly equivalent to:

```python
CapabilitySpec(
    id="scene.get_summary",
    host=HostKind.GENERIC,
    summary="Return a structured summary of the active scene",
    input_model=SceneSummaryInput,
    output_model=SceneSummaryOutput,
    mutation=MutationKind.READ_ONLY,
    evidence=[EvidenceKind.STRUCTURED_STATE],
    requirements=[],
)
```

I would resist making this huge initially. Only encode properties that the first vertical slice actually exercises. The design should be extensible, but we don't need speculative fields for every Blender edge case yet.

Then implement the registry/catalog:

```text
src/super_mcp/catalog/
├── registry.py
├── search.py
└── models.py
```

It should support only three meaningful operations initially:

```text
register(capability)
search(query/filter)
get(capability_id)
```

This becomes the source of truth for capability discovery. There should be no duplicated tool metadata hidden inside the MCP registration layer.

Then define the host boundary:

```text
src/super_mcp/hosts/
├── base.py
├── router.py
└── fake.py
```

Something conceptually like:

```python
class HostAdapter(Protocol):
    async def invoke(
        self,
        capability: CapabilitySpec,
        request: CapabilityRequest,
    ) -> CapabilityResult: ...
```

The fake host should behave like a real host rather than just returning `"ok"`.

For example, give it deterministic fake state:

```text
Scene
├── Camera
├── KeyLight
└── Cube
```

Calling `scene.get_summary` returns structured state from that model. That lets contract tests assert actual semantics rather than merely asserting that function A called function B.

### Then expose the smallest MCP surface

This is where I’d be quite strict.

Do **not** expose twenty placeholder tools.

Start with something close to:

```text
super_status
super_search_capabilities
super_get_capability
super_invoke
```

Potentially even three if status belongs naturally in resources/discovery.

The exact names aren't important yet. The properties are.

`search_capabilities("scene summary")` should return a lightweight descriptor, not the entire JSON schema.

Then:

```text
get_capability("scene.get_summary")
```

returns the full typed contract.

Then:

```text
invoke(
    capability="scene.get_summary",
    arguments={}
)
```

validates against that contract before the host sees anything.

That gives us the architecture we liked in Blender Agent Bridge:

```text
search
  ↓
inspect schema
  ↓
invoke
```

without inheriting its legacy protocol layer.

### Make resources real in this slice too

I wouldn't postpone resources.

Have the fake host expose something like:

```text
super://hosts
super://hosts/fake
super://hosts/fake/scene
```

Then the capability result can reference:

```json
{
  "capability": "scene.get_summary",
  "status": "success",
  "data": { ... },
  "resources": [
    "super://hosts/fake/scene"
  ]
}
```

That establishes an important distinction early:

**tools cause/query operations; resources provide addressable state.**

Otherwise there's a real risk that we gradually turn every read operation into another tool.

### Evidence should also appear now, but minimally

For this first slice, evidence doesn't need images.

Give the fake host a structured evidence artifact:

```text
Evidence
├── kind: structured_state
├── before: null
├── after: scene snapshot
├── source: fake
└── resource: super://...
```

That gives `CapabilityResult` somewhere to put future:

```text
Blender render
Godot viewport screenshot
compiler diagnostics
runtime logs
scene-tree diff
geometry statistics
before/after captures
```

without having to retrofit the result model later.

This matters because I want one foundational invariant to emerge very early:

> **An invocation reports both what happened and what evidence exists for believing it happened.**

That will become extremely valuable once agents start operating visually.

### Error semantics belong in this slice

I'd also deliberately test:

```text
unknown capability
invalid arguments
host unavailable
capability unsupported by selected host
host execution failure
timeout/cancellation
```

Not necessarily full timeout infrastructure yet, but the canonical result/error model needs to distinguish these.

The model should be able to tell the difference between:

```text
"I requested something invalid"
```

and

```text
"the Godot editor disconnected while executing a valid operation"
```

without parsing strings.

### The tests are actually the output of this slice

The main artifact I'd care about is a contract suite like:

```text
tests/contract/
├── test_discovery.py
├── test_capability_schema.py
├── test_invocation.py
├── test_resources.py
└── test_errors.py
```

The critical test should effectively read:

```python
async def test_full_capability_round_trip():
    client = ...

    results = await client.search_capabilities("scene summary")
    assert "scene.get_summary" in results

    schema = await client.get_capability("scene.get_summary")
    assert schema.mutation == "read_only"

    result = await client.invoke("scene.get_summary", {})

    assert result.status == "success"
    assert result.data["object_count"] == 3
    assert result.evidence
    assert result.resources

    scene = await client.read_resource(result.resources[0])
    assert ...
```

That's the first genuinely meaningful milestone.

## I would stop the slice there

No Blender WebSocket.

No Godot editor plugin connection.

No screenshots.

No undo manager.

No semantic search embeddings.

No arbitrary Python/GDScript execution.

No giant capability taxonomy.

Once this works, the next two vertical slices become wonderfully boring:

```text
Slice 2A
FakeHost → BlenderHost
scene.get_summary → actual Blender scene

Slice 2B
FakeHost → GodotHost
scene.get_summary → actual Godot scene tree
```

The MCP client shouldn't know which implementation it's talking to.

And after that:

```text
read-only state
    ↓
visual evidence
    ↓
reversible mutation
    ↓
preview / undo
    ↓
agent workflow
    ↓
capability breadth
```

That's the foundation I'd want before we let the project fan out. It forces us to prove **protocol → discovery → contract → routing → execution → evidence → resource** as one coherent system while the problem is still small enough to change cheaply.

The response has a strong instinct—prove the spine before capability breadth—but I think it makes **one major architectural mistake**: it calls something a vertical slice while deliberately avoiding the parts most likely to invalidate the architecture.

The fake-host round trip is useful, but it should not be the *next vertical slice*. It is closer to a **contract harness**.

The biggest problems I see:

1. **The fake host can validate our abstractions without validating their assumptions.**
   We can make `CapabilitySpec → HostAdapter → FakeHost → CapabilityResult` beautifully coherent because we control every side of that interaction. Blender and Godot are exactly what will tell us whether `HostAdapter`, capability identity, cancellation, resource addressing, undo, threading, project identity, and evidence semantics are shaped correctly. Avoiding both engines means the slice cannot expose those mistakes.

2. **`scene.get_summary` contradicts the resource philosophy in the same proposal.**
   The response says:

   > tools cause/query operations; resources provide addressable state.

   Then its foundational capability is a read-only operation whose only purpose is to return scene state, after which it also points at `super://hosts/fake/scene`.

   That's duplicate semantics.

   Either:

   ```text
   resources/read super://hosts/blender/scene
   ```

   is the way an agent observes a scene,

   or:

   ```text
   invoke("scene.get_summary")
   ```

   is.

   Making both foundational guarantees we'll spend time later deciding which is canonical.

3. **It risks inventing a second protocol inside MCP.**
   `search_capabilities → get_capability → invoke` is effectively our own RPC/capability protocol carried through four MCP tools.

   That may ultimately be justified—CallMeJones's Blender design is evidence that bounded tool discovery can be valuable—but we haven't yet demonstrated that it needs to be the universal architecture.

   MCP 2026-07-28 already gives us `server/discover` for protocol/server capability discovery, normal `tools/list`, `resources/list`, `prompts/list`, structured results, and cacheable stateless list operations. `server/discover` is mandatory for servers, although clients don't have to call it first. ([GitHub][1])

   We need to distinguish clearly between:

   ```text
   MCP protocol discovery
   ```

   and:

   ```text
   our application-level engine capability catalog
   ```

   The previous response blurred those concepts by putting `server/discovery` directly above our catalog search.

4. **It prematurely assumes Blender and Godot should share semantic capabilities.**
   This is the line I'd be most suspicious of:

   > The MCP client shouldn't know which implementation it's talking to.

   Why not?

   Blender and Godot overlap in concepts like scenes, nodes/objects, materials and transforms, but they are not interchangeable hosts.

   Forcing:

   ```text
   scene.get_summary
   ```

   across both may lead us toward a lowest-common-denominator abstraction.

   A healthier model may be:

   ```text
   common protocol envelope
   common discovery/safety/evidence vocabulary

   blender.scene.inspect
   godot.scene.inspect
   ```

   with convergence only where semantics genuinely match.

   **Shared infrastructure does not imply shared domain ontology.**

5. **`HostAdapter.invoke(CapabilitySpec, CapabilityRequest)` is suspiciously generic.**
   It looks elegant because everything becomes one dispatcher.

   But it can easily become:

   ```text
   string capability id
       +
   bag of JSON
       +
   enormous switch statement
   ```

   hidden behind Python types.

   We should instead make the registry carry typed handlers, so the genericity exists at registration/routing boundaries rather than infecting implementation:

   ```python
   Capability[InspectSceneInput, InspectSceneResult]
       -> registered handler
       -> BlenderInspectSceneHandler
   ```

   The actual host code should retain useful static structure.

6. **The evidence model is being designed before we know what evidence actually looks like.**
   This:

   ```text
   Evidence
   ├── kind
   ├── before
   ├── after
   ├── source
   └── resource
   ```

   feels plausible, but it is speculative.

   A Blender render, Godot debugger diagnostic, scene-tree diff, compiler error and viewport capture have radically different lifecycle and storage characteristics.

   The safer first abstraction is probably just:

   ```text
   ArtifactRef
   ```

   with:

   ```text
   media type
   URI
   provenance
   optional semantic role
   ```

   Let actual workflows teach us whether "Evidence" deserves a richer common model.

7. **Timeout/cancellation is listed as an error case without exercising a boundary where it matters.**
   A fake in-process adapter cannot meaningfully teach us about:

   * Blender main-thread dispatch;
   * Godot editor scheduling;
   * host process death;
   * socket disconnect;
   * request cancellation arriving during engine work.

   Testing a fake `HostUnavailableError` proves the enum exists, not that the architecture survives failure.

8. **It underuses a major property of MCP 2026-07-28: statelessness.**
   The newest revision removed initialization/session state; protocol version and client capabilities travel with each request, and cross-call application state must be explicit rather than smuggled through protocol sessions. ([GitHub][2])

   That's a foundational constraint for our bridge architecture.

   The proposed slice should have explicitly asked:

   > What state belongs in MCP requests, what belongs in host identity/resource URIs, and what requires a server-minted handle?

   That's more important right now than an elaborate `CapabilityResult`.

---

## I would change the next slice

I'd make it a **real observation slice**, with a tiny contract harness underneath it.

Something like:

```text
MCP 2026-07-28 request
        ↓
shared server
        ↓
host registry
        ↓
real Blender bridge
        ↓
inspect active scene
        ↓
structured resource/result
        ↓
MCP client
```

And then repeat the exact infrastructure with Godot immediately afterward.

Not mutation yet.

Not hundreds of capabilities.

Not even capability search yet.

Just prove:

```text
server identity
host discovery
host connection
real request routing
real engine-thread execution
structured observation
resource addressing
host failure
```

### Slice 1A — Blender

One real operation:

```text
blender://scene
```

returns:

```text
document identity
Blender version
scene name
object count
object names/types
active object
camera
```

The Blender add-on has to establish the actual bridge and safe main-thread dispatch.

That single feature will force us to answer questions the fake host cannot.

### Slice 1B — Godot

Then:

```text
godot://scene
```

returns:

```text
project identity
Godot version
edited scene path
root node
node count
node names/types
selected nodes
```

The Godot plugin has to establish editor lifecycle and bridge behavior.

Now we compare what actually generalized.

---

Only **after those two** would I formalize:

```text
HostAdapter
CapabilitySpec
Evidence
generic scene vocabulary
capability discovery gateway
```

where the similarities are demonstrated rather than imagined.

We still absolutely want a fake host—but I'd build it **after or alongside the first real host contract**, as the deterministic test implementation of a contract learned from reality.

That reverses the epistemology:

```text
previous proposal

invent abstraction
    ↓
make fake implementation satisfy it
    ↓
hope Blender/Godot fit
```

versus:

```text
better

exercise real host
    ↓
exercise second real host
    ↓
identify stable common boundary
    ↓
codify contract
    ↓
create fake implementation for tests
```

The second path is more resistant to framework-building for its own sake.

The strongest part of the original response remains the restraint around capability breadth. I would keep that completely. The mistake was applying the same restraint to **host reality**. For this project, Blender and Godot aren't implementation details beneath the architecture—they are the primary sources of truth that should shape it.

[1]: https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2026-07-28/server/discover.mdx?utm_source=chatgpt.com "modelcontextprotocol/docs/specification/2026-07-28/server/discover.mdx at main · modelcontextprotocol/modelcontextprotocol · GitHub"
[2]: https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/blog/content/posts/2026-07-28-spec-ga/index.md?utm_source=chatgpt.com "modelcontextprotocol/blog/content/posts/2026-07-28-spec-ga/index.md at main · modelcontextprotocol/modelcontextprotocol · GitHub"