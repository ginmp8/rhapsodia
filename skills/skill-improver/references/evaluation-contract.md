# Evaluation Contract

## Benchmark lifecycle

The improvement loop must not start until a benchmark exists and is frozen for the run.

```text
prepare benchmark -> run baseline -> freeze evaluator inputs -> test hypotheses
```

A benchmark may be created immediately before the loop, but candidate changes must be measured against the same frozen benchmark. Do not change tests, expected outputs, evaluator scripts, scenario results, scoring weights, or gate definitions during an improvement iteration.

## Required score format for custom evaluators

The preferred evaluation command prints JSON to stdout:

```json
{
  "score": 87.5,
  "max_score": 100,
  "direction": "higher-is-better",
  "status": "pass",
  "gates": {
    "frontmatter": "pass",
    "packaging": "pass",
    "activation_suite": "pass"
  },
  "report_path": "docs/skill-benchmark/example/skill-benchmark.md",
  "notes": ["short explanation"]
}
```

Only `score` is mandatory for backward compatibility. For autonomous runs, include `status` and `gates` so the runner can reject candidates that raise the numeric score while breaking a required condition. The runner can also extract a score with `--score-regex`, but JSON is safer.

## Built-in skill-benchmark evaluator

When `--evaluator skill-benchmark` is used, the runner calls the installed skill-benchmark report generator, parses the generated Markdown report, and converts it into this internal shape:

```json
{
  "score": 93,
  "status": "pass",
  "gates": {
    "Valid SKILL.md exists": "pass",
    "Frontmatter has name and description": "pass",
    "Expected output is clear": "pass"
  },
  "verdict": "approve with reservations",
  "report_path": ".skill-improver/skill-benchmark-reports/target/skill-benchmark.md"
}
```

`approve` and `approve with reservations` are treated as pass. `reject` is treated as fail. Blocker gates are enforced by default.

## Acceptance rule

A candidate is accepted only when all configured conditions are true:

```text
same benchmark hash
and no blocked paths changed
and candidate status/gates pass
and candidate_score >= best_score + min_delta
```

for `higher-is-better`, or:

```text
same benchmark hash
and no blocked paths changed
and candidate status/gates pass
and candidate_score <= best_score - min_delta
```

for `lower-is-better`.

If a gate fails, reject even when the numeric score improves. If the evaluator or locked fixtures changed, reject and revert.

## Gate policy

Use these flags to tune strictness:

- `--enforce-blocker-gates`: default on; rejects failed benchmark blocker gates.
- `--enforce-all-gates`: rejects any reported gate failure.
- `--required-gate <name>`: requires a specific gate to exist and pass. Can be repeated.
- `--require-status-pass`: requires evaluator status to equal `pass` exactly.
- `--enforce-no-new-gate-failures`: default on; rejects new gate failures relative to baseline.

Recommended default for skill improvement:

```text
blocker gates on
no new gate failures on
all gates optional unless the benchmark is mature
```

## Freeze policy

The runner freezes evaluator identity and inputs by hashing:

- evaluator mode and acceptance settings;
- custom eval command string, when using `--evaluator command`;
- `skill-benchmark` script and optional results file, when using `--evaluator skill-benchmark`;
- every file or directory passed with `--benchmark-lock-path`.

Use `--blocked-path` to prevent Codex from editing evaluator files or fixtures even when they are inside the repo or target skill path.

## Suggested metric sources

Use one or more of:

1. Static skill benchmark score.
2. Activation prompt suite.
3. Output conformance suite.
4. Packaging validator.
5. Golden examples.
6. Safety/negative prompts.
7. Human review score.

For strong autonomous runs, prefer a composite benchmark:

```text
static skill-benchmark score
+ fixed activation/output scenario results
+ packaging validation
+ safety/negative prompt gates
```

## Anti-overfitting rules

- Do not delete failing tests to improve the score.
- Do not alter expected outputs during an improvement iteration.
- Do not edit the evaluator unless the run objective is explicitly evaluator design.
- Do not accept a candidate if the benchmark hash changed.
- Keep a holdout set of prompts for manual review after accepted changes.
- Log rejected hypotheses so the loop does not repeatedly test the same failed idea.
