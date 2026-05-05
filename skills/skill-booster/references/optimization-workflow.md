# Optimization Workflow

Use this ordered workflow for every target skill. If a stop condition applies, report the blocker instead of mutating.

## Phase 0: Intake

Capture target path/zip, mode, final artifact, writable scope, blocked paths, known failures, evaluator, language/output conventions, and user-declared read-only files. For “full optimization”, use `apply-optimization`, then validation and package when gates pass.

## Phase 1: Preflight and inventory

Run:

```bash
python scripts/validate_skill_booster.py --target <TARGET_SKILL_PATH>
```

Inventory `SKILL.md`, `agents/`, `references/`, `scripts/`, `assets/templates/`, `examples/`, `evals/`, validators, reports, generated files, and packages. Record risks and unavailable resources.

## Phase 2: Baseline and freeze

Use the strongest available evaluator: target validator/CI, `skill-benchmark`, harness, static validator, then planned evaluator. Freeze scenarios, expected outputs, benchmark inputs, scoring config, validator scripts, fixtures, generated baseline reports, and blocked paths. Record score, gates, warnings, command, timestamp, hashes when practical.

## Phase 3: Specialist passes

Run or account for the passbook sequence, including `skill-hypothesis-discovery` for evidence-based hypothesis selection and `skill-change-gate` for candidate acceptance and final regression checks. Key order constraints:

1. `skill-creator-juiced` and architecture decisions before broad text rewrites.
2. Run `skill-benchmark` and `skill-harness` before `skill-hypothesis-discovery` whenever possible, so discovery uses actual score, scenario, and gate evidence instead of speculation.
3. `skill-hypothesis-discovery` produces a deduplicated, ranked backlog and recommends the next 1-3 hypotheses; do not let it mutate target files.
4. `skill-improver` tests selected bounded hypotheses, then `skill-change-gate` reviews candidate acceptance risk before broader conclusions are treated as accepted.
5. `skill-prompt-and-activation-review` and `prompt-architect` before consistency/doc/code/security passes.
6. `skill-testing-and-validation` before cleanup or compression.
7. `skill-token-efficient` only after behavior, safety, architecture, docs, consistency, validation, and candidate gate checks are stable.
8. Revalidate after compression, then harden, rerun final `skill-change-gate`, benchmark, close with `skill-improver`, and finish with final token-efficiency audit/validate.

## Phase 4: Patch discipline

Apply one bounded hypothesis per patch batch, selected from the discovery backlog or supplied by the user. Keep `SKILL.md` compact; move branch details to references; use scripts only for deterministic validation/packaging; keep templates/assets only when operational or intentionally retained. Do not alter frozen evaluator inputs, fixtures, expected outputs, generated evidence, secrets, old zips, or unrelated files.

## Phase 5: Validate, package, and close

After each material change, rerun the frozen evaluator, affected validators, and `skill-change-gate` or its local checklist. If discovery found no viable mutation, report no-mutation and preserve the target unless required repairs exist. After cleanup and compression, rerun target validators, script syntax/smoke checks, local-link checks, package checks, final `skill-change-gate`, and final benchmark.

Package only when validation passes:

```bash
python scripts/package_skill.py --target <TARGET_SKILL_PATH> --output <OUTPUT_DIR>/skill.zip --report <REPORT_DIR>/package-validation.json
```

Use an equivalent specialist packager only when the target lacks one. The archive must be named `skill.zip`, written outside the target folder, exclude caches/reports/secrets/old zips, and contain the final skill folder only.

Final closure reports baseline vs final, discovery backlog summary, deltas, accepted/rejected hypotheses, command outcomes, pass ledger, candidate and final `skill-change-gate` status, final package path, remaining risks, next hypothesis, and final token-efficiency closure status. If the final token pass mutates files, rerun affected validation and package gates before readiness claims.
