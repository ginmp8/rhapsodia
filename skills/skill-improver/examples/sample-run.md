# Sample runs

## Using a hypothesis-discovery backlog

Generate or supply a backlog before running the loop when no bounded hypothesis is obvious. Replace `<target-skill-root>` with the target skill package root, for example `skills/magnomo`, `.github/skills/magnomo`, or an extracted `magnomo` directory.

```bash
python scripts/skill_improver_loop.py \
  --target <target-skill-root> \
  --evaluator skill-benchmark \
  --hypothesis-backlog ./reports/hypothesis-backlog.json \
  --max-iterations 3 \
  --min-delta 1.0 \
  --codex-mode full-auto
```

The backlog should come from `skill-hypothesis-discovery` or an equivalent evidence-backed planning pass. The runner tests selected hypotheses; it does not treat discovery recommendations as measured improvements.

## Skill-benchmark evaluator

```bash
python scripts/skill_improver_loop.py \
  --target <target-skill-root> \
  --evaluator skill-benchmark \
  --max-iterations 10 \
  --min-delta 1.0 \
  --codex-mode full-auto
```

This uses the installed `skill-benchmark` generator, writes reports under `.skill-improver/skill-benchmark-reports/`, freezes evaluator inputs, enforces blocker gates, and reverts candidates that do not improve.

## Hybrid static plus behavioral benchmark

```bash
python scripts/skill_improver_loop.py \
  --target <target-skill-root> \
  --evaluator skill-benchmark \
  --skill-benchmark-results /path/to/frozen-scenario-results.json \
  --benchmark-lock-path /path/to/frozen-scenario-results.json \
  --blocked-path ./evals \
  --max-iterations 10 \
  --min-delta 1.0 \
  --codex-mode full-auto
```

Use this when activation and output behavior matter. The scenario result file is locked so the agent cannot improve the score by weakening the benchmark.

## Custom evaluator command

```bash
python scripts/skill_improver_loop.py \
  --target <target-skill-root> \
  --evaluator command \
  --eval-command 'python ../../evals/customer_research_eval.py --target .' \
  --benchmark-lock-path ./evals/customer_research_eval.py \
  --required-gate packaging \
  --max-iterations 8 \
  --min-delta 0.5
```

The command should print JSON with at least `score`. Include `status` and `gates` for stronger acceptance rules.

## Yolo mode only in a disposable environment

```bash
python scripts/skill_improver_loop.py \
  --target <target-skill-root> \
  --evaluator skill-benchmark \
  --max-iterations 50 \
  --codex-mode yolo \
  --sandbox-acknowledged
```

Do not run this on a normal developer workstation.

## Graceful cancellation for long-running loops

Start a bounded loop with an explicit stop file:

```bash
python scripts/skill_improver_loop.py \
  --target <target-skill-root> \
  --evaluator skill-benchmark \
  --max-iterations 10 \
  --stop-file .skill-improver/stop
```

Cancel from the repository root without deleting accepted target changes:

```bash
python scripts/cancel_skill_improver.py --stop-file .skill-improver/stop
```

The loop exits before the next candidate. Re-run validation before packaging or reporting final success.
