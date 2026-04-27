# Skill Benchmark Integration

## Role separation

Use `skill-benchmark` as the default structural benchmark and report generator. Use `skill-improver` as the experiment orchestrator.

```text
skill-benchmark -> evaluates and reports
skill-improver -> proposes, patches, evaluates, accepts, or reverts hypotheses
```

The improver must not make subjective acceptance decisions without an evaluator. The benchmark does not need to exist before the project starts, but it must exist, run successfully, and be frozen before the first candidate hypothesis is tested.

## When skill-benchmark is enough

Use the built-in `skill-benchmark` evaluator by itself when the goal is structural maturity:

- better frontmatter trigger;
- clearer scope and non-goals;
- explicit input/output contract;
- validation checklist;
- supporting resources and scripts;
- context efficiency and maintainability.

Run:

```bash
python scripts/skill_improver_loop.py \
  --target /path/to/target-skill \
  --evaluator skill-benchmark \
  --max-iterations 10 \
  --min-delta 1.0
```

## When skill-benchmark is not enough

Static score alone can be gamed by adding benchmark-friendly words without improving behavior. Add behavioral evidence when the target skill depends on activation quality or generated output quality.

Recommended hybrid setup:

```bash
python scripts/skill_improver_loop.py \
  --target /path/to/target-skill \
  --evaluator skill-benchmark \
  --skill-benchmark-results /path/to/frozen-scenario-results.json \
  --benchmark-lock-path /path/to/frozen-scenario-results.json \
  --blocked-path evals \
  --max-iterations 10 \
  --min-delta 1.0
```

The `--skill-benchmark-results` file should use the scenario result schema supported by `skill-benchmark`:

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

For `--evaluator skill-benchmark`, keep these defaults unless there is a reason to relax them:

- freeze benchmark inputs;
- enforce blocker gates;
- reject new gate failures relative to baseline;
- block evaluator and scenario paths;
- reject if `skill-benchmark` returns `reject`;
- generate a run report under the configured state directory.

Use `--enforce-all-gates` only when the benchmark is mature enough that every gate is expected to pass. During early hardening, a candidate may still be useful if it improves the score and does not introduce new failed gates.

## Benchmark design phase

If no benchmark exists, run a separate benchmark-design phase before improvement:

1. Run `skill-benchmark` once for a static baseline.
2. Create at least 20 planned or measured scenarios: activate, do not activate, ambiguous, and edge cases.
3. Convert measured scenario outputs to a locked scenario-results JSON file.
4. Lock the result file and evaluator configuration.
5. Start the improvement loop only after the baseline score is recorded.

Do not add new tests during the same candidate acceptance loop. Add new tests only in a separate benchmark-hardening phase, then start a new improvement run.
