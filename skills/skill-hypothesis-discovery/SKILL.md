---
name: skill-hypothesis-discovery
description: use when an existing Agent Skills-compatible skill already has identified evidence and the next decision is which bounded improvement hypotheses, evidence gaps, or no-mutation outcome should be tested before any target mutation. Produces a small evidence-bound hypothesis pool with deterministic eligibility, deduplication, dependency/conflict handling, ranking, and one next experiment. Do not use to improve, patch, package, benchmark, or score the skill, design evaluators after seeing candidates, accept/reject concrete patches, or create a net-new skill.
---

# Skill Hypothesis Discovery

## Mission and activation boundary

Turn identified evidence about exactly one existing skill into a small pre-mutation decision backlog. This skill plans only: it may classify, deduplicate, rank, and select hypotheses, but it never mutates/packages the target, runs benchmark or harness scoring, weakens/edits evaluators or fixtures, or accepts a concrete candidate.

Activate when evidence already exists and the unresolved question is **what bounded change, evidence collection step, or no-mutation decision should come next**. Do not activate for generic "improve this skill" execution, known repairs with a known correction, benchmark scoring, candidate gating, package delivery, or net-new skill design. `gather-evidence`, `insufficient-evidence`, and `no-mutation-recommended` are valid outcomes.

For the same target identity, evidence snapshot, mode, research policy, and constraints, preserve material taxonomy, eligibility, dedupe/conflict/dependency treatment, scoring inputs, tie-breaks, caps, and next-experiment selection. Semantic wording may vary; decision semantics may not drift without new evidence.

## Required inputs and mode router

Resolve one target/baseline identity, identified evidence and its provenance/status, caller context, protected constraints, metrics/evaluators, output form, and `research_policy` (`never`, `if-needed`, `required`) when external evidence could matter. Keep unknown identities/measurements explicit; never invent them.

| Mode | Use for | Final cap | Selected cap |
|---|---|---:|---:|
| `backlog-discovery` | normal bounded discovery | 8 | 3 |
| `deep-discovery` | broader adversarial generation/critique over the same evidence | 8 | 3 |
| `closure-discovery` | close remaining bounded hypotheses/gaps | 5 | 2 |
| `evidence-gap-review` | prioritize missing evidence only | 5 | 0 |

Default: `backlog-discovery`. `deep-discovery` does **not** require web research, multi-agent execution, or a different ranking contract.

## Eligibility and decision contract

Classify every item as exactly `testable-hypothesis`, `recommendation`, `evidence-gap`, or `unsupported-speculation`; only the first can be selected for testing. A `test-now` hypothesis must have identified evidence with status `measured|observed|derived|supplied`, a causal mechanism, observable effect tied to an active metric, an available frozen evaluator, explicit acceptance criteria, and no unresolved dependency. `planned|gap|unknown` evidence cannot justify `test-now`.

Keep saturated metrics as regression gates. If no active auxiliary metric can expose useful change, gather evidence or stop. Research-backed hypotheses additionally require a bounded counterevidence/falsification attempt plus an independent/held-out deciding evaluator before v2 handoff.

## Quick-start workflow

1. Freeze one target/baseline identity and assess whether current evidence is sufficient before freezing the discovery snapshot.
2. If a material source-resolvable gap blocks a causal/measurable hypothesis, apply `research_policy`; prefer target-local evidence for target-local facts. Research is optional unless explicitly required.
3. When research runs, freeze source/finding identities, separate discovery from validation/regression evidence, attempt falsification/counterevidence, validate the research artifact, then freeze the normal discovery evidence snapshot.
4. Classify signals and backlog item kinds; downgrade any incomplete `evidence -> mechanism -> observable -> evaluator -> acceptance` chain.
5. Dedupe by semantic key, merge near-duplicates, declare symmetric conflicts and prerequisites, and never select conflicting/dependent items together.
6. Rank only eligible hypotheses with `impact + confidence + testability - risk - ceil(cost / 2)` using the exact deterministic tie-breaks in `references/hypothesis-schema.md`.
7. Respect mode caps and identify exactly one `next_hypothesis_id` whenever testing is recommended; the shortlist is not a simultaneous mutation batch.
8. Validate canonical JSON v2 with `scripts/validate_hypothesis_backlog.py`; when research ran, validate `research-discovery` v1 first. Hand off exact target/evidence/pool/hypothesis/evaluator/acceptance/dependency identities.

## Critical invariants

- No random search, mutation-by-taste, duplicate padding, fabricated evidence, novelty bonus, unsupported `test-now`, unresolved dependency selection, or simultaneous conflicting selection.
- Never relabel candidate-aware validation evidence as discovery evidence without explicit re-baselining and a new identity.
- Never design/change a deciding evaluator after seeing candidate results, weaken a gate to make an item eligible, or claim behavioral improvement from planned/static evidence.
- Prefer more evidence or no mutation over a forced experiment. Freeze deciding evaluator identity before downstream mutation.
- Keep the package host-neutral: relative resources, capability-based execution, serial execution as a valid baseline, and optional host adapters only.

## Direct resource map

- [references/discovery-method.md](references/discovery-method.md): load for the ordered evidence-to-backlog pipeline, evidence statuses, saturation, deep-discovery, stop rules, and handoff sequence.
- [references/hypothesis-schema.md](references/hypothesis-schema.md): load when constructing/validating canonical v2 items, deterministic score/tie-breaks, dedupe keys, dependencies/conflicts, caps, and recommendation constraints.
- [references/research-grounding.md](references/research-grounding.md): load only when research/evidence-gap prioritization is active; owns source/finding roles, falsification, evaluator-independence, and research-discovery v1.
- [references/integration-workflows.md](references/integration-workflows.md): load for ownership boundaries and exact downstream handoff fields.
- `scripts/validate_hypothesis_backlog.py`: deterministic v2 validator/ranker and `hypothesis_pool_id`.
- `scripts/validate_research_discovery.py`: deterministic research pre-handoff validator; additive, never a replacement for v2.
- `contracts/integration-manifest.json`: owned peer-facing `skill-opt.hypothesis-pool` v2 contract.
- `assets/templates/`: canonical backlog/report/research shapes; `evals/` and `tests/fixtures/` are planned/regression assets, not proof of executed behavior.
- [examples/hypothesis-discovery-examples.md](examples/hypothesis-discovery-examples.md): calibration only, never benchmark evidence.

## Output contract

Return target/baseline identity, mode/caller, evidence snapshot/status, recommendation, evidence inspected/missing, metrics/evaluators, bounded backlog, selected next hypothesis, deferred/rejected/gap items, and exact downstream handoff. When research ran, also return corpus identity, research policy/status, falsification/holdout status, and ranked evidence gaps. Canonical peer output remains `skill-opt.hypothesis-pool` v2.

## Stop conditions

Stop with evidence collection/no mutation when identity/provenance is inadequate, required research cannot complete, no causal/measurable hypothesis is supported, falsification or independent evaluator requirements are unmet, all candidates are duplicate/conflicted/blocked/dependent/unsupported, active metrics are unavailable, effects are not observable, caps are reached, or further work would be speculative/random search.

## Ownership and integration

`skill-booster` may call this after baseline evidence; mutation belongs to the improvement owner, candidate acceptance to the change gate, and benchmark/harness scoring to their evidence owners. Never make those downstream owners depend on this skill at runtime.
