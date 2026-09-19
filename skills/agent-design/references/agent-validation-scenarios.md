# Agent Validation Scenarios

Use this reference to design repeatable validation for agent behavior. The bundled frozen planning suite is `evals/agent-design-scenarios.json`. Its presence is **planned evidence**, not proof that an LLM behavior run occurred.

## Scenario Groups

Cover materially distinct behavior:

1. `activation`: the agent-design capability should own the request.
2. `non-activation`: another Skill, agent, repository workflow, or human owns it.
3. `ambiguous`: safe defaults, a bounded question, or escalation is required.
4. `core`: representative high-value design/routing behavior.
5. `edge`: boundary, missing-tool, missing-context, partial-failure, or authority-edge cases.
6. `regression`: a known defect or failure mode that must stay observable.
7. `adversarial`: attempts to bypass controls, hide evidence, overreach authority, or create uncontrolled loops.
8. `holdout`: cases reserved from normal authoring when a real comparative evaluation is run.

Prefer a small set of behaviorally distinct cases over many paraphrases.

## Scenario Record

Recommended machine-readable fields:

```json
{
  "id": "regression-circular-handoff",
  "group": "regression",
  "prompt": "...",
  "expected": {"activate": true, "mode": "agent-routing-design"},
  "must": ["define termination behavior"],
  "must_not": ["allow an unbounded cycle"],
  "evidence_status": "planned"
}
```

Scenario execution status is one of:

- `planned`: defined but not run;
- `executed`: run in the current evaluation with captured output/evaluator evidence;
- `supplied`: result supplied by another actor and not independently executed here.

## Claim Evidence Labels

When reporting validation results, use:

- `measured`: produced by an executed command, scenario harness, or runtime check;
- `observed`: directly inspected in an artifact/source;
- `supplied`: provided externally;
- `inferred`: reasoned from evidence;
- `planned`: specified but not executed;
- `blocked`: unavailable.

Do not convert `planned`, `supplied`, or `observed` evidence into `measured` merely because the design looks correct.

## Frozen Comparison Rule

For baseline-vs-candidate behavioral claims:

1. freeze prompts, expected invariants, evaluator criteria, and relevant input files before candidate mutation;
2. run the same frozen cases against both arms;
3. keep holdout cases unchanged after results are seen;
4. repeat stochastic cases when a strong reliability claim requires it;
5. record ties/failures rather than forcing a winner;
6. invalidate the comparison if the evaluator changes.

A static package audit, rubric score, or scenario file does not demonstrate behavioral improvement.

## Default Acceptance Invariants

An agent design should, where applicable:

- activate or route according to owned outcome;
- stay within declared authority;
- use only allowed capabilities or state the missing dependency;
- produce the declared output contract;
- define stop/escalation behavior;
- define termination/re-entry behavior for stateful or routing systems;
- keep routers from specialist execution;
- use compact handoffs without duplicated specialist prompts;
- preserve evidence labels;
- avoid claiming unexecuted runtime or behavioral validation.

## Structural Validator

When a generated agent artifact is available as a file, run:

```text
<PYTHON> scripts/validate_agent_artifact.py <ARTIFACT> --kind auto --profile <PROFILE> --json <RECEIPT>
```

Profiles are `generic`, `router`, `review`, `governance`, or `controlled-executor`. Use `--require-complete` for final artifacts to reject unresolved template placeholders. Read-only profiles reject obvious write-capable tools unless `--allow-write-tools` is explicitly justified.

This validator proves structural invariants only. Semantic quality still requires rubric/scenario review, and actual tool behavior requires runtime evidence.

## Validation Plan Output

```markdown
# Agent Validation Plan

## Scope
...

## Frozen Inputs/Evaluator
- scenario suite identity:
- evaluator identity:
- baseline/candidate arms:

## Scenario Matrix
| Scenario | Group | Expected behavior | Acceptance criteria | Evidence status |
|---|---|---|---|---|

## Critical Gates
- mission/ownership:
- authority:
- tool least authority:
- stop/escalation:
- state/termination:
- evidence truthfulness:

## Not Measured
List behaviors or metrics that were not executed.
```
