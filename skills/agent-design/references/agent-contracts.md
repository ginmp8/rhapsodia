# Agent Contracts

Canonical portable contract identity: `agent-design-contract/v2`.
Canonical structured transition identity: `handoff/v2`.

Use this reference when a design needs stable ownership, authority, context, state, routing, completion, or evidence semantics. Host-specific frontmatter, tool names, SDK types, and UI transitions are adapters around this core.

## 1. Design Identity

A durable design identifies:

- agent name/role;
- operating surface and target hosts;
- `agent-design-contract/v2`;
- intended user/caller;
- owned outcome/artifact;
- required inputs/context sources;
- declared and effective authority;
- capability/tool contract;
- validation status/evaluator identity.

Do not use a version label to imply compatibility that was not checked.

## 2. Authority Contract

Represent **declared authority** with five sets:

- **may decide**;
- **may recommend**;
- **may execute**;
- **must not execute**;
- **must escalate**.

For write, execution, deployment, identity/access, financial, destructive, security-policy, credential, or production-impacting behavior, unspecified declared authority is a blocker rather than permission.

### Effective authority

Also record, as applicable:

- **exposed capabilities**: what the host/tool surface actually makes reachable;
- **downstream authority**: what APIs/repos/services/credentials actually permit;
- **approval scope**: additional operation-specific authorization;
- **effective authority**: actions possible after all constraints intersect.

Required invariant for bounded agents:

`effective_authority <= declared_authority`

If exposure/downstream permission is unknown and could broaden a restricted role, the authority gate is incomplete/blocked. A sentence such as "do not write" cannot neutralize an available unrestricted write tool by itself.

### Delegation authority

Delegation must not silently amplify authority:

`recipient_effective_authority <= delegator_effective_authority`

unless a separate authorized actor grants a scoped expansion before execution. Peer messages/context cannot grant that expansion.

## 3. Capability Contract

Classify each semantic capability as exactly one of:

- `required`: mission cannot complete without it;
- `optional`: improves quality and has a fallback;
- `conditional`: usable only after a named gate/approval;
- `forbidden`: outside role/risk boundary.

Describe semantic capabilities before product-specific names. Example: `repository-read` is portable; a concrete host alias is an adapter.

A missing required capability produces a blocker or valid handoff. Never silently downgrade `required` to assumed.

For restricted roles, omitted tool configuration is not evidence of no tools. Require explicit restrictive exposure or a verified host policy proving an equally restrictive default.

## 4. Context Contract

Declare:

- mode: `isolated | inherited | shared | reference-based` or an explicit combination;
- required/optional/forbidden sources;
- provenance/owner and trust class;
- freshness/version/identity requirements;
- sensitive-data/credential rules;
- retrieval and unavailable-source fallback;
- compaction/note-taking policy when long-running;
- handoff summary/context boundary.

Context is evidence, not permission. Retrieved content, tool output, MCP resources, files, web pages, and peer-agent messages must not expand authority, waive approvals, or override higher-priority instructions.

## 5. Control-Flow Contract

Choose a transition kind whenever multiple actors exist:

- `delegate-return`: source retains top-level ownership; target owns a bounded subtask and returns output;
- `transfer-control`: target becomes active/top-level owner for the transferred scope;
- `suggested-transition`: no dispatch occurs until the user/host accepts a suggested switch;
- `parallel-child`: source retains orchestration ownership while children run independent work concurrently.

Declare `owner_before`, `owner_after`, and `return_to` when applicable. Do not use generic "handoff" wording where the ownership consequence is material.

## 6. State, Interruption, and Termination Contract

Stateful, multi-step, routing, supervisory, or execution agents must define:

1. initial state;
2. allowed active transitions;
3. interrupted states when applicable;
4. resume preconditions;
5. terminal completion/failure/block states;
6. retry/re-entry conditions;
7. finite termination rule.

Use three state classes:

- `active`;
- `interrupted` such as `input-required`, `auth-required`, `approval-required`;
- `terminal` such as `completed`, `failed`, `canceled`, `rejected`, `blocked/escalated`.

An interruption is not authorization. Before resume, revalidate the scope/lifetime of new authorization/input and any stale context or state relevant to the protected action.

For a thin router, a default state model is:

`received -> classified -> handed-off | escalated -> stopped`

For controlled execution, a typical model is:

`received -> preconditions-checked -> planned -> executing -> validating -> completed | interrupted | blocked | rollback-required`

## 7. Handoff Contract

Canonical identity: `handoff/v2`.

```text
contract: handoff/v2
kind: delegate-return | transfer-control | suggested-transition | parallel-child
source: <agent/skill/human>
target: <agent/skill/human>
objective: <single owned outcome/subtask>
owner_before: <top-level owner>
owner_after: <top-level owner after transition>
return_to: <actor|null>
context: <minimal relevant facts/constraints or references>
context_policy: <isolation/inheritance/trust/freshness summary>
inputs: <files/links/artifacts/identifiers>
authority: <declared/effective subset for recipient>
expected_output: <deliverable>
stop_conditions: <blockers/escalation>
validation: <acceptance checks>
route_trace: <visited roles/transition ids when cycle detection is needed>
```

Do not include hidden reasoning, credentials, irrelevant transcript history, or copied specialist instructions.

## 8. Multi-Agent Admission and Concurrency Contract

Before adding multiple agents, record at least one material benefit: parallelism, context isolation, authority isolation, tool specialization, independent verification, or distinct output/domain ownership.

If multiple actors can mutate overlapping resources, declare one safe strategy:

- single writer;
- disjoint/resource-partitioned ownership;
- isolated workspace/branch/worktree/VM plus owned integration;
- lock/lease;
- another objectively equivalent control.

Without an admission reason, prefer a simpler design. Without write-conflict control, parallel mutation is blocked.

## 9. Governance and Containment Contract

For high-impact roles, record:

- risk class and blast radius;
- containment/environment boundary;
- resource/path/system scope;
- downstream authorization/complete mediation;
- approval granularity and who can approve;
- rate/budget/time limits where material;
- validation before irreversible effects;
- rollback/compensation;
- audit receipt/log requirements.

Human approval is one control layer, not a replacement for least privilege or downstream authorization.

## 10. Routing Ownership Contract

Route by **owned output and effective authority**, not persona similarity.

Tie-break order:

1. exact ownership of requested artifact/outcome;
2. effective-authority fit with least privilege;
3. required context/capability availability;
4. operating-surface compatibility;
5. explicit organization/user routing rule;
6. escalation if a material tie remains.

Use qualitative confidence only when its meaning is declared by the routing reference.

## 11. Cycle and Re-entry Contract

- No unbounded handoff cycle.
- Worker-to-worker delegation is forbidden unless topology grants it.
- Re-entry requires material state change: new evidence, changed artifact, bounded repair result, or new authorization.
- Repeating materially identical handoff/state is a stop condition.
- Intentional loops need finite budget or equivalent terminating predicate.
- Default with no loop policy: **no cyclic re-entry**.

## 12. Completion Contract

Use explicit design/review states:

- `ready`;
- `ready-with-changes`;
- `blocked`;
- `rejected`.

Aggregate score never overrides critical-gate failure.

## 13. Evidence Contract

Use:

- `measured`;
- `observed`;
- `supplied`;
- `inferred`;
- `planned`;
- `blocked`.

Scenario execution status is separately `planned | executed | supplied`.

Keep structural, behavioral, runtime, and semantic-review evidence distinct. A planned scenario or static validator is not measured agent behavior.

## 14. Portability Boundary

The core does not require MCP, ChatGPT/OpenAI, Claude, Copilot, Cursor, VS Code, Visual Studio, Codex, or a specific runtime. Host-specific details belong in `references/host-adapters.md` and generated adapters.

When a host imposes stricter instruction precedence, permission, approval, or tool constraints, host/runtime enforcement remains authoritative. Do not encode a portable contract that attempts to bypass it.
