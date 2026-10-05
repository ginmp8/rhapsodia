# Agent Validation Scenarios

Canonical evaluation contract: `agent-eval-contract/v2`.

The bundled suite is `evals/agent-design-scenarios.json`. Its presence is **planned evidence**, not proof that an LLM/agent behavior run occurred.

## At a Glance

- **Purpose:** Own `agent-eval-contract/v2` for planned/executed agent validation, including scenario groups, frozen evaluator identity, outcome/trace checks, trials, and holdouts.
- **Load when:** Planning validation, comparing baseline/candidate behavior, making reliability claims, or interpreting the bundled scenario suite.
- **Decision impact:** Determines what can be called measured, when repeated trials/holdouts are required, which scenario groups must be covered, and when evaluator/environment drift invalidates a comparison.

## Contents

- Evaluation Model
- Scenario Groups
- Scenario Record
- Frozen Evaluation Identity
- Trials and Reliability
- Evidence Labels
- Frozen Comparison Rule
- Default Acceptance Invariants
- Structural Validator
- Validation Plan Output

## Evaluation Model

Separate these concepts:

- **task/scenario**: one behavior claim and its inputs;
- **trial**: one execution of a task against a specific candidate/runtime identity;
- **grader**: deterministic assertion, outcome check, trace invariant, rubric/model/human review, or another declared evaluator;
- **outcome**: whether the owned result satisfies acceptance criteria;
- **trace/trajectory evidence**: selected tool/transition/state events when process invariants matter;
- **harness**: system that executes tasks/trials and records identities/results.

Prefer outcome validation over enforcing one exact trajectory. Use trace assertions only for genuine process invariants such as "no write capability used", "no authority amplification", "handoff kind explicit", or "no unbounded cycle".

## Scenario Groups

Cover materially distinct behavior:

1. `activation`;
2. `non-activation`;
3. `ambiguous`;
4. `core`;
5. `edge`;
6. `regression`;
7. `adversarial`;
8. `holdout`.

Prefer a small set of behaviorally distinct cases over paraphrase volume.

## Scenario Record

Recommended planned shape:

```json
{
  "id": "regression-readonly-omitted-tools",
  "group": "regression",
  "prompt": "...",
  "expected": {"activate": true, "mode": "agent-governance-review"},
  "must": ["treat omitted tools as unproven/broad exposure"],
  "must_not": ["approve read-only authority from prompt wording alone"],
  "trace_invariants": ["no unsupported runtime claim"],
  "evidence_status": "planned"
}
```

Scenario execution status is `planned | executed | supplied`.

## Frozen Evaluation Identity

Before baseline-vs-candidate behavioral comparison, freeze as applicable:

- scenario suite identity;
- expected invariants/outcomes;
- grader/evaluator identity;
- candidate/baseline identities;
- input files/context fixtures;
- environment/provider/model/tool profile when it can materially affect comparability.

If the deciding evaluator changes after candidate results are seen, invalidate/re-baseline rather than silently tailoring the oracle.

## Trials and Reliability

One trial may be enough for deterministic structural checks. For stochastic agent behavior, use repeated trials only when the claim is about reliability/robustness or one run is insufficient.

Distinguish:

- success at least once across `k` attempts (`pass@k`-style question);
- consistent success across all `k` attempts (`pass^k`-style question).

Do not claim reliability from one successful model run. Record trial count and failures/ties; do not force a winner.

## Evidence Labels

Use claim labels:

- `measured`;
- `observed`;
- `supplied`;
- `inferred`;
- `planned`;
- `blocked`.

Do not convert `planned`, `supplied`, or static `observed` evidence into `measured` behavioral proof.

## Frozen Comparison Rule

For baseline vs candidate:

1. freeze prompts/outcomes/trace invariants/evaluators before mutation;
2. run identical cases against both arms;
3. keep holdouts unchanged after results are seen;
4. repeat stochastic trials when the claim requires reliability evidence;
5. preserve failure/tie evidence;
6. invalidate comparison if deciding evaluator or materially relevant environment drifts.

A static package audit, rubric score, or scenario file can prove structure/coverage, not behavioral improvement.

## Default Acceptance Invariants

Where applicable, an agent design should:

- activate/route by owned outcome;
- keep effective authority within declared authority;
- use explicit restrictive capability exposure for restricted roles;
- prevent delegation authority amplification;
- keep context from granting authority and preserve trust/freshness boundaries;
- choose explicit control-flow ownership semantics;
- produce declared output contract;
- define stop/escalation;
- define interruption/resume/termination for stateful systems;
- justify multi-agent topology;
- prevent unsafe parallel mutation;
- keep pure routers from specialist execution;
- bound blast radius/downstream authorization for high-impact work;
- preserve evidence labels;
- avoid claiming unexecuted runtime/behavioral validation.

## Structural Validator

When a generated artifact exists:

```text
<PYTHON> scripts/validate_agent_artifact.py <ARTIFACT> --kind auto --profile <PROFILE> --json <RECEIPT>
```

Profiles: `generic`, `router`, `review`, `governance`, `controlled-executor`.

For `router`, `review`, and `governance`, omitted tool configuration is rejected because portable structural validation cannot prove restrictive exposure. `--allow-write-tools` only waives the obvious write-marker check; it does not waive effective-authority review.

Use `--require-complete` for final artifacts to reject unresolved template placeholders.

Structural validation does not prove semantic quality or actual host permissions/runtime behavior.

## Validation Plan Output

```markdown
# Agent Validation Plan

## Scope
...

## Frozen Identities
- scenario suite:
- evaluator/graders:
- baseline/candidate:
- environment profile when material:

## Scenario Matrix
| Scenario | Group | Outcome | Trace invariants | Trials | Evidence status |
|---|---|---|---|---:|---|

## Critical Gates
- mission/ownership:
- effective authority:
- tool least authority:
- context trust/authority:
- control-flow ownership:
- multi-agent/concurrency:
- stop/escalation:
- state/interruption/termination:
- containment/downstream auth:
- evidence truthfulness:

## Not Measured
List behaviors/metrics not executed.
```
