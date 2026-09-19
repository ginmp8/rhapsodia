# Sample runs

Use the host's Python 3.10+ execution method for `<PYTHON>`.

## Bounded run with evidence-backed backlog

```text
<PYTHON> scripts/skill_improver_loop.py \
  --target <TARGET_SKILL_ROOT> \
  --evaluator skill-benchmark \
  --hypothesis-backlog ./reports/hypothesis-backlog.json \
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
  --eval-command '<PYTHON> ../../evals/eval_skill.py --target .' \
  --benchmark-lock-path ../../evals/eval_skill.py \
  --agent-adapter command \
  --agent-command-template '<AGENT_CLI> run --cwd {cwd} --prompt {prompt}' \
  --max-iterations 3 \
  --min-delta 0.5
```

The generic template is executed as argv without a shell. It must contain `{prompt}` and may contain `{cwd}` and `{target}`.

## Lock material source evidence

```text
<PYTHON> scripts/skill_improver_loop.py \
  --target <TARGET_SKILL_ROOT> \
  --evaluator skill-benchmark \
  --source-root <REPOSITORY_ROOT> \
  --source-lock-path docs/requirements.md \
  --source-lock-path reports/prior-audit.json \
  --max-iterations 3
```

The runner captures these source bytes before baseline evaluation and verifies them before candidate acceptance and final reporting.

## Hybrid static plus behavioral benchmark

```text
<PYTHON> scripts/skill_improver_loop.py \
  --target <TARGET_SKILL_ROOT> \
  --evaluator skill-benchmark \
  --skill-benchmark-results /path/to/frozen-scenario-results.json \
  --benchmark-lock-path /path/to/frozen-scenario-results.json \
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
  --output ./skill.zip \
  --receipt ./skill.zip.receipt.json
```

Do not edit the target between the final validation/hash and packaging without rerunning affected gates.
