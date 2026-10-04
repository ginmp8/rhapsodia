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

Resolve target identity, evidence, caller context, protected constraints, metrics/evaluators, output form, and `research_policy` (`never`, `if-needed`, or `required`) when external evidence acquisition is relevant. Unknown identities or measurements stay explicit; never invent them. External research is capability-based and optional unless the caller explicitly requires it.

| Mode | Final cap | Selected cap |
|---|---:|---:|
| `backlog-discovery` | 8 | 3 |
| `deep-discovery` | 8 | 3 |
| `closure-discovery` | 5 | 2 |
| `evidence-gap-review` | 5 | 0 |

Default: `backlog-discovery`. `deep-discovery` means broader adversarial generation/critique over evidence; it does **not** imply external deep research or mandatory multi-agent execution.

## Load on demand

- [references/discovery-method.md](references/discovery-method.md): full ordered discovery method, evidence statuses, saturation and stop rules.
- [references/hypothesis-schema.md](references/hypothesis-schema.md): v2 taxonomy/schema, score, tie-breaks, dependency/conflict semantics, limits.
- [references/integration-workflows.md](references/integration-workflows.md): handoffs and ownership.
- [references/research-grounding.md](references/research-grounding.md): optional bounded research, source/finding provenance, falsification, discovery-vs-validation separation, and evidence-gap priority.
- [scripts/validate_hypothesis_backlog.py](scripts/validate_hypothesis_backlog.py): deterministic v2 validator/ranker and `hypothesis_pool_id`.
- [scripts/validate_research_discovery.py](scripts/validate_research_discovery.py): deterministic research-aware pre-handoff validator; additive and does not change the peer-facing v2 backlog contract.
- [contracts/integration-manifest.json](contracts/integration-manifest.json): peer-facing `skill-opt.hypothesis-pool` v2.
- [assets/templates/hypothesis-backlog.json.template](assets/templates/hypothesis-backlog.json.template), [assets/templates/hypothesis-report.md.template](assets/templates/hypothesis-report.md.template), [assets/templates/research-discovery.json.template](assets/templates/research-discovery.json.template): output shapes.
- [examples/hypothesis-discovery-examples.md](examples/hypothesis-discovery-examples.md): calibration.
- [evals/activation-scenarios.json](evals/activation-scenarios.json): planned routing coverage.
- [tests/fixtures/discovery-regression-scenarios.json](tests/fixtures/discovery-regression-scenarios.json): domain regression fixtures.

## Workflow

1. Freeze one target/baseline identity. Assess evidence sufficiency before freezing the discovery snapshot.
2. If a material source-resolvable gap blocks a causal/measurable hypothesis, follow `research_policy` and [references/research-grounding.md](references/research-grounding.md). Prefer target-local evidence for target-local facts; bounded external research is optional/capability-based unless explicitly required.
3. When research ran, freeze the research corpus, normalize atomic source -> finding links, separate discovery from validation/regression evidence, run a counterevidence/falsification pass, validate `research-discovery` v1, then freeze the normal v2 discovery evidence snapshot.
4. Classify signals, then each backlog item as exactly `testable-hypothesis`, `recommendation`, `evidence-gap`, or `unsupported-speculation`.
5. Require `hypothesis -> evidence refs -> mechanism -> observable effect -> evaluator -> acceptance criteria`; downgrade incomplete chains. Research-backed hypotheses additionally require attempted falsification and an independent/held-out deciding evaluator before v2 handoff.
6. Dedupe by canonical semantic key; review near-duplicates; declare conflicts/dependencies before ranking. In `deep-discovery`, adversarially critique candidates and search counterexamples before consolidation; serial execution remains valid.
7. Keep saturated metrics as regression gates. Without an active auxiliary metric, gather evidence or stop rather than optimize noise. Rank open evidence gaps with the bounded information-value/cost rule from `research-grounding.md` when that artifact is used.
8. Rank only eligible v2 hypotheses with `impact + confidence + testability - risk - ceil(cost / 2)` and the exact tie-breaks in [references/hypothesis-schema.md](references/hypothesis-schema.md). Respect mode caps and choose exactly one next experiment when testing is recommended.
9. Validate canonical JSON v2 with `<PYTHON> scripts/validate_hypothesis_backlog.py --input <BACKLOG.json> --json-output <RESULT.json>` and hand off exact target/evidence/pool/hypothesis/evaluator/acceptance/dependency identities.

## Hard rules

No random search, mutation-by-taste, duplicate padding, unsupported `test-now`, unresolved dependency selection, conflicting simultaneous selection, target mutation, evaluator weakening, fabricated evidence, candidate-aware validation evidence relabeled as discovery evidence, confirmation-only research, or behavioral-improvement claims from planned/static evidence. Freeze the deciding evaluator before downstream mutation. Do not reward novelty as a generic skill-optimization objective. Prefer more evidence or no mutation over a forced experiment.

## Output contract

Return target/baseline identity, mode/caller, evidence snapshot/status, recommendation, evidence inspected/missing, metrics/evaluators, bounded backlog, selected next hypothesis, deferred/rejected/gap items, and downstream handoff. When research ran, also return the frozen research/corpus identity, research policy/status, falsification/holdout status, and ranked evidence gaps. Use canonical JSON v2 for the peer-facing hypothesis pool; the additive research-discovery v1 artifact is pre-handoff evidence, not a replacement contract.

## Stop conditions

Stop with `gather-evidence`, `insufficient-evidence`, or `no-mutation-recommended` when target identity is inadequate; required research cannot complete; a material evidence gap remains unresolved; no causal/measurable hypothesis is supported; falsification cannot be attempted for a research-backed candidate; an independent/held-out evaluator cannot be frozen; a saturated metric lacks a useful auxiliary metric; effects are not observable; all candidates are duplicate/conflicted/blocked/dependent/unsupported; the mode cap is reached; or further work would be random search.

## Integration

`skill-booster`: run after baseline evidence. `skill-improver`: use when no bounded hypothesis exists or current evaluation is saturated/blocked. `skill-creator-juiced`: existing-skill redesign/quality-upgrade only. A deep/web research capability may supply a frozen corpus, and a Research Traceability-compatible workspace may supply stable source/finding identities; neither is a runtime dependency. Never make `skill-harness`, `skill-benchmark`, or `skill-change-gate` depend on this skill.
