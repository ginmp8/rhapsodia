# Evaluation Contract

## Lifecycle

Do not start improvement until a benchmark exists and is frozen.

```text
prepare benchmark -> run baseline -> freeze evaluator inputs -> test hypotheses
```

A benchmark may be created immediately before the loop, but candidate changes must use the same frozen benchmark. Do not alter tests, expected outputs, evaluator scripts, scenario results, scoring weights, or gate definitions during an improvement iteration.

## Custom evaluator output

Preferred stdout is JSON:

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

Only `score` is mandatory for backward compatibility. Autonomous runs should include `status` and `gates`; `--score-regex` is allowed but JSON is safer.

## Built-in `skill-benchmark`

With `--evaluator skill-benchmark`, the runner calls the installed report generator, parses Markdown, and converts it to:

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

`approve` and `approve with reservations` pass; `reject` fails. Blocker gates are enforced by default.

## Acceptance rule

Accept only when all configured conditions hold:

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

for `lower-is-better`. Any gate failure, evaluator drift, or locked-fixture drift rejects and reverts the candidate even if the number improves.

## Gate flags

- `--enforce-blocker-gates`: default on; reject failed benchmark blocker gates.
- `--enforce-all-gates`: reject any reported gate failure.
- `--required-gate <name>`: require a named gate to exist and pass; repeatable.
- `--require-status-pass`: require evaluator status exactly `pass`.
- `--enforce-no-new-gate-failures`: default on; reject new gate failures relative to baseline.

Default: blocker gates on; no-new-gate-failures on; all gates optional unless benchmark maturity supports strictness.

## Freeze policy

Hash evaluator identity and inputs: evaluator mode and acceptance settings; custom eval command for `--evaluator command`; `skill-benchmark` script and optional results file for `--evaluator skill-benchmark`; and every file/directory passed with `--benchmark-lock-path`. Use `--blocked-path` to stop Codex from editing evaluator files or fixtures, even inside the repo or target skill.

## Metric sources

Use one or more: static skill benchmark, activation suite, output conformance suite, packaging validator, golden examples, safety/negative prompts, human review. Strong autonomous runs should combine static score, fixed activation/output results, packaging validation, and safety/negative gates.

## Anti-overfitting

Do not delete failing tests, alter expected outputs, edit the evaluator unless the objective is eval design, accept when benchmark hash changed, or report prompt-pass rates without captured outputs. Keep a holdout prompt set for manual review and log rejected hypotheses to prevent repeated failed attempts.
