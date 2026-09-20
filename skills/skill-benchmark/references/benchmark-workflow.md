# Benchmark Workflow

Use for filesystem execution, evidence identity, comparison, paths, and finalization.

## Capability preflight

Resolve before commands:

- readable target;
- writable work/output directory outside target;
- `<PYTHON>` = available Python 3.10+ launcher/execution method;
- requested host profiles;
- optional independent behavioral execution capability.

If Python cannot run, manual/static inspection may continue, but script gates are `not-run` and no package/report-validation pass may be claimed.

## Filesystem benchmark sequence

1. Read target `SKILL.md`; confirm one root skill.
2. Capture exact source bytes:

```text
<PYTHON> scripts/snapshot_target.py capture \
  --target <TARGET> \
  --snapshot-dir <WORK>/target-snapshot \
  --out <WORK>/target-manifest.json
```

3. Freeze evaluator identity:

```text
<PYTHON> scripts/benchmark_identity.py --json <WORK>/evaluator-manifest.json
```

4. When multi-host support is requested/claimed:

```text
<PYTHON> scripts/validate_portability.py \
  --target <WORK>/target-snapshot \
  --hosts portable-core,openai,codex,claude,copilot,cursor \
  --json <WORK>/portability.json
```

5. If scenario results exist, validate them first:

```text
<PYTHON> scripts/validate_scenario_results.py \
  --results <RESULTS_JSON> \
  --json-output <WORK>/scenario-validation.json
```

6. Generate the report from the frozen snapshot:

```text
<PYTHON> scripts/generate_benchmark_report.py \
  --target <WORK>/target-snapshot \
  --source-manifest <WORK>/target-manifest.json \
  --out <OUTPUT_ROOT> \
  --hosts <HOSTS> \
  [--results <RESULTS_JSON>]
```

7. Validate the generated report:

```text
<PYTHON> scripts/validate_benchmark_report.py \
  --report <REPORT_MD> \
  --json-output <WORK>/report-validation.json
```

8. Before final comparison/readiness claims, verify source identity:

```text
<PYTHON> scripts/snapshot_target.py verify \
  --manifest <WORK>/target-manifest.json \
  --json <WORK>/target-verification.json
```

Read `integrity-and-recovery.md` for failure/recovery semantics.

## Evidence hierarchy

1. Frozen target bytes and command output.
2. Identity-bound supplied/executed scenario evidence.
3. User-supplied prior reports/review notes/issues, clearly labeled.
4. Target-local references/examples/validators.
5. Qualitative judgment, explicitly labeled.

Never cite uninspected files or treat planned evals as executed evidence.

## Comparison rules

For baseline vs candidate:

- freeze each target separately;
- use the same evaluator identity;
- use the same scenario suite identity;
- compare only like-for-like dimensions/metrics;
- if evaluator/scenario identity differs, mark delta `not comparable`;
- source changes after snapshot invalidate live-source claims unless deliberately re-baselined.

## Output ownership

Generated reports/receipts belong outside the target package. Never write into target fixtures, expected outputs, secrets, credentials, evaluator files, or benchmark baselines.

The report generator and package builder preflight canonical paths and preserve last-known-good outputs on failed commits. Do not bypass those checks with manual overwrites.

## Final response

Include target/source identity, evaluator identity, report path/content, score/verdict, failed/review gates, behavioral evidence status, requested-host portability status, commands run, validation result, and residual risks.
