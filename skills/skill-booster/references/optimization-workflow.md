# Optimization Workflow

Use this ordered workflow for every target skill. If a stop condition applies, report the blocker instead of mutating.

## Phase 0: Intake

Capture target path/zip, mode, final artifact, writable scope, blocked paths, known failures, evaluator, language/output conventions, requested hosts, and user-declared read-only files. Resolve host capabilities from `references/host-compatibility.md` instead of assuming a vendor runtime. For `full optimization`, use `apply-optimization`, then validation and package when gates pass.

## Phase 1: Preflight and inventory

Run:

```text
<PYTHON> scripts/validate_skill_booster.py --target <TARGET_SKILL_PATH>
```

When portability is requested or will be claimed:

```text
<PYTHON> scripts/validate_portability.py --target <TARGET_SKILL_PATH> --hosts <HOSTS>
```

Inventory `SKILL.md`, optional host adapters such as `agents/`, `references/`, `scripts/`, `assets/templates/`, `examples/`, `evals/`, validators, reports, generated files, and packages. Host adapters may enhance one platform but cannot be required by the portable core. Record risks and unavailable resources.

## Phase 2: Baseline and freeze

Use the strongest available evaluator: target validator/CI, `skill-benchmark`, harness, static validator, then planned evaluator. Freeze scenarios, expected outputs, benchmark inputs, scoring config, validator scripts, fixtures, generated baseline reports, and blocked paths. When external files or repository evidence materially determine hypotheses or acceptance, capture exact source bytes before analysis with `scripts/snapshot_sources.py`; prefer immutable revision/object reads for pinned VCS evidence. When activation scenarios are present and compatible, run `scripts/run_activation_harness.py` as deterministic schema/coverage evidence, not as live activation precision. Record score, gates, warnings, command, timestamp, source identity, and hashes when practical.

## Phase 3: Specialist passes and reproducibility routing

Run or account for the passbook sequence using the host-native dispatch mechanism. Specialist names are logical capabilities; do not embed or assume a vendor-private skill API. Key order constraints:

1. `skill-creator-juiced` and architecture-governance decisions precede broad rewrites.
2. Run initial `skill-benchmark` and `skill-harness` before the reproducibility gate whenever possible.
3. Evaluate `references/reproducibility-routing.md` and write one routing decision before hypothesis discovery. Validate it:

```text
<PYTHON> scripts/validate_reproducibility_decision.py <DECISION_JSON>
```

4. If the state is `invoke-audit`, invoke `reproducibility-engineer` in `audit-only`; its ceiling/variability/control findings feed `skill-hypothesis-discovery`. If the state is `invoke-apply`, invoke it in `apply` only for the explicit bounded reproducibility batch, then run `skill-change-gate` before acceptance. `not-applicable`, `blocked`, and `unavailable` require evidence and do not count as invocation.
5. `skill-hypothesis-discovery` produces a deduplicated ranked backlog from benchmark, harness, reproducibility findings when applicable, and the remaining specialist evidence; it does not mutate target files.
6. `skill-improver` tests selected bounded hypotheses not already owned by an `invoke-apply` reproducibility batch; `skill-change-gate` reviews candidate acceptance before broader conclusions are accepted.
7. Run prompt/activation, consistency, docs, code/security/testing, cleanup, and token passes in passbook order. Revalidate after compression, then harden, run final `skill-change-gate`, benchmark, improver closure, and final token-efficiency closure.

If the user supplies an explicit required specialist sequence, actual invocation is mandatory for every available listed specialist; checklist-only is allowed only when unavailable, blocked, unsafe, or not-applicable. Reconcile before completion/package claims.

## Phase 4: Patch discipline

Apply one bounded hypothesis per patch batch. Keep `SKILL.md` compact; move branch details to references; use scripts only for deterministic validation/packaging; keep templates/assets only when operational or intentionally retained. Do not alter frozen evaluator inputs, fixtures, expected outputs, generated evidence, secrets, old zips, or unrelated files.

For reproducibility-owned work:

- `audit-only` does not mutate; route findings into the normal backlog.
- `apply` owns only the selected reproducibility transformation batch.
- Do not duplicate the same patch under both `reproducibility-engineer` and `skill-improver`.
- After a reproducibility `apply` batch, run the same target validators and candidate `skill-change-gate` used for other material patches.

## Phase 5: Validate, freeze, package, and close

After each material change, rerun the frozen evaluator, affected validators, and `skill-change-gate` or local checklist. Before final report or packaging, validate any explicit specialist reconciliation ledger and reverify any material source snapshot. If the live source changed, evaluate only the captured snapshot or explicitly invalidate/re-baseline the experiment. If discovery finds no viable mutation, report no-mutation unless required repairs exist. After cleanup/compression, rerun validators, script syntax/smoke checks, link/package checks, final `skill-change-gate`, final benchmark, and token audit with local-regression review.

After the last passing final gate, freeze the candidate outside the target folder:

```text
<PYTHON> scripts/freeze_candidate.py freeze \
  --target <TARGET_SKILL_PATH> \
  --out <WORK_DIR>/candidate-manifest.json
```

Any later target edit invalidates the freeze. Immediately before packaging:

```text
<PYTHON> scripts/freeze_candidate.py verify \
  --target <TARGET_SKILL_PATH> \
  --manifest <WORK_DIR>/candidate-manifest.json
```

Package only when verification passes. `scripts/package_skill.py` validates/canonicalizes archive and receipt destinations before writing, rejects aliases, validates the target, excludes generated evidence/reports/caches/old zips/control artifacts, writes and verifies deterministic staged outputs, computes candidate/archive hashes, then commits `skill.zip` plus the success receipt as one recovery-aware transaction. A failed attempt must leave the previous archive and previous successful receipt untouched; incomplete rollback must preserve explicit recovery paths.

```text
<PYTHON> scripts/package_skill.py \
  --target <TARGET_SKILL_PATH> \
  --output <OUTPUT_DIR>/skill.zip \
  --report <REPORT_DIR>/package-validation.json
```

When an explicit required sequence was supplied:

```text
<PYTHON> scripts/package_skill.py \
  --target <TARGET_SKILL_PATH> \
  --output <OUTPUT_DIR>/skill.zip \
  --report <REPORT_DIR>/package-validation.json \
  --reconciliation-ledger <LEDGER_JSON>
```

For a portability objective, add `--portability-hosts <HOSTS>` to packaging so the delivered candidate is rechecked before replacement. Final closure reports baseline vs final, source-snapshot/provenance verification when material, host capability/portability evidence, reproducibility decision/evidence, backlog summary, deltas, accepted/rejected hypotheses, commands, pass ledger, reconciliation counts/finalization decision, candidate/final `skill-change-gate`, candidate manifest hash, package hash, receipt version/stage, last-known-good/recovery status, risks, next hypothesis, and token closure. If any post-freeze target mutation occurs, invalidate closure evidence and rerun affected gates before packaging.
