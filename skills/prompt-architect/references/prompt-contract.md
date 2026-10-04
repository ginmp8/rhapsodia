# Prompt Contract v2

Use the machine-readable prompt contract for reusable, complex, or comparison-sensitive work. It separates semantic requirements from executor/runtime assumptions so the same behavior can be rendered for multiple hosts without pretending the text is universal.

Canonical scaffold: [`../assets/templates/prompt-contract.json.template`](../assets/templates/prompt-contract.json.template).

## Core sections

### `target`

Logical artifact identity: name, kind, executor, and language.

### `solution_lever`

Records the selected control lever and whether prompt engineering is primary. Allowed values:

`prompt`, `model`, `context`, `tool-schema`, `application-control`, `fine-tuning`, `architecture`, `mixed`, `undetermined`.

A non-prompt lever may still include a prompt artifact, but the contract must not claim prompt text controls behavior owned elsewhere.

### `execution_profile`

Captures provider/host/model/snapshot/configuration, active instruction surfaces, capability states, and a profile identity when material. Structural work may use explicit `unknown` values. Behavioral/runtime claims require a stable non-empty `profile_identity`.

### `authority_and_trust`

Keep separate:

- design-authority precedence;
- runtime instruction authority description;
- untrusted-data policy.

### `inputs.context`

Captures stable/dynamic/untrusted context plus budget, placement, overflow, and provenance behavior.

### `requirements`

Each requirement includes:

- stable id/text;
- authority;
- protected flag;
- source/status/reason;
- `control_class`;
- `enforcement`.

Authorization, security, and side-effect controls cannot claim `prompt` as their sole enforcement layer.

### `validation`

Records suite/freeze/claim level, execution-profile identity, and optional comparison controls.

Behavioral/runtime claims require:

- `freeze_state=frozen`;
- non-empty `suite_id`;
- non-empty `execution_profile_identity` matching the execution profile.

For material pairwise `llm-judge` comparison, v2 requires blinding, position swap, at least two repetitions, and ties allowed. Use another evaluator kind when those controls do not apply.

## Version policy

Version 2 is the current contract. Do not silently coerce obsolete v1 contracts; migrate them explicitly so missing execution/enforcement semantics remain visible.

## Validation

Run:

```text
<PYTHON> scripts/validate_prompt_contract.py <CONTRACT_JSON>
```

A pass proves contract shape and declared invariants only. It does not prove that the prompt behaves correctly on a model/runtime.
