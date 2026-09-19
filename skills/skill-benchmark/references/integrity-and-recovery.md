# Benchmark Integrity and Recovery

Use for filesystem benchmarks, version comparisons, measured behavioral evidence, and any report/package write.

## Freeze target bytes before scoring

For a filesystem target, prefer:

```text
<PYTHON> scripts/snapshot_target.py capture \
  --target <TARGET> \
  --snapshot-dir <WORK>/target-snapshot \
  --out <WORK>/target-manifest.json
```

Benchmark `<WORK>/target-snapshot`, not the mutable live target. The manifest binds the report to exact source bytes.

Before a final comparison/readiness claim:

```text
<PYTHON> scripts/snapshot_target.py verify \
  --manifest <WORK>/target-manifest.json \
  --json <WORK>/target-verification.json
```

If the live source changes, either keep evaluating the frozen snapshot or invalidate/re-baseline. Do not silently mix versions.

## Freeze evaluator identity

The benchmark rubric, report template, scenario contract, generator, and validators are part of the evaluator. Compute their identity:

```text
<PYTHON> scripts/benchmark_identity.py --json <WORK>/evaluator-manifest.json
```

For strict version deltas, baseline and candidate must use the same evaluator identity and the same scenario suite identity. If they differ, show the individual results but label the delta `not comparable`.

## Pinned repository evidence

When a benchmark attributes evidence to a VCS revision, prefer immutable object reads for that revision rather than the current working tree. Record repository, revision SHA, path/range, and any limitation preventing immutable reads. Dirty files, moving refs, or replacement refs must not silently redefine the claimed revision.

## Scenario provenance

Prefer the versioned scenario envelope documented in `test-scenarios.md`. It binds results to:

- target identity;
- evaluator identity;
- evidence origin;
- scenario rows.

Legacy arrays remain accepted for compatibility but are `unpinned` and cannot support strict before/after improvement claims.

## Output alias preflight

Before writing a report, package, or receipt:

- canonicalize authored and resolved paths;
- keep generated evidence outside the benchmark target;
- reject report/receipt aliases, including hardlink/symlink aliases;
- reject output/input aliases;
- reject symbolic-link cycles and non-file targets where a normal file is required.

A preflight failure must preserve existing bytes.

## Transactional report/package delivery

Treat an artifact plus success receipt as one logical transaction:

`stage -> validate -> hash -> preserve old targets -> commit artifact+receipt -> remove backups`

If commit fails, restore last-known-good outputs. If rollback is incomplete, preserve exact recovery paths instead of deleting the evidence.

Success receipts must identify the exact committed bytes and include, where applicable:

- `receipt_version`;
- `status` and `stage`;
- target/source identity;
- evaluator identity;
- report/archive hash;
- portability/validation evidence;
- recovery state.

Do not overwrite a prior successful receipt merely to record a failed attempt.
