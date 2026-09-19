# Prompt Contract

Use a prompt contract when the target is complex, governed, reused, or compared across revisions. The contract is a semantic ledger; it is not the final prompt.

## Contract goals

The contract should make these stable before wording is optimized:

- target identity;
- intended executor;
- mode;
- available inputs/tools;
- protected requirements;
- output contract;
- success criteria;
- assumptions/conflicts;
- validation identity and claim level.

Use [`assets/templates/prompt-contract.json.template`](../assets/templates/prompt-contract.json.template) as the canonical scaffold and validate it with `scripts/validate_prompt_contract.py`.

## Requirement authority

Allowed authority values:

- `explicit`: directly required by the user/current task;
- `source-required`: required by an authoritative source or compatibility contract;
- `inferred`: derived from context but not explicitly stated;
- `optional`: design preference or nonessential enhancement.

Protected requirements may not be removed or semantically weakened without higher authority. If a protected requirement conflicts with another protected requirement at the same authority level, record the conflict rather than guessing.

## Requirement states

- `preserve`: semantic behavior must stay;
- `clarify`: semantics stay, wording/placement may change;
- `change`: behavior intentionally changes with reason/evidence;
- `remove`: intentionally removed with authority/reason;
- `blocked`: unresolved conflict or missing authority.

## Output contract fields

Capture only fields material to correctness:

- `format`;
- `sections` or schema identity;
- `language`;
- `length` when bounded;
- `citations`;
- `ordering`;
- `unknown_or_error_behavior`.

## Validation block

`validation.freeze_state` values:

- `frozen`: evaluator/scenarios were fixed before candidate mutation;
- `planned`: assets exist but are not executed/frozen evidence;
- `not-applicable`: no behavioral comparison is being claimed.

`validation.claim_level` values:

- `structural`;
- `behavioral`;
- `runtime`.

A `behavioral` claim requires a frozen baseline-vs-candidate evaluator. A `runtime` claim requires actual execution by the intended executor/tool environment.
