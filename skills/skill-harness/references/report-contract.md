# Report Contract

Use for final responses or durable reports.

Required sections: mode/target; portability profile/runtime capabilities; target trust/execution policy; decision; evidence policy/source identities; immutable baseline snapshot identity; baseline inventory/audit/portability gates; harness plan with hypotheses, scenarios, reference-solution/oracle status, metamorphic relations, metrics, evaluators, gates; evaluator freeze and grader-calibration status; environment identity/comparability when material; stochastic trial/uncertainty evidence when claimed; trace/lineage and holdout-exposure status when applicable; evaluation-provenance identity when material; changes; validation commands/outcomes; before/after comparison; auxiliary metrics when static score is saturated; final candidate/package hashes; recovery/last-good status; residual risks/assumptions; recommendation; package/artifact path when produced.

Evidence labels: `measured` = command/test/validator/package/scenario executed; `derived` = inferred from target/context; `researched` = cited research; `proposed` = planned only; `unknown` = unavailable. Scenario pass rates, activation precision/recall, and behavioral conformance are measured only after prompts execute and evaluator results are captured.

File change groups: `SKILL.md`, `references/`, `scripts/`, `assets/templates/`, `examples/evals/`, optional host adapters (`agents/` or host extensions), and `packaging`.

Command format:

```text
PASS|FAIL|SKIPPED - <command or validator name>: <evidence path or concise result>
```

If a command cannot run, state failure and workaround separately. Do not convert failed commands into passes because related evidence exists.

Recommendation: exactly one of `accept: <reason>`, `accept with risks: <reason and risks>`, `reject: <blocking gates>`, or `plan only: <ready state and remaining work>`. Return package path only when the file exists and package report succeeds.
