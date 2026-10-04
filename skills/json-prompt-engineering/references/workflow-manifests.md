# Workflow Manifests for Skills and Tools

## Purpose

A workflow manifest declares requested orchestration. It does not activate, authorize, or execute capabilities by itself. An executor must resolve identifiers, enforce authority, validate inputs/outputs, manage state, and persist evidence.

## Step contract

```json
{
  "id": "planning",
  "capability": "mago",
  "action": "define_spec",
  "instruction": "Produce the technical planning package.",
  "depends_on": ["governance"],
  "input": {"source": "$.results.intake"},
  "output": {
    "key": "spec",
    "contract": "mago-spec-v2"
  },
  "authority": {"side_effect": "write-owned-artifact"}
}
```

`skill` may be used instead of `capability` when the executor specifically resolves Agent Skills. Do not copy a permanent skill/tool prompt into `instruction`.

## Required mechanics

Validate deterministically where possible:

- known workflow/schema versions;
- unique step IDs;
- dependencies exist and are acyclic;
- declared capability/action is resolvable and allowlisted;
- handoff contract identities are compatible;
- output keys do not collide unexpectedly;
- retry, timeout, parallelism, and recursion are bounded;
- authority/side-effect requirements are permitted;
- model-generated state cannot silently expand execution authority.

## Execution modes

- `sequential`: declared array order is execution order.
- `dependency_graph`: a step is eligible only after all dependencies complete successfully according to policy.
- `parallel`: only for independent steps with explicit bounded concurrency.

Never rely on JSON object-property order for execution.

## Ownership

Keep artifact ownership explicit and reject cross-owner writes unless the governing policy authorizes them. Ownership declarations describe allowed mutation surfaces; they do not grant user authorization by themselves.

## Handoff contracts

A handoff should name its contract/version rather than embed an unversioned example. Validate producer and consumer expectations separately. When the handoff crosses provider/tool surfaces, keep the canonical contract distinct from any provider projection.

## State and evidence

Persist concise machine-readable state and enough human-readable evidence to review failures. Distinguish requested state, model-proposed state, validated state, and committed execution state.
