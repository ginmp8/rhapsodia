# Activation Scenario Design

Use `evals/activation-scenarios.json` as the canonical candidate-visible regression/calibration suite and `references/activation-contract.md` for routing semantics.

## Scenario groups

- `activation`: owned positive cases;
- `non-activation`: negative cases split into `alternative-owner` and `abstain`;
- `ambiguous`: missing-context cases that should not be forced into binary routing;
- `boundary`: mixed-scope/ownership cases exercising constrained activation or split handoff;
- `adversarial`: attempts to bypass authority, evaluator, evidence, or anti-gaming rules;
- `regression`: candidate-visible realistic cases retained to detect future regressions.

Do not call bundled regression cases blind holdouts. True blind holdouts must remain outside candidate-visible inputs under evaluator-only control.

## Required routing dimensions

Each scenario declares:

- `invocation_mode`: `explicit`, `implicit`, or `contextual`;
- `measurement_scope`: `direct-usage`, `auto-routing`, `boundary-routing`, `policy-resistance`, or `regression`;
- `dimensions.language`;
- `dimensions.context_profile`: `clean`, `noisy`, or `long`;
- `dimensions.input_style`: `terse`, `conversational`, or `typo`;
- `dimensions.intent_profile`: `single` or `multi-intent`.

The canonical suite should include all invocation modes plus at least one non-English case, noisy/typo case, long-context case, and multi-intent case. These are coverage dimensions, not separate quality scores.

## Negative cases

For every `non-activation` scenario declare:

- `negative_kind=alternative-owner` and `neighbor_owner=<capability-role>` when another workflow should win; or
- `negative_kind=abstain` when no relevant skill should activate.

Near-miss alternatives should resemble the target skill semantically. Do not rely only on obviously unrelated negatives.

## Activation-gaming adversaries

Include cases that request the reviewer to:

- remove stop/non-trigger conditions to increase activation;
- claim priority over every prompt-related skill;
- add keyword stuffing or promotional wording to beat neighboring descriptions;
- edit frozen expected outcomes/evaluators after seeing failures;
- fabricate a behavioral pass without executing routing.

Expected handling is rejection of the unsafe/evidence-weakening change while preserving the legitimate review role.

## Scenario quality rules

- Write realistic user language, not contract paraphrases.
- Give every case a stable `id`.
- Tie each case to one or more contract IDs.
- Freeze prompts/expectations before baseline execution.
- Never alter a failed expectation after candidate output is observed.
- Exclude ambiguous/conditional cases from binary precision/recall unless the evaluator predeclares a binary expectation.
- Prefer semantic diversity over duplicate paraphrases.
- Treat explicit invocation as direct-use evidence, never automatic-discovery evidence.

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
  "visibility": "candidate-visible",
  "invocation_mode": "contextual",
  "measurement_scope": "boundary-routing",
  "dimensions": {
    "language": "en",
    "context_profile": "clean",
    "input_style": "conversational",
    "intent_profile": "single"
  }
}
```

## Evidence labels

A scenario/result can be:

- `planned` — authored but not run;
- `supplied` — externally supplied execution evidence;
- `executed` — actually run in the current workflow;
- `blocked` — execution unavailable or invalid.

Presence in a scenario file is not execution evidence.
