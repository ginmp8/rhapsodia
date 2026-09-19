# Evaluator Visibility and Blind-Run Contract

Use when activation/boundary behavior is evaluated with hidden graders, private expected routes, holdout labels, or other evaluator-only material.

## Visibility classes

- `candidate-visible`: information the evaluated agent/skill is legitimately allowed to read, including the user prompt, declared input files, and any rubric intentionally supplied as part of the task.
- `evaluator-only`: expected routes, private holdout labels, grader prompts, private scoring keys, and post-run adjudication that must not influence candidate behavior.
- `runner-only`: orchestration metadata needed to execute the run but not to decide the expected result.
- `post-run-only`: computed metrics and adjudication created after execution.

A rubric cannot be both hidden and candidate-visible. If the task intentionally exposes the rubric, classify it as `candidate-visible` and do not call the run blind.

## Isolation rule

Blind evaluation requires a clean candidate/evaluator boundary. Use the strongest isolation the host reasonably supports, but keep the semantic contract host-neutral:

1. fresh dedicated working state is the minimum;
2. separate process or container isolation is stronger when available;
3. external hosts are acceptable when their isolation limitations are recorded;
4. do not make Docker, a particular sandbox, or a vendor-specific runner mandatory for portable correctness.

## Leakage gate

Set `candidate_saw_evaluator_only_assets=false` only when the execution setup actually prevented access to evaluator-only assets. If exposure occurred or cannot be established, do not use the run for hidden/blind comparison claims.

Exposure includes direct file/context access and indirect injection of expected routes, holdout labels, grader prompts, or post-run judgments before candidate completion.

## Trace provenance

When a host exposes a trace, bind it through `trace_manifest_sha256` or another stable reference. A trace can help diagnose routing behavior but does not replace evaluator identity, suite identity, or leakage checks.

Do not put secrets or unnecessary sensitive payloads in the evidence envelope merely to obtain a trace hash.

## Comparability

Baseline and candidate comparisons require materially equivalent host configuration. If host profiles differ in a way that can affect routing or skill invocation, mark the behavioral delta not comparable rather than attributing the difference to the prompt/activation change.
