# Measurement protocol and comparator

## Freeze before running a candidate

Write down: metric name and unit; lower/higher is better; target gain or allowed loss; workload/data size; environment ID; benchmark harness version; sample protocol, warmup and repetition count; relevant confounders (CPU contention, cache, network, JVM/CLR warmup, GC, throttling, CI runner variance). For user-visible UX, consider real-world measurements as well as synthetic results.

Capture at least 5 **positive finite** observations per baseline and candidate for the optional comparator. Gather more when variable. Baseline and candidate must use the same environment, workload and harness IDs; a mismatch makes the comparison invalid. Alternate or randomize run order where practical to reduce drift and thermal/cache bias. Record raw observations; never edit away inconvenient samples without a predeclared outlier rule.

## Comparator input

`assets/metrics-input.example.json` is an illustrative JSON contract. Replace IDs and samples with executed observations. Run from a Python 3 runtime (standard library only):

```text
python scripts/compare_metrics.py path/to/metrics.json --out path/to/metric-report.json
```

Choose a new output report path each time; an existing report is never overwritten. The helper computes medians, median absolute deviation (MAD), relative improvement and a conservative noise margin. `noise_margin_pct = max(user_noise_floor_pct, 3 * baseline_relative_MAD_pct, 3 * candidate_relative_MAD_pct)`.

For a **target**: `met` requires `improvement_pct >= min_improvement_pct + noise_margin_pct`. A clearly negative change outside the allowed regression plus noise margin is `regression`; an unequivocally sub-target result is `unmet`; ambiguous differences are `inconclusive`. For a **guardrail**, `met` requires a conservative margin above the maximum allowed regression. The noise margin is a heuristic, not a confidence interval or statistical test.

If any metric reports regression/unmet, the aggregate is `fail`; otherwise any inconclusive metric makes aggregate `inconclusive`; all met gives `pass`. These are **metric-only** results. They never prove test success, semantic equivalence, source integrity, security, or readiness to merge.

## Decision integrity

- Do not compare unequal hardware/runner/container, altered benchmark inputs, different warmup, incompatible time windows or changed test data as though they were equivalent.
- Do not compare one lucky sample against a noisy average. Do not assert statistical significance without an appropriate statistical design and calculation.
- Treat smaller memory at a much slower startup as a possible trade-off; explicit guardrails decide acceptability.
- The numerical helper does not execute the measured application, verify input authenticity, inspect Git diffs, or grant authorization to keep a change.
- An `inconclusive` result can justify another planned measurement attempt but not indefinite retry or altered thresholds.
