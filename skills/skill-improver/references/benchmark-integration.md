# Skill Benchmark Integration

## Roles

Use `skill-benchmark` for structural scoring/reporting. Use `skill-improver` to propose, patch, evaluate, accept, or revert hypotheses.

```text
skill-benchmark -> evaluates and reports
skill-improver -> orchestrates experiments
```

Never accept subjectively without an evaluator. A benchmark may be created first, but it must run successfully and be frozen before candidate testing.

## Static benchmark enough when optimizing

- frontmatter trigger clarity;
- scope/non-goals;
- input/output contract;
- validation checklist;
- resource/script integration;
- context efficiency and maintainability.

Run:

```bash
<PYTHON> scripts/skill_improver_loop.py \
  --target /path/to/target-skill \
  --evaluator skill-benchmark \
  --max-iterations 10 \
  --min-delta 1.0
```

## Add behavioral evidence when

Activation quality or generated-output quality matters; static score is saturated; or benchmark-friendly wording could game the result.

```bash
<PYTHON> scripts/skill_improver_loop.py \
  --target /path/to/target-skill \
  --evaluator skill-benchmark \
  --skill-benchmark-results /path/to/frozen-scenario-results.json \
  --benchmark-lock-path /path/to/frozen-scenario-results.json \
  --blocked-path evals \
  --max-iterations 10 \
  --min-delta 1.0
```

Scenario-result schema:

```json
[
  {
    "id": "A1",
    "category": "should_activate",
    "prompt": "Benchmark the target skill.",
    "expected_activation": true,
    "actual_activation": true,
    "output_conforms": true,
    "quality_score": 5,
    "needs_rework": false,
    "notes": "Expected behavior observed."
  }
]
```

## Guardrail defaults

For `--evaluator skill-benchmark`: freeze benchmark inputs; enforce blocker gates; reject new gate failures relative to baseline; block evaluator/scenario paths; reject benchmark verdict `reject`; write the run report under the configured state directory. Use `--enforce-all-gates` only when the benchmark is mature enough for every gate to pass.

## Benchmark-design phase

If no benchmark exists: run `skill-benchmark` once; create at least 20 planned/measured scenarios across activate, do-not-activate, ambiguous, and edge cases; convert measured outputs to locked scenario-results JSON; lock results/config; record baseline; then start a new improvement run. Do not add tests inside the same candidate acceptance loop.


## Reproducibility overlay

When benchmark score is already saturated, keep it as a gate and choose a non-saturated auxiliary metric before mutation. Freeze evaluator inputs and material source evidence separately: `--benchmark-lock-path` protects evaluator identity; `--source-lock-path` captures external evidence whose bytes affect the decision. A score gain is not accepted when source verification or the structural change gate fails.
