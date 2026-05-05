# Evaluation Contract

## Lifecycle

Do not start improvement until a benchmark exists and is frozen.

```text
prepare benchmark -> run baseline -> freeze evaluator inputs -> discover or load hypothesis backlog -> test selected hypotheses
```

A benchmark may be created immediately before the loop, but candidate changes must use the same frozen benchmark. Do not alter tests, expected outputs, evaluator scripts, scenario results, scoring weights, or gate definitions during an improvement iteration. Hypothesis discovery may inspect benchmark/harness evidence, but it must not change evaluator inputs or claim measured improvement.

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





## Hypothesis discovery contract

Use a supplied bounded hypothesis first. When none is supplied, when the evaluator score is saturated, or when findings point to multiple possible candidate patches, load a hypothesis backlog from `skill-hypothesis-discovery` or a compatible JSON file before mutation. Discovery is planning evidence, not an accepted improvement.

Preferred JSON backlog shape:

```json
{
  "hypotheses": [
    {
      "id": "H001",
      "name": "Improve activation boundaries",
      "statement": "If negative activation boundaries are added, false positives should decrease without reducing target recall.",
      "evidence_signal": "ambiguous or adjacent prompts trigger the skill",
      "target_area": "activation",
      "files": ["SKILL.md"],
      "expected_effect": "lower false-positive rate",
      "validation": "activation and non-activation scenario suite",
      "constraints": ["do not weaken positive triggers"],
      "risk": 2,
      "confidence": 4,
      "testability": 5,
      "recommendation": "test-next"
    }
  ]
}
```

Use only hypotheses with a clear mechanism, evidence signal, bounded file scope, validation method, and rollback/gate expectation. Reject or defer cosmetic, duplicate, random, or low-evidence hypotheses. If discovery returns `no mutation recommended` or `gather evidence`, do not force a patch; report the blocker or create the requested evidence first.

## Structural change gate

Use a structural change gate as an acceptance check separate from the numeric evaluator. The gate may be performed by `skill-change-gate`, a reviewer, or a compatible command. It evaluates whether a candidate patch introduced blocking regressions in skill loading, activation, scope boundaries, local references, safety and authority, validation, packaging, evidence discipline, or output contracts.

Gate policy:

- `disabled`: do not run a structural change gate.
- `advisory`: record the gate result, but do not reject solely on gate warnings or failures; use for manual exploration.
- `required`: reject candidates when the gate fails, cannot run, or reports blocking regressions; use for automated-loop and self-improvement when a gate command or reviewer is available.

A compatible gate command should print JSON with this shape:

```json
{
  "status": "pass",
  "blocking_regressions": [],
  "material_concerns": [],
  "accepted_tradeoffs": [],
  "notes": []
}
```

`status` may be `pass`, `pass-with-warnings`, or `fail`. A `fail` status blocks acceptance when policy is `required`. `pass-with-warnings` may be accepted only when warnings are explicitly recorded as non-blocking trade-offs.

## Acceptance rule

Accept only when all configured conditions hold:

```text
same benchmark hash
and no blocked paths changed
and selected hypothesis has evidence-backed mechanism and validation
and candidate status/gates pass
and structural change gate passes when required
and candidate_score >= best_score + min_delta
```

for `higher-is-better`, or:

```text
same benchmark hash
and no blocked paths changed
and selected hypothesis has evidence-backed mechanism and validation
and candidate status/gates pass
and structural change gate passes when required
and candidate_score <= best_score - min_delta
```

for `lower-is-better`. Any evaluator gate failure, missing/invalid hypothesis source, required change-gate failure, evaluator drift, or locked-fixture drift rejects and reverts the candidate even if the number improves.

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
