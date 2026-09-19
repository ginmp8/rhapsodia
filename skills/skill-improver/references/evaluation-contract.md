# Evaluation Contract

Use this contract whenever a candidate mutation can be accepted or rejected.

## Lifecycle

```text
identify target -> preserve baseline -> detect capabilities -> freeze evaluator
-> snapshot material sources -> run baseline -> select one hypothesis -> patch
-> verify sources -> rerun same evaluator -> structural change gate
-> accept/reject -> freeze final candidate -> validate/package/deliver
```

Do not change evaluator inputs, thresholds, fixtures, or expected outputs after observing candidate results.

## Evaluator result contract

A custom evaluator should emit JSON with a numeric `score` and preferably `status`, `gates`, and stable diagnostics:

```json
{
  "score": 84.5,
  "status": "pass",
  "gates": {
    "activation": "pass",
    "packaging": "pass"
  },
  "diagnostics": [
    {
      "code": "activation/ambiguous-route",
      "severity": "major",
      "subject": "prompt:A17",
      "evidence": {"expected": "manual-patch", "actual": "benchmark-only"},
      "supported_fixes": ["tighten mode router"]
    }
  ]
}
```

When only free text exists, use `--score-regex`; treat that as weaker evidence because gates and diagnostics are less structured.

## Built-in `skill-benchmark`

`skill-benchmark` can be the primary structural evaluator. Freeze its generator/script and any supplied behavioral results. Treat static or saturated scores as gates rather than proof of behavioral quality.

For behavioral claims, supply locked scenario results or execute paired scenarios against baseline and candidate with the same prompts/files.

## Severity handling

Use `references/severity-lifecycle.md` for canonical severity and tie-breakers. `critical` and `major` findings block final acceptance; `minor` findings are individually evaluated; `needs-verification` is never treated as fixed or safe by absence of proof. Order equally severe findings by stable diagnostic code or canonical subject path when possible.

## Hypothesis discovery contract

Prefer, in order:

1. user-supplied bounded hypothesis;
2. supplied evidence-backed backlog;
3. `skill-hypothesis-discovery` when the next candidate is unclear or metrics are saturated;
4. built-in catalog fallback.

Every tested hypothesis must identify:

- mechanism;
- evidence signal;
- bounded file scope;
- expected effect;
- validation method;
- accept/reject threshold;
- rollback plan;
- reproducibility control being improved.

Discovery is planning evidence. A discovered hypothesis is not an improvement until it passes the frozen comparison and structural change gate.

## Structural change gate

Run a structural gate independently from the numeric evaluator when the policy is `advisory` or `required`. `skill-change-gate` or a compatible command may be used.

The gate should inspect regressions in:

- activation and scope boundaries;
- semantic/output contracts;
- safety/authority;
- references and progressive loading;
- validator/test/eval integrity;
- compatibility/migration behavior;
- packaging/delivery;
- evidence discipline and receipts.

Compatible command output:

```json
{
  "status": "pass-with-warnings",
  "blocking_regressions": [],
  "material_concerns": ["new adapter is untested on Windows"],
  "accepted_tradeoffs": [],
  "notes": "core semantics preserved"
}
```

`fail` blocks acceptance when policy is `required`. `pass-with-warnings` may be accepted only when warnings are explicitly recorded as non-blocking.

## Acceptance rule

A candidate may be accepted only when all applicable conditions hold:

```text
same frozen evaluator identity
and material source snapshots still verify
and no blocked/protected paths changed
and required evaluator gates pass
and no new mandatory gate failure appears
and target metric meets the predeclared delta when improvement is claimed
and structural change gate allows acceptance
and cost/time remains within the declared budget
```

If the primary metric is saturated, replace the metric-improvement clause with an explicit non-saturated auxiliary metric or a clearly scoped hardening objective. Do not claim numeric improvement from wording changes against a ceilinged static score.

## Freeze policy

Hash/freeze evaluator identity and inputs:

- evaluator mode and acceptance settings;
- custom evaluator command or benchmark generator;
- scenarios, expected outputs, grading prompts, thresholds;
- every `--benchmark-lock-path`;
- behavioral result files reused by the benchmark.

Use `--blocked-path` to stop the patching agent from editing evaluator/fixture paths even if they are within the normal mutation scope.

If an evaluator must be repaired, invalidate the current comparison, freeze the repaired evaluator separately, and restart the baseline.

## Source integrity policy

When mutable external files or repository content materially determine the hypothesis or acceptance decision, capture their exact bytes before analysis:

```text
<PYTHON> scripts/evidence_snapshot.py capture ...
```

For the autonomous runner, use `--source-lock-path` and optional `--source-root`. The runner verifies the manifest before candidate acceptance and again before final reporting.

A failed source verification invalidates the comparison unless the experiment is deliberately re-baselined.

## Saturated metrics

Keep a saturated score as a gate and add a non-saturated auxiliary metric before claiming improvement, such as:

- holdout robustness;
- ambiguous activation;
- repair rounds;
- manual rework;
- runtime failures;
- token/context cost;
- portability capability coverage.

## Diagnostic repair rule

For an objective failure:

`diagnostic -> one causal subject -> smallest supported fix -> same gate -> adjacent gates`

Stop the branch after two consecutive rounds that do not reduce the same objective error set unless new evidence changes the hypothesis.

## Freeze after pass

Once the accepted final candidate passes applicable validation, compute its exact identity and stop editing it. Any later change invalidates the affected evidence and requires revalidation before packaging.

## Anti-overfitting

Do not:

- delete failing tests or difficult scenarios;
- weaken thresholds or expected outputs;
- edit evaluator inputs after seeing candidate results;
- accept when the frozen evaluator hash changed;
- report prompt/scenario pass rates without captured outputs;
- optimize a 100/100 static score by adding benchmark-friendly keywords.

Keep holdout scenarios or independent review for claims vulnerable to benchmark overfitting.

## Evidence vocabulary

Use:

- `measured`: executed command/scenario/evaluator evidence;
- `observed`: direct file/output inspection;
- `derived`: deterministic calculation from evidence;
- `supplied`: user-provided evidence not independently executed;
- `planned`: not executed;
- `blocked`: could not be obtained.

Do not upgrade structural evidence to behavioral/runtime/perceptual evidence.
