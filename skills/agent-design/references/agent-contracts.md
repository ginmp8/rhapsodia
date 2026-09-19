# Agent Contracts

Canonical portable contract identity: `agent-design-contract/v1`.

Use this reference when a design needs stable authority, state, routing, handoff, completion, or evidence semantics. These contracts describe behavior independently from any single host. Host-specific frontmatter, tool names, and runtime APIs are adapters around this core.

## 1. Design Identity

A durable agent design should identify:

- agent name or role;
- operating surface;
- contract identity (`agent-design-contract/v1` unless a newer explicit contract is requested);
- intended user or caller;
- owned outcome/artifact;
- required inputs and context sources;
- tool capabilities and authority boundary;
- validation status.

Do not use a version label to imply compatibility that was not checked.

## 2. Authority Contract

Represent authority with five distinct sets:

- **may decide**: decisions the agent can make without another actor;
- **may recommend**: decisions it can analyze but not finalize;
- **may execute**: concrete actions it may perform;
- **must not execute**: prohibited actions/resources;
- **must escalate**: conditions that require another actor.

If write, execution, deployment, identity/access, financial, destructive, security-policy, or production-impacting behavior is in scope, unspecified authority is a blocker rather than implicit permission.

## 3. Tool Capability Contract

Classify each capability as exactly one of:

- `required`: mission cannot be completed without it;
- `optional`: improves quality but has a defined fallback;
- `conditional`: usable only after a stated gate or approval;
- `forbidden`: outside the role or risk boundary.

Describe capabilities before product-specific tool names when portability matters. Example: `repository-read` is the semantic capability; `read_file` may be one host adapter.

A missing required capability must produce a blocker or a valid handoff. Never silently downgrade a required tool to an assumed tool.

## 4. State and Termination Contract

Any stateful, multi-step, routing, supervisory, or execution agent must define:

1. initial state;
2. allowed state transitions;
3. completion state;
4. blocked/escalated state;
5. retry or re-entry conditions;
6. finite termination rule.

Prefer the smallest state model that makes failure and completion observable. Do not introduce state merely to make the design look agentic.

For a thin router, the default state model is:

`received -> classified -> handed-off | escalated -> stopped`

The router does not continue as the specialist after `handed-off`.

For a controlled executor, a typical model is:

`received -> preconditions-checked -> planned -> executing -> validating -> completed | blocked | rollback-required`

The exact states may differ, but every mutation path needs an observable terminal outcome.

## 5. Handoff Contract

Canonical handoff identity: `handoff/v1`.

A handoff should contain only the context needed by the recipient:

```text
contract: handoff/v1
source: <agent/skill/human>
target: <agent/skill/human>
objective: <single owned outcome>
context: <relevant facts and constraints only>
inputs: <files/links/artifacts/identifiers>
authority: <recipient may/must-not/escalate summary>
expected_output: <deliverable>
stop_conditions: <recipient blockers/escalation triggers>
validation: <acceptance checks>
route_trace: <prior route identifiers or visited roles when cycle detection is needed>
```

Do not include hidden reasoning, credentials, irrelevant transcript history, or full copied specialist instructions.

## 6. Routing Ownership Contract

Routing is based on **owned output and required authority**, not persona similarity.

When multiple targets appear eligible, resolve in this order:

1. exact ownership of the requested artifact/outcome;
2. authority fit with the least privilege needed;
3. required context/tool availability;
4. compatibility with caller and operating surface;
5. explicit user/org routing rule;
6. escalation if a material tie remains.

Do not invent confidence precision. Use qualitative confidence only when its meaning is declared by the routing reference.

## 7. Cycle and Re-entry Contract

A design must not contain an unbounded handoff cycle.

- Worker-to-worker delegation is forbidden unless explicitly part of the topology.
- Re-entry requires a stated reason, such as new evidence, a changed artifact, or a bounded repair result.
- Repeating the same handoff with materially identical state is a stop condition.
- If a workflow intentionally loops, declare a finite iteration/hop budget or an equivalent terminating condition.
- If no loop policy is declared, the portable default is **no cyclic re-entry**.

## 8. Completion Contract

Use explicit completion states:

- `ready`: design contract is complete and applicable hard gates pass;
- `ready-with-changes`: design is usable only after listed non-blocking changes;
- `blocked`: required authority, context, capability, owner, or evidence is missing;
- `rejected`: the requested design would violate a critical boundary and no in-scope safe redesign satisfies the request.

For reviews, map these states to the report vocabulary defined by the rubric; do not infer completion from a high aggregate score alone.

## 9. Evidence Contract

Keep evidence strength explicit:

- `measured`: produced by an executed validator/scenario/runtime check;
- `observed`: directly inspected in an artifact or source;
- `supplied`: provided by the user or another actor and not independently executed;
- `inferred`: reasoned from evidence but not directly observed;
- `planned`: specified but not executed;
- `blocked`: evidence could not be obtained.

Scenario records separately use `planned | executed | supplied` as their execution status.

Never describe a planned scenario as measured validation. Structural validation does not prove semantic quality or real runtime behavior.

## 10. Portability Boundary

The core contract does not require MCP, ChatGPT, Claude, Copilot, Cursor, or a specific agent runtime. Platform-specific details belong in adapters such as frontmatter, repository paths, and concrete tool names.

When a host imposes stricter instruction precedence, security, approval, or tool constraints, the host rules remain authoritative. Do not encode a portable contract that attempts to bypass them.
