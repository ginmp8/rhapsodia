---
name: skill-quality-reviewer
description: Review, audit, score, compare, or validate existing Agent Skills-compatible packages or prior skill-review reports across ChatGPT/OpenAI, Codex, Claude, GitHub Copilot, Cursor, and other compatible hosts. Use for evidence-backed findings about activation, ownership, workflow correctness, architecture, progressive loading, obsolete compatibility, migration or runtime peer coupling, duplicated or contradictory contracts, structural noise, resource integration, validation gaps, package hygiene, portability, token efficiency, readiness, or remediation inputs. Do not use to implement fixes, create new skills, review ordinary application code, or perform security audits.
---

# Skill Quality Reviewer

## Mission and Boundary

Review one existing skill package as a connected operational system, not as isolated prose. Find defects that can change activation, routing, authority, execution, evidence, outputs, compatibility, portability, or package integrity, then produce an auditable review and self-contained correction input.

- Default to read-only review. Do not mutate or repackage the target unless a separate correction phase is explicitly authorized.
- Keep security outside this rubric. For bundled scripts, review correctness, determinism, error handling, path assumptions, runtime coupling, integration, and package behavior only; route secrets, authorization, permissions, threat models, dependency vulnerabilities, sandbox escape, and abuse resistance to a dedicated security skill.
- If the user wants implementation rather than review, finish the correction input and hand it to an improvement workflow instead of silently editing the target.

## Modes

| Mode | Use | Primary output |
|---|---|---|
| `full-review` | complete audit, score, readiness, remediation | report, weighted scorecard, findings, verdict, correction input |
| `legacy-audit` | obsolete compatibility, migrations, aliases, ownership drift, structural noise | legacy/ownership/compatibility matrices, findings, correction input |
| `quick-triage` | explicitly short review or intentionally small target | up to five highest-value findings and next checks |
| `compare-versions` | two inspectable packages or before/after candidate | capability deltas, regressions, improvements, acceptance verdict |
| `report-validation` | prior review report or remediation input | unsupported claims, missing evidence, structural/report defects |

Default to `full-review`. Use `legacy-audit` when historical behavior or compatibility is the subject. Use `compare-versions` only when both baselines are inspectable.

## Critical Invariants

- Tie every material finding to inspectable evidence; use `confirmed`, `likely`, `needs verification`, `planned`, or `out of scope` instead of filling gaps.
- Reconstruct the current canonical contract before classifying history; newest-looking or most-repeated text is not automatically authoritative.
- Treat keyword, filename, and deterministic legacy-signal matches as discovery leads only until owners, writers, readers, consumers, tests, validators, examples, packaging, and migration paths are traced.
- Classify legacy candidates as `current`, `migration-only`, `obsolete`, `duplicate`, `contradictory`, `noise`, or `blocked`; require explicit isolation for `migration-only` behavior.
- Recommend the smallest sufficient correction. Do not penalize unconventional structure without a behavioral, maintenance, evidence, or package-integrity consequence.
- Do not require optional folders or host adapters without a declared need. Keep portable-core requirements separate; `agents/openai.yaml` is optional unless OpenAI metadata is explicitly required.
- Separate normative conformance, package integrity, and operational quality. A pass in one layer never proves another.
- Separate static checklist/scoring from executed validation. A weighted score is an internal static quality indicator unless stronger evaluator evidence exists.
- For multi-platform claims, distinguish structural, host-semantic, runtime, and behavioral portability; never extrapolate one host's semantics to another.
- Produce a correction input that is self-contained and does not depend on the conversation, hidden reasoning, or unstated context.

## Quick Start

1. Resolve exactly one skill root, review mode, intended output, protected scope, and requested host/profile.
2. Declare the review profile: normative conformance, package integrity, operational quality, or a combination; pin a specification baseline only when claiming conformance.
3. When execution is available, build review identity/evidence outside the target and run the deterministic package preflight; treat structural findings as evidence and legacy-signal inventory as leads only.
4. Inventory the connected package and reconstruct current activation, boundaries, owner role, modes, inputs, outputs, schemas/states, tools, handoffs, stop conditions, versions, writers, readers, and consumers.
5. Define invariants, canonical sources, and bounded defect hypotheses before scoring. Trace common paths and failure paths, including silent fallback and dead branches.
6. Load only the branch-specific references below. Keep required Markdown one hop from this file; do not make a reference-to-reference chain the only route to required instructions.
7. Run semantic review, legacy/compatibility analysis when applicable, host-semantic review when requested, and capability-delta analysis for baseline/candidate comparisons.
8. Score only after findings. Apply hard gates, evidence coverage, confidence, and claim ceilings before deciding readiness or acceptance.
9. Write the mode-appropriate report, build the correction input, run report validation when possible, and close with inspected coverage, executed checks, unresolved gaps, and the bounded verdict.

## Inputs and Defaults

- Accept a skill folder, extracted ZIP, ZIP archive, repository path, supplied files, or prior review report.
- Infer purpose from frontmatter and package contents; answer in the user's language; inspect all available files under the selected root.
- Treat missing compatibility/consumer evidence as `blocked`, not as permission to preserve or remove by assumption.
- Keep generated reports, manifests, and validator outputs outside the target package.
- Resolve an available Python 3 launcher as `<PYTHON>` instead of assuming one executable name.
- Stop for an ambiguous root. If an intentionally partial target is supplied, proceed and state the limitation.

## Decision-Driven Resource Map

- Core investigation and closure: [`references/review-workflow.md`](references/review-workflow.md).
- Scoring, severity, gates, and readiness: [`references/review-rubric.md`](references/review-rubric.md).
- Evidence layers, calibration, identities, trials, and claim ceilings: [`references/evidence-and-calibration.md`](references/evidence-and-calibration.md).
- Legacy, migrations, compatibility, ownership, and structural noise: [`references/legacy-and-compatibility-audit.md`](references/legacy-and-compatibility-audit.md).
- Finding quality and confidence: [`references/finding-model.md`](references/finding-model.md).
- Baseline/candidate capability preservation and regression taxonomy: [`references/capability-delta-review.md`](references/capability-delta-review.md).
- Host portability and semantic-evidence boundaries: [`references/host-portability.md`](references/host-portability.md).
- Report shapes and required sections: [`references/report-contract.md`](references/report-contract.md).
- Copy-paste-ready remediation instructions: [`references/correction-input-contract.md`](references/correction-input-contract.md).
- Severity/legacy calibration examples: [`examples/review-scenarios.md`](examples/review-scenarios.md).

## Deterministic Helpers
- [`scripts/inspect_skill_package.py`](scripts/inspect_skill_package.py): structural/package preflight and discovery-only legacy-signal inventory.
- [`scripts/build_review_evidence_manifest.py`](scripts/build_review_evidence_manifest.py): dependency-free target/reviewer/evaluator/source fingerprinting; write output outside the target.
- [`scripts/validate_review_report.py`](scripts/validate_review_report.py): deterministic structural validation of the generated Markdown report.
- [`evals/activation-scenarios.json`](evals/activation-scenarios.json): planned activation/boundary scenarios only; never describe them as executed metrics.
- [`assets/templates/skill-review-report.md.template`](assets/templates/skill-review-report.md.template): full-review report skeleton.

## Special Evidence Rules
- Normalize activation-scenario coverage across supported `type`, `category`, `group`, and `expected_route` shapes before declaring missing coverage; do not emit `EVAL002` solely because a richer compatible schema is used.
- For model-judge evidence, record calibration status when decision-critical. Use bounded validator challenges only when their result can change a material finding or readiness claim.
- For baseline/candidate work, classify each material capability delta using `references/capability-delta-review.md`. More files, instructions, or scripts are not capability gains by themselves.
- If a candidate is self-generated, record supplied controller/baseline/candidate/generation provenance separately from capability classification; self-reported claims never replace independent evidence.
- Strong activation reliability or accuracy claims require repeated comparable trials or a lower claim ceiling.

## Review Priorities
Inspect in this order: package root/parseability; canonical sources and ownership; activation/boundaries; core workflow/output feasibility; implicit legacy acceptance and migration leakage; contradictions/duplicated contracts/ownership drift; broken or orphaned resources; validation/evidence discipline; package hygiene; documentation/token efficiency; cosmetic style last.

## Output Contract
Use [`references/report-contract.md`](references/report-contract.md). Every substantive review must include target/mode/scope, reconstructed current contract and canonical sources, invariants, review profile, evidence coverage/confidence, weighted scorecard with gate effects, severity-ranked findings with failure path and smallest fix, legacy/compatibility assessment, rejected hypotheses and positive signals, validation gaps, prioritized remediation, self-contained correction input, and a verdict bounded to the declared evidence profile.

For baseline/candidate comparison, also include an evidence-bound capability-delta matrix. For `legacy-audit`, always include legacy classification, ownership, compatibility, and runtime-coupling matrices. Do not call static presence/absence a behavioral improvement.

## Stop Conditions
Return `NEEDS_MORE_CONTEXT`, narrow the claim, or stop when the root is ambiguous; the canonical current contract cannot be reconstructed; essential compatibility/consumer/migration evidence is missing for a removal decision; two sources claim current authority with no resolving evidence; a requested behavioral/readiness claim requires execution that was not supplied or run; a prior report lacks enough target evidence; or the task is primarily a security audit.

Do not stop merely because the package is large. Bound inspected scope, report coverage, and continue with the highest-impact surfaces.
