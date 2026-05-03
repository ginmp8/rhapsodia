# Execution Runbook

Use for CLI details, benchmark modes, defaults, self-improvement safeguards, packaging, and rollback beyond `SKILL.md`.

## Defaults

When details are omitted, continue conservatively:
- Evaluator: `skill-benchmark` when available; if `100/100`, treat as gate and add non-saturated auxiliary evidence before claiming improvement.
- Budget: one manual patch or `--max-iterations 3`.
- Minimum delta: `1.0` unless the evaluator has a smaller meaningful unit.
- Scope: target skill folder only.
- Blocked: evaluator scripts, expected outputs, scenario fixtures, benchmark reports used as fixtures, lockfiles, `.git`, caches, package artifacts, secrets.
- Safety: separate working copy and manual review unless the user provides a disposable sandbox or CI runner.


## Skill path resolution

When a user supplies an imprecise target, resolve it before mutation:
1. If the input ends with `SKILL.md`, use the containing directory after confirming the file exists.
2. If the input is a directory containing `SKILL.md`, use that directory.
3. Otherwise, search candidate skill roots by skill name or path substring and continue only after exactly one match is found.

For zero matches, report available candidate roots. For multiple matches, ask for selection rather than guessing. Never mutate a path that does not resolve to exactly one root `SKILL.md`.

## Reviewer-severity loop

When a reviewer, benchmark, agent, or static audit produces issues, triage them before patching:
- Critical: blocks skill loading, package validation, reference resolution, evaluator execution, or runtime safety. Fix immediately or stop.
- Major: materially weakens activation, output contract, workflow order, validation, or scope boundaries. Fix before polish.
- Minor: style, formatting, optional clarity, or subjective suggestions. Evaluate each item for functional value and false-positive risk before editing.

Do not batch unrelated critical, major, and minor changes in one candidate patch. A minor-only remainder may be rejected intentionally when the issue is a false positive, adds complexity, or does not improve activation/output behavior.

## Graceful cancellation

Long-running loops should expose a stop-file path. The runner checks the file before starting the next candidate and exits cleanly when present. Accepted changes stay in the target folder; rejected candidates remain reverted; in-flight candidate behavior depends on the active executor and should be reviewed before continuing.

```bash
python scripts/skill_improver_loop.py \
  --target /path/to/target-skill \
  --evaluator command \
  --eval-command 'python scripts/static_skill_score.py --target .' \
  --max-iterations 10 \
  --stop-file .skill-improver/stop
```

Request cancellation from the repository root or pass the same explicit stop-file path:

```bash
python scripts/cancel_skill_improver.py --stop-file .skill-improver/stop
```

Remove the stop file before starting a new loop. Do not report completion solely because cancellation happened; report the last accepted state, skipped iterations, validation status, and remaining risks.

## Benchmark modes

- `existing-command`: user supplies deterministic evaluator; require JSON score or score regex; lock inputs.
- `skill-benchmark`: structural maturity; parse score/verdict/blocker gates; reject blocker failures.
- `hybrid`: behavior matters; combine static score with locked behavioral result file.
- `generate-first`: no benchmark; create it, baseline, freeze it, then improve.

## Skill-benchmark run

```bash
python scripts/skill_improver_loop.py \
  --target /path/to/target-skill \
  --evaluator skill-benchmark \
  --max-iterations 10 \
  --min-delta 1.0 \
  --codex-bin codex \
  --codex-mode full-auto
```

Writes reports under `.skill-improver/skill-benchmark-reports/`, freezes inputs, enforces blocker gates, and reverts non-improving candidates.

## Hybrid run

```bash
python scripts/skill_improver_loop.py \
  --target /path/to/target-skill \
  --evaluator skill-benchmark \
  --skill-benchmark-results /path/to/frozen-scenario-results.json \
  --benchmark-lock-path /path/to/frozen-scenario-results.json \
  --blocked-path /path/to/evals \
  --max-iterations 10 \
  --min-delta 1.0
```

Use for activation/output behavior; lock scenario results so the agent cannot weaken the benchmark.

## Custom evaluator

```bash
python scripts/skill_improver_loop.py \
  --target /path/to/target-skill \
  --evaluator command \
  --eval-command 'python /path/to/eval_skill.py --target .' \
  --benchmark-lock-path /path/to/eval_skill.py \
  --required-gate packaging \
  --max-iterations 8 \
  --min-delta 0.5
```

Command should print JSON with at least `score`; add `status`, `gates`, `direction`, and `report_path` for stronger decisions.

## Yolo mode

Only inside an explicitly acknowledged disposable environment:

```bash
python scripts/skill_improver_loop.py \
  --target /path/to/target-skill \
  --evaluator skill-benchmark \
  --max-iterations 50 \
  --codex-mode yolo \
  --sandbox-acknowledged
```

Never use on a normal workstation or broad filesystem mount.

## Install/package

1. Preserve backup before overwriting an installed skill.
2. Confirm destination is writable; otherwise produce zip/patch artifact.
3. Copy only accepted skill folder, excluding evaluator work files, temp reports, caches, secrets, and prior packages.
4. Re-run validation on installed/packaged contents.
5. State whether installation is persistent or current-session only.
6. Include rollback instructions from backup path.

For this package:

```bash
python scripts/validate_skill_improver_package.py --target /path/to/skill-improver
python scripts/package_skill.py --target /path/to/skill-improver --output /path/to/skill.zip
```

## Self-improvement safeguards

For `skill-improver` itself: work in a separate copy; record backup/hash; block `evals/`, benchmark reports, expected outputs, and external evaluator scripts unless benchmark design was requested; use one bounded hypothesis per patch; integrate useful resources before deletion; remove templates only after classifying them as placeholders, duplicates, obsolete, or unconsumed; treat static `100/100` as gate only; report bootstrapping, self-reference, and unmeasured behavior.

## Reject/revert when

Benchmark or locked-fixture hash changed; a blocked path changed; files outside scope changed; required gates failed; evaluator output is missing/unparsable/lower confidence; score misses configured delta; safety boundaries weaken; difficult tests are removed; or unmeasured scenario results are claimed.
