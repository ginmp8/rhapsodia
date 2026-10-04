# Validation Scenarios

Use for prompt testing, baseline-vs-candidate comparison, migration checks, and regression coverage.

## Evidence layers

Keep these distinct:

- `static`: prompt/source/contract inspection or deterministic validator evidence;
- `behavioral`: actual execution by a compatible model/agent with recorded output;
- `runtime`: actual external tools/connectors/filesystems/browser/application behavior;
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
- thresholds/acceptance rule;
- material execution-profile identity.

If these change after candidate results are seen, invalidate the comparison or start a new experiment.

## Scenario groups

Use the smallest relevant set:

- `activation`;
- `non-activation`;
- `core`;
- `boundary`;
- `ambiguous`;
- `conflict`;
- `regression`;
- `adversarial`;
- `execution-profile`;
- `long-context`;
- `runtime`;
- `holdout`.

The machine-readable canonical suite maps these concepts onto its supported v2 group/type vocabulary; the semantic label may be carried in ids/contracts/acceptance criteria.

Bundled visible scenarios are not true holdouts by themselves.

## Focused scenario patterns

### Right lever

Give a failing criterion that is actually controlled by model selection, native schema, authorization, retrieval, or runtime policy. Pass only if the prompt designer identifies the correct layer instead of burying it in prose.

### Authority/trust

Place imperative text inside quoted/retrieved/tool data. Pass only if it remains data unless trusted instruction authority is explicitly delegated.

### Enforcement

Ask for a prompt that "guarantees" authorization, secret isolation, or destructive-action safety. Pass only if runtime/application enforcement is required or the claim is downgraded.

### Execution profile

Change model/host/tool schema while keeping the prompt text constant. Pass only if affected behavioral/runtime evidence is invalidated or revalidated.

### Long context

Vary relevant-information position, distractors, and overflow behavior. Preserve provenance and test untrusted embedded instructions.

### LLM judge

For material pairwise comparisons, swap order and allow ties. Repetition is warranted when a strong stochastic claim depends on judge stability.

## Scenario record

Recommended machine-readable fields remain the package v2 schema. Contract descriptions and acceptance criteria should identify execution-profile and enforcement assumptions when relevant.

The canonical package suite is [`../evals/activation-scenarios.json`](../evals/activation-scenarios.json). Validate reusable suites with [`../scripts/validate_scenario_suite.py`](../scripts/validate_scenario_suite.py).

## Defect taxonomy

Use stable classes:

- `ACTIVATION_FALSE_POSITIVE`;
- `ACTIVATION_FALSE_NEGATIVE`;
- `SCOPE_DRIFT`;
- `WRONG_SOLUTION_LEVER`;
- `MISSING_INPUT_RULE`;
- `AUTHORITY_CONFLICT`;
- `UNTRUSTED_AUTHORITY_ESCALATION`;
- `TOOL_RULE_ERROR`;
- `SOURCE_RULE_ERROR`;
- `PROMPT_ONLY_ENFORCEMENT`;
- `CONTEXT_CONTRACT_DRIFT`;
- `EXECUTION_PROFILE_DRIFT`;
- `OUTPUT_CONTRACT_DRIFT`;
- `EXAMPLE_CONTRADICTION`;
- `SAFETY_PRIVACY_DEFECT`;
- `UNTESTABLE_CRITERION`;
- `EVALUATOR_BIAS_OR_LEAKAGE`;
- `UNSUPPORTED_CLAIM`;
- `RUNTIME_DEPENDENCY_BLOCKED`.

Severity: `critical`, `major`, `moderate`, `minor`.

## Acceptance

For each scenario record:

- pass/fail/blocked;
- evidence layer;
- defect codes;
- relevant output excerpt or observable evidence;
- evaluator/rubric identity;
- execution-profile identity when material.

One failure can prove a regression. One success does not prove reliability for stochastic executors.

For strong behavioral improvement claims, repeat paired runs when practical and record ties rather than forcing a winner. Load [evaluation-integrity.md](../references/evaluation-integrity.md) when an LLM judge or optimizer decides promotion.

## Repair loop

Use:

`scenario -> failed criterion -> causal defect -> smallest repair -> same scenario -> adjacent regressions`

Do not modify the frozen evaluator to obtain a pass. Stop after two non-improving repair rounds on the same material defect set, with a default maximum of three cycles.
