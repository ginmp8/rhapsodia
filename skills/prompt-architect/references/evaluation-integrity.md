# Evaluation Integrity

Use this reference for comparative prompt evaluation, strong behavioral claims, LLM judges, optimizer-assisted search, and model/runtime migration.

## Freeze before candidate mutation

Freeze as applicable:

- scenario inputs;
- required/forbidden behaviors;
- dataset split;
- evaluator/rubric prompt;
- evaluator identity/version;
- thresholds and acceptance rule;
- material execution-profile identity;
- material execution-environment identity when runtime conditions can change paired outcomes;
- stop rule and trial budget.

If any deciding element changes after candidate results are visible, invalidate or explicitly re-baseline the comparison.

## Evidence layers

Keep static/structural, behavioral, runtime, and perceptual/editorial evidence separate. One failure can prove a regression; one success rarely proves stochastic reliability.

## LLM-as-a-judge controls

When an LLM judge materially decides a pairwise preference:

- blind candidate identity when practical;
- randomize or swap candidate order;
- permit ties;
- repeat judgments when a strong claim matters;
- keep judge model/prompt/configuration fixed;
- calibrate against human or objective labels when consequences justify it;
- report disagreement/instability instead of forcing a winner.

These controls are conditional. Do not add repeated LLM judging to deterministic checks that do not need it.

## Dataset separation

Use authoring/development cases to improve the prompt. Keep genuine holdouts outside the authoring surface when claiming generalization. A visible bundled eval is regression coverage, not a hidden holdout.

## Optimizer-assisted search

Prompt optimizers are allowed only as a bounded strategy:

1. freeze metric/evaluator and protected requirements;
2. declare search budget and stop rule;
3. preserve a canonical direct/single-candidate comparator when practical;
4. evaluate candidates with the same evidence basis;
5. do not let the optimizer edit graders, thresholds, expected outputs, or protected semantics;
6. validate finalists on holdouts when overfitting risk is material;
7. retain rejected/inconclusive evidence when it informs future search.

Optimizer output never self-promotes.

## Environment comparability

When a paired behavioral/runtime comparison can change because of provider/model configuration, host/runtime, tools/dependencies, locale/timezone, cache, or concurrency policy, capture the standalone profile in [environment-provenance.md](../references/environment-provenance.md) and validate both arms with `scripts/validate_execution_environment.py`. A material profile mismatch is `not-comparable`; rerun or re-baseline instead of averaging across drift.

Do not require this profile for static-only inspection where environment identity cannot affect the conclusion.

## Execution-profile migration

A model/host/tool-schema migration is a behavioral dependency change. Reuse structural requirements, but revalidate behavioral/runtime evidence affected by the changed profile.

Do not describe previous runtime evidence as current after material profile drift.
