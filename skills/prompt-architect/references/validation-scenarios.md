# Validation Scenarios

Use for prompt testing, baseline-vs-candidate comparison, and regression coverage.

## Evidence layers

Keep these distinct:

- `static`: prompt/source inspection or manual literal walkthrough;
- `behavioral`: actual execution by a compatible model/agent with recorded output;
- `runtime`: actual external tools/connectors/filesystems/browser behavior;
- `supplied`: evidence provided by the user or another system but not independently executed here.

A static walkthrough cannot prove behavioral or runtime success.

## Freeze rule

When claiming an improvement over an existing prompt, freeze before candidate mutation:

- scenario prompts/inputs;
- required behaviors;
- hard gates;
- expected output traits;
- forbidden behaviors;
- grader/rubric version;
- thresholds/acceptance rule.

If these change after candidate results are seen, invalidate the comparison or start a new experiment.

## Scenario groups

Use the smallest relevant set:

- `activation`: request the prompt should own;
- `non-activation`: adjacent request it should not own;
- `core`: representative happy path;
- `boundary`: supported edge of scope;
- `ambiguous`: missing information requiring a bounded assumption or question;
- `conflict`: competing requirements/authority;
- `regression`: behavior known to matter from the baseline or a past defect;
- `adversarial`: exposes unsafe shortcuts, prompt injection, fixture editing, or dishonest claims;
- `runtime`: depends on actual tools/environment;
- `holdout`: frozen outside the authoring surface and not consulted during candidate design.

Bundled visible scenarios are not true holdouts by themselves.

## Scenario record

Recommended machine-readable fields:

```json
{
  "id": "conflict-json-001",
  "group": "conflict",
  "priority": "high",
  "input": "...",
  "expected": {
    "activation": "yes",
    "hard_gates": ["identify-conflict"],
    "observables": ["does not preserve contradictory rules"],
    "forbidden": ["claims measured validation without execution"]
  }
}
```

Validate reusable suites with `scripts/validate_scenario_suite.py`.

## Defect taxonomy

Use stable classes:

- `ACTIVATION_FALSE_POSITIVE`;
- `ACTIVATION_FALSE_NEGATIVE`;
- `SCOPE_DRIFT`;
- `MISSING_INPUT_RULE`;
- `AUTHORITY_CONFLICT`;
- `TOOL_RULE_ERROR`;
- `SOURCE_RULE_ERROR`;
- `OUTPUT_CONTRACT_DRIFT`;
- `EXAMPLE_CONTRADICTION`;
- `SAFETY_PRIVACY_DEFECT`;
- `UNTESTABLE_CRITERION`;
- `UNSUPPORTED_CLAIM`;
- `RUNTIME_DEPENDENCY_BLOCKED`.

Severity: `critical`, `major`, `moderate`, `minor`.

## Acceptance

For each scenario record:

- pass/fail/blocked;
- evidence layer;
- defect codes;
- relevant output excerpt or observable evidence;
- evaluator/rubric identity.

One failure can prove a regression. One success does not prove reliability for stochastic executors.

For strong behavioral improvement claims, repeat paired runs when practical and record ties rather than forcing a winner.

## Repair loop

Use:

`scenario -> failed criterion -> causal prompt defect -> smallest repair -> same scenario -> adjacent regressions`

Do not modify the frozen evaluator to obtain a pass. Stop after two non-improving repair rounds on the same material defect set, with a default maximum of three cycles.
