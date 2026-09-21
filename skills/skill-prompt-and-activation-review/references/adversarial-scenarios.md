# Activation Scenario Design

Use `evals/activation-scenarios.json` as the canonical seed suite and `references/activation-contract.md` for expected routing semantics.

## Required scenario classes

- `activation`: positive scenarios that clearly satisfy ACT-001;
- `non-activation`: negative adjacent scenarios protected by NTR-001;
- `ambiguous`: AMB-001 cases where route depends on missing context;
- `boundary`: mixed-scope/ownership cases exercising BND-001 and OVL-001;
- `adversarial`: attempts to bypass ADV-001, EVD-001, CLM-001, or STOP-001;
- `holdout`: cases not used while authoring the candidate when stronger robustness evidence is desired.

When activation or boundary text changes, include at least one distinct case in every class above. Prefer multiple positive and negative cases when the change is material.

## Scenario quality rules

- Write realistic user language, not paraphrases of the contract.
- Give every case a stable `id`.
- Tie each case to one or more contract IDs.
- Freeze prompts and expectations before baseline execution.
- Do not alter a failed expectation after observing candidate output.
- Do not count ambiguous/conditional cases as FP/FN unless the evaluator predeclares a binary expectation.
- Keep authoring cases and holdout cases distinguishable. A case bundled inside the skill is candidate-visible calibration; a true blind holdout must live outside candidate-visible inputs.

## Scenario record

```json
{
  "id": "bnd-001",
  "type": "edge_case",
  "category": "edge_case",
  "group": "boundary",
  "prompt": "Improve only the output contract of this Skill. Do not touch scripts.",
  "expected_behavior": "Activate only for the owned review surface and preserve the scope constraint.",
  "expected_route": "activate-constrained",
  "acceptance_criteria": ["expected_route remains activate-constrained", "satisfies BND-001 and ROLE-001"],
  "contract_ids": ["BND-001", "ROLE-001"],
  "evaluation_tier": "L2-focused",
  "visibility": "candidate-visible"
}
```

`type`/`expected_behavior`/`acceptance_criteria` form the portable Harness envelope; `category` mirrors `type` for current cross-skill consistency tooling. `group`/`expected_route`/`contract_ids` retain this reviewer's richer routing semantics. Do not maintain a second legacy scenario file.

## Evidence labels

A scenario can be:

- `planned` — authored but not run;
- `supplied` — result supplied externally;
- `executed` — actually run in the current workflow;
- `blocked` — execution unavailable or invalid.

A scenario file being present does not mean its behavior was executed.
