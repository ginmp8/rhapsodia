# Sample runs

Use the host's Python 3.10+ execution method for `<PYTHON>`.
 The generic `command` adapter is the default portable path; the Codex adapter is optional. Evaluator and change-gate command strings are argv-tokenized and never interpreted by a shell.

## Bounded run with evidence-backed backlog

```text
<PYTHON> scripts/skill_improver_loop.py \
  --target <TARGET_SKILL_ROOT> \
  --evaluator skill-benchmark \
  --hypothesis-backlog <HYPOTHESIS_BACKLOG_JSON> \
  --max-iterations 3 \
  --min-delta 1.0 \
  --agent-adapter codex \
  --codex-mode full-auto
```

The backlog should come from `skill-hypothesis-discovery` or an equivalent evidence-backed planning pass. Discovery recommendations are not measured improvements until tested.

## Generic agent CLI adapter

```text
<PYTHON> scripts/skill_improver_loop.py \
  --target <TARGET_SKILL_ROOT> \
  --evaluator command \
  --eval-command '<PYTHON> <SKILL_IMPROVER_ROOT>/examples/eval_skill.py --target .' \
  --benchmark-lock-path <SKILL_IMPROVER_ROOT>/examples/eval_skill.py \
  --agent-adapter command \
  --agent-command-template '<AGENT_CLI> run --cwd {cwd} --prompt {prompt}' \
  --max-iterations 3 \
  --min-delta 0.5
```

The generic template is executed as argv without a shell. It must contain `{prompt}` and may contain `{cwd}` and `{target}`.

`<SKILL_IMPROVER_ROOT>` must be replaced with the absolute canonical path of this `skill-improver` package. The same evaluator path is used for execution and `--benchmark-lock-path` so the executed evaluator and frozen evaluator identity cannot diverge because of different relative-path bases.

## Lock material source evidence

```text
<PYTHON> scripts/skill_improver_loop.py \
  --target <TARGET_SKILL_ROOT> \
  --evaluator skill-benchmark \
  --source-root <REPOSITORY_ROOT> \
  --source-lock-path <SOURCE_REQUIREMENTS_PATH> \
  --source-lock-path <PRIOR_AUDIT_PATH> \
  --max-iterations 3
```

The runner captures these source bytes before baseline evaluation and verifies them before candidate acceptance and final reporting.

## Hybrid static plus behavioral benchmark

```text
<PYTHON> scripts/skill_improver_loop.py \
  --target <TARGET_SKILL_ROOT> \
  --evaluator skill-benchmark \
  --skill-benchmark-results <FROZEN_SCENARIO_RESULTS_JSON> \
  --benchmark-lock-path <FROZEN_SCENARIO_RESULTS_JSON> \
  --blocked-path ./evals \
  --max-iterations 3 \
  --min-delta 1.0
```

Use this when activation/output behavior matters. The scenario result file is frozen so the patching agent cannot improve the score by weakening the benchmark.

## Graceful cancellation

```text
<PYTHON> scripts/skill_improver_loop.py \
  --target <TARGET_SKILL_ROOT> \
  --evaluator skill-benchmark \
  --max-iterations 10 \
  --stop-file .skill-improver/stop
```

Cancel without deleting accepted changes:

```text
<PYTHON> scripts/cancel_skill_improver.py --stop-file .skill-improver/stop
```

## Freeze and package

```text
<PYTHON> scripts/evidence_snapshot.py hash-tree --root <TARGET_SKILL_ROOT>

<PYTHON> scripts/validate_skill_improver_package.py \
  --target <TARGET_SKILL_ROOT>

<PYTHON> scripts/package_skill.py \
  --target <TARGET_SKILL_ROOT> \
  --output <OUTPUT_SKILL_ZIP> \
  --receipt <OUTPUT_RECEIPT_JSON>
```

Do not edit the target between the final validation/hash and packaging without rerunning affected gates.
