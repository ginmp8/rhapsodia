# Software Improvement Loop (v0.1.0)

Portable Agent Skills workflow for evidence-driven improvements of existing software. The skill does not require PandaCode and does not modify Magia or any other skill. It can be loaded by a coding agent used from PandaCode when the chosen agent supports and discovers Agent Skills.

## How to use

1. Install the whole `software-improvement-loop` directory in a location supported by the **underlying coding agent**; confirm it actually loads `SKILL.md`.
2. Request an improvement with scope, constraints and acceptance: "Use software-improvement-loop to reduce startup latency by 15%, without increasing memory by more than 3%; run benchmarks and regression tests; no merge/deployment."
3. The agent establishes a baseline, freezes checks, isolates candidates, performs at most three bounded attempts by default, verifies and reports `keep`, `revert`, `inconclusive`, or `blocked`.
4. For numeric performance evaluation, optionally run `python scripts/compare_metrics.py your-evidence.json --out your-report.json` using real recorded benchmark samples. `assets/metrics-input.example.json` is synthetic example data, **not a performance result**.

The helper never executes an app or tests, manipulates source code, or makes a merge decision. An actual coding agent must perform and record those actions within authorization.

## Package contents

`SKILL.md` is the control plane. `references/` contains mode, safety, measurement and integration rules. `scripts/compare_metrics.py` is an optional standard-library-only metric comparison tool with regression tests. `assets/` has example input and report templates. `evals/` contains **planned** activation scenarios (not model-run evidence). `VERSION` and `CHANGELOG.md` identify the release.

## Check locally

```text
python -m unittest discover -s scripts/tests -v
python scripts/compare_metrics.py assets/metrics-input.example.json --out /tmp/metric-report.json
```

For structural portability, use a compatible Agent Skills validator; successful structural checks do not prove PandaCode, Codex, Claude Code, Copilot, Cursor, or ChatGPT runtime activation.
