---
name: skill-hypothesis-discovery
description: use when asked to discover, generate, rank, triage, or plan testable improvement hypotheses for an existing agent skills-compatible skill package before mutation. consumes identified target evidence, benchmark/harness findings, validation logs, specialist reviews, gate results, and explicit evidence gaps to produce a small evidence-bound hypothesis backlog with deterministic eligibility, deduplication, ranking, and experiment selection. do not use it to edit or package the target, run benchmark or harness scoring, accept or reject concrete patches, or claim measured improvement without executed or supplied evidence.
---

# Skill Hypothesis Discovery

## Scope and mission

Convert identified evidence about one existing skill into a small, testable pre-mutation backlog. This skill plans; it never patches, packages, benchmarks, runs harness scoring, accepts candidates, or edits evaluators/fixtures/baselines. Plausibility is insufficient: a testable hypothesis needs identified evidence, causal mechanism, observable effect, available evaluator, and acceptance criteria. `gather-evidence` and `no-mutation-recommended` are valid outcomes.

Given the same target identity, evidence snapshot, mode, and constraints, preserve material taxonomy, eligibility, dedupe/conflict/dependency treatment, scoring inputs, tie-breaks, and bounded selection. Keep semantic judgment where interpretation is irreducible.

## Portability

Keep the Agent Skills package as the host-neutral semantic core. Use relative resources and capability-based runtime decisions; do not require ChatGPT/Codex, Claude, GitHub Copilot, Cursor, vendor-private APIs, fixed install paths, Bash, or a particular Python executable. `agents/openai.yaml` is optional adapter metadata.

## Required inputs and modes

Resolve target identity, evidence, caller context, protected constraints, metrics/evaluators, and output form. Unknown identities or measurements stay explicit; never invent them.

| Mode | Final cap | Selected cap |
|---|---:|---:|
| `backlog-discovery` | 8 | 3 |
| `deep-discovery` | 8 | 3 |
| `closure-discovery` | 5 | 2 |
| `evidence-gap-review` | 5 | 0 |

Default: `backlog-discovery`.

## Load on demand

- [references/discovery-method.md](references/discovery-method.md): full ordered discovery method, evidence statuses, saturation and stop rules.
- [references/hypothesis-schema.md](references/hypothesis-schema.md): v2 taxonomy/schema, score, tie-breaks, dependency/conflict semantics, limits.
- [references/integration-workflows.md](references/integration-workflows.md): handoffs and ownership.
- [scripts/validate_hypothesis_backlog.py](scripts/validate_hypothesis_backlog.py): deterministic v2 validator/ranker and `hypothesis_pool_id`.
- [contracts/integration-manifest.json](contracts/integration-manifest.json): peer-facing `skill-opt.hypothesis-pool` v2.
- [assets/templates/hypothesis-backlog.json.template](assets/templates/hypothesis-backlog.json.template), [assets/templates/hypothesis-report.md.template](assets/templates/hypothesis-report.md.template): output shapes.
- [examples/hypothesis-discovery-examples.md](examples/hypothesis-discovery-examples.md): calibration.
- [evals/activation-scenarios.json](evals/activation-scenarios.json): planned routing coverage.
- [tests/fixtures/discovery-regression-scenarios.json](tests/fixtures/discovery-regression-scenarios.json): domain regression fixtures.

## Workflow

1. Freeze one target identity and snapshot evidence with stable ids/provenance.
2. Classify signals, then each backlog item as exactly `testable-hypothesis`, `recommendation`, `evidence-gap`, or `unsupported-speculation`.
3. Require `hypothesis -> evidence refs -> mechanism -> observable effect -> evaluator -> acceptance criteria`; downgrade incomplete chains.
4. Dedupe by canonical semantic key; review near-duplicates; declare conflicts/dependencies before ranking.
5. Keep saturated metrics as regression gates. Without an active auxiliary metric, gather evidence or stop rather than optimize noise.
6. Rank only eligible hypotheses with `impact + confidence + testability - risk - ceil(cost / 2)` and the exact tie-breaks in [references/hypothesis-schema.md](references/hypothesis-schema.md). Respect mode caps and choose exactly one next experiment when testing is recommended.
7. Validate JSON v2 with `<PYTHON> scripts/validate_hypothesis_backlog.py --input <BACKLOG.json> --json-output <RESULT.json>` and hand off exact target/evidence/pool/hypothesis/evaluator/acceptance/dependency identities.

## Hard rules

No random search, mutation-by-taste, duplicate padding, unsupported `test-now`, unresolved dependency selection, conflicting simultaneous selection, target mutation, evaluator weakening, fabricated evidence, or behavioral-improvement claims from planned/static evidence. Freeze the deciding evaluator before downstream mutation. Prefer more evidence or no mutation over a forced experiment.

## Output contract

Return target/baseline identity, mode/caller, evidence snapshot/status, recommendation, evidence inspected/missing, metrics/evaluators, bounded backlog, selected next hypothesis, deferred/rejected/gap items, and downstream handoff. Use canonical JSON v2 for machine consumption and the report template for durable Markdown.

## Stop conditions

Stop with `gather-evidence`, `insufficient-evidence`, or `no-mutation-recommended` when target identity is inadequate; no causal/measurable hypothesis is supported; an evaluator cannot be frozen independently; a saturated metric lacks a useful auxiliary metric; effects are not observable; all candidates are duplicate/conflicted/blocked/dependent/unsupported; the mode cap is reached; or further work would be random search.

## Integration

`skill-booster`: run after baseline evidence. `skill-improver`: use when no bounded hypothesis exists or current evaluation is saturated/blocked. `skill-creator-juiced`: existing-skill redesign/quality-upgrade only. Never make `skill-harness`, `skill-benchmark`, or `skill-change-gate` depend on this skill.
