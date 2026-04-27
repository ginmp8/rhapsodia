# Skill Improver Execution Runbook

Use this reference when a run needs operational detail beyond the control plane in `SKILL.md`: CLI commands, benchmark modes, self-improvement safeguards, packaging, and rollback.

## Default operating assumptions

When the user asks to improve a skill but omits details, continue with conservative defaults instead of stalling:

- Evaluator: use `skill-benchmark` when available. If it is saturated at `100/100`, keep it as a gate and add an auxiliary non-saturated signal before claiming improvement.
- Budget: one manual patch or up to `--max-iterations 3` for an automated loop.
- Minimum delta: `1.0` unless the evaluator has a smaller meaningful unit.
- Scope: edit only the target skill folder.
- Blocked paths: evaluator scripts, expected outputs, scenario fixtures, benchmark reports used as fixtures, lockfiles, `.git`, caches, package artifacts, and secrets.
- Safety: prefer a separate working copy and manual patch review unless the user explicitly provides a disposable sandbox or CI runner.

## Benchmark modes

| Mode | Use when | Required guardrail |
|---|---|---|
| `existing-command` | The user already has a deterministic evaluator command. | Require JSON score or a score regex and lock evaluator inputs. |
| `skill-benchmark` | Structural maturity and canonical reporting are enough to start. | Parse score, verdict, and blocker gates; reject blocker failures. |
| `hybrid` | Activation or output behavior matters. | Use static structure plus a locked behavioral result file. |
| `generate-first` | No benchmark exists. | Create the benchmark, measure baseline, freeze it, then start improvement. |

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

This mode uses the installed benchmark report generator, writes reports under `.skill-improver/skill-benchmark-reports/`, freezes evaluator inputs, enforces blocker gates, and reverts candidates that do not improve.

## Hybrid run with fixed behavioral results

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

Use this when activation and output behavior matter. The scenario result file is locked so the agent cannot improve the score by weakening the benchmark.

## Custom evaluator command

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

The command should print JSON containing at least `score`. Include `status`, `gates`, `direction`, and `report_path` for stronger acceptance decisions.

## Yolo mode rule

Only use yolo mode inside a disposable environment that the user explicitly acknowledges:

```bash
python scripts/skill_improver_loop.py \
  --target /path/to/target-skill \
  --evaluator skill-benchmark \
  --max-iterations 50 \
  --codex-mode yolo \
  --sandbox-acknowledged
```

Never use this mode on a normal developer workstation or broad filesystem mount.

## Installation and packaging flow

When the user asks to install or package the improved skill:

1. Preserve a backup before overwriting an installed skill.
2. Confirm the destination is writable. If it is not, produce a zip or patch artifact.
3. Install by copying the accepted skill folder only, excluding evaluator work files, temporary reports, caches, secrets, and prior package artifacts.
4. Re-run validation on the installed or packaged contents.
5. State whether the installation is persistent or only applies to the current runtime/session.
6. Include rollback instructions based on the backup path.

For this package, use:

```bash
python scripts/validate_skill_improver_package.py --target /path/to/skill-improver
python scripts/package_skill.py --target /path/to/skill-improver --output /path/to/skill.zip
```

## Self-improvement safeguards

When improving `skill-improver` itself:

- work in a separate copy when possible;
- record a pre-change hash or backup;
- keep `evals/`, benchmark reports, expected outputs, and external evaluator scripts blocked unless the user requested benchmark-design work;
- use one bounded hypothesis per patch;
- when improving supporting resources, integrate useful assets before deleting them; only remove templates after classifying them as placeholders, duplicated, obsolete, or not consumed by any script, reference, declared workflow, or validation gate;
- treat the static `100/100` score as a gate rather than a proof of improvement;
- make the final report explicit about bootstrapping, self-reference, and any unmeasured behavior.

## Rejection reasons

Reject or revert a candidate patch when any of these occur:

- benchmark hash or locked fixture hash changed;
- a blocked path changed;
- files outside allowed scope changed;
- required gates failed;
- evaluator output was missing, unparsable, or lower confidence than baseline;
- score failed to improve by the configured delta;
- the patch weakened safety boundaries, removed difficult tests, or claimed unmeasured scenario results.
