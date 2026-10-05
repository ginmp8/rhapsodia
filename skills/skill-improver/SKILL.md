---
name: skill-improver
description: "use when improving one existing agent skills-compatible package through a bounded evidence-backed experiment: preserve an immutable baseline, freeze deciding evidence, test one hypothesis or inseparable batch, materialize the smallest candidate, gate regressions independently, accept/reject from evidence, and freeze exact passing bytes. also use for caller-routed evolution candidate materialization and externally controlled self-improvement generations. do not use for net-new skills (skill-creator-juiced), end-to-end multi-specialist optimization/strategy (skill-booster), standalone maturity scoring/reporting (skill-benchmark), broad package-integrity hardening (skill-hardening), generic repository/application code, evaluator-fixture edits, or unbounded automation."
---

# Skill Improver

## Purpose, ownership, and selection

Own **bounded improvement execution for one existing skill**. Preserve an immutable baseline and frozen deciding evidence, diagnose from observed failures, test a falsifiable change, compare with the same evaluator, apply an independent regression gate, retain rejection evidence, and freeze only an accepted candidate.

Stay inside the target skill's existing responsibility. Never gain score by weakening activation, semantics, safety, compatibility, validation, evidence, fixtures, or authority boundaries. Do not discover or orchestrate a broad specialist catalog; the caller/orchestrator owns global strategy and final promotion.

Route elsewhere when the user's primary goal is: create/redesign a skill -> `skill-creator-juiced`; optimize a skill end to end across specialists/strategy -> `skill-booster`; produce a standalone benchmark/maturity report -> `skill-benchmark`; harden package integrity/readiness as the main objective -> `skill-hardening`; change ordinary application/repository code -> the relevant engineering skill.

Reproducibility means repeated runs on the same supported inputs/environment satisfy the same semantic contract and gates; subjective/model judgment need not produce identical prose. Evidence layers are distinct: **structural** (package/schema/hash), **behavioral** (executed scenarios), **runtime** (actual tool/app execution), and **perceptual** (independent subjective review). Never promote a weaker layer into a stronger claim.

## Mode router

| Mode | Select when | Contract |
|---|---|---|
| `benchmark-only` | establish/freeze a baseline for an improvement workflow or caller-directed comparison; not standalone maturity scoring | evaluate/report only; no mutation |
| `manual-patch` | one bounded hypothesis can be tested directly | baseline -> minimal candidate -> evaluate/gate -> accept/reject -> freeze |
| `automated-loop` | repeated bounded attempts are justified | clean worktree, frozen evaluator, finite budget, blocked paths, rollback, stop rule, supported adapter |
| `package-install` | validated candidate must be delivered/installed | validate/freeze first; stage/package/install atomically with hashes/receipt |
| `self-improvement` | this skill improves its own package | immutable external controller, isolated candidate, recursion depth 1 by default, external promotion gate, last-known-good |

## Core operating contract

Before mutation resolve exactly one target root, objective/mode, runtime capabilities (filesystem read/write, Python 3.10+ for bundled helpers, command execution, optional network/research, independent evaluation, artifact delivery), writable/protected scope, safety posture, finite budget, delivery paths, hypothesis source (`user|backlog|skill-hypothesis-discovery|fallback`), material source evidence, change-gate policy, and evaluator contract (metric/direction, hard gates, frozen/blocked paths, partitions, runtime identity, auxiliary metric when saturation matters). For marginal-value claims predeclare `no-skill`, `parent`, and `candidate` arms.

Defaults: snapshot before mutation; one bounded manual patch or at most three automated iterations; `--min-delta 1.0` constrains only the selected optimization metric and never overrides hard gates; mutate the target folder only; protect fixtures, expected outputs, evaluators, reports/evidence/packages/caches, `.git`, credentials, and secrets; snapshot material sources; require the runner change gate when available; freeze the final pass. Strong stochastic claims require repeated trials; promotion-sensitive claims require a controller-only holdout.

Non-negotiable invariants:
- evaluator/scenario/expected-output/scoring/blocked-path identity is frozen before candidate mutation; drift requires explicit re-baselining;
- diagnostics visible to the mutator, regression evidence, and promotion holdout are separate; holdout contamination invalidates promotion evidence;
- static or saturated scores are regression gates, not behavioral-improvement proof; add a non-saturated auxiliary metric when needed;
- scalar gains never override activation, safety, compatibility, evaluator integrity, hard gates, protected paths, or unauthorized capability/authority expansion;
- one diagnosed cause gets the smallest supported repair; rerun the same failed gate first; stop after two non-improving repairs without new evidence;
- self-improving candidates cannot edit the active controller, evaluator, or promote themselves;
- output/receipt paths must not alias protected inputs; validate/hash staged bytes before commit; receipts bind to committed bytes; any post-freeze edit reopens affected validation;
- command execution is host-neutral by default; Codex or other host adapters remain optional edges and cannot change the semantic acceptance contract.

## Quick-start workflow

1. **Establish** target, mode, scope, runtime, budget, delivery expectation, protected paths, and immutable baseline; self-improvement also freezes controller/generation/last-known-good identities.
2. **Freeze deciding evidence** and material source bytes; freeze an evaluation plan when tri-arm, stochastic, runtime-comparability, capability-delta, or holdout claims are material.
3. **Measure and diagnose** baseline metrics/gates/identities and concrete failure traces; use repeated paired trials only when reliability claims need them.
4. **Select one bounded hypothesis or inseparable batch** with intent (`repair|optimization|simplification|experiment`), mechanism, transformation/capability ids, expected effect, acceptance rule, rollback, and mutation owner; preserve supplied intent/ids/parent/prior evidence, and require `simplification` to preserve capability/quality gates.
5. **Materialize the smallest candidate** while preserving parent/transformation provenance and moving only genuinely mechanical variance into scripts/schemas/validators; caller-routed search follows [candidate execution](references/evolution-candidate-execution.md), otherwise follow [transformation/ablation](references/transformation-records-and-ablation.md).
6. **Evaluate and repair** with frozen identities; compute parent delta / no-skill Skill Lift only when those arms actually ran; run holdout only controller-side.
7. **Decide**: reject identity/protected-path drift, contamination, un-rebaselined material runtime drift, failed hard gates, weakened semantics/safety, blocking regressions, or unauthorized authority expansion; preserve rejection evidence and last-good state.
8. **Freeze and deliver** exact passing bytes; canonicalize destinations, stage/validate/hash, preserve recovery state on failure, package/install only after validation, and emit a receipt for committed bytes.
9. **Report truthfully** with identities, commands/results, accepted/rejected hypotheses, changed files, gate decision, evidence-layer limits, rollback/recovery, residual risk, and hashes only when validated.

## Direct branch resources

Load only the branch that can change the decision; all required Markdown is one hop from this file.
- Candidate acceptance/evidence: [evaluation contract](references/evaluation-contract.md), [severity lifecycle](references/severity-lifecycle.md), [reproducibility controls](references/reproducibility-controls.md), [transformation/ablation](references/transformation-records-and-ablation.md).
- Hypothesis/evaluation design: [hypothesis catalog](references/hypothesis-catalog.md), [benchmark integration](references/benchmark-integration.md), [harness design](references/harness-design.md), `evals/activation-scenarios.json`, evaluation/paired-trial templates and validators.
- Runtime/portability/delivery: [execution runbook](references/execution-runbook.md), [host portability](references/host-portability.md), [environment provenance](references/environment-provenance.md), [stochastic evaluation](references/stochastic-evaluation.md), [autoresearch adaptation](references/autoresearch-adaptation.md), bundled evidence/state/package scripts.
- Self-improvement: [self-improvement protocol](references/self-improvement-protocol.md) plus self-improvement receipt validator.
- Evolution/search: [candidate execution](references/evolution-candidate-execution.md), request/receipt validators, and `contracts/integration-manifest.json`.
- Final reporting: [report contract](references/report-template.md) and bundled report/patch/transformation/generation templates.

## Evolution/search compatibility

When a caller supplies an evolution request, preserve v2 identity (`request_signature`, base/donor parents, operator, transformations, expected capability effects), validate it before mutation, and return a validated **generation-receipt v3**. `skill-improver` owns candidate materialization only; population/search state, selection, and promotion remain external. Treat `contracts/integration-manifest.json` as a public compatibility surface.

## Stop Conditions

Stop/revert/return `blocked` or `not-run` when target/baseline identity is ambiguous or unsafe; required source truth/frozen evaluator/runtime/gate is unavailable; protected evidence changes; mutation requires blocked fixtures/secrets/unrelated paths; the same objective repair fails twice without new evidence; output aliases protected inputs; validation/package/source verification fails; or passing requires weakening a hard gate.

## Final Acceptance

Before success verify comparable frozen evaluators; no-skill control for marginal-value claims; controller-only holdout with explicit contamination state; repeated trials for stochastic claims; comparable or re-baselined runtime identity; no unauthorized capability delta; source snapshots unchanged; saturated metrics supported by auxiliary evidence; target validators/tests plus independent change gate pass; protected paths unchanged; modified scripts executed or syntax-checked; no post-freeze edits; artifact/receipt hashes match exact bytes; scenario rates come only from captured executions; and self-improvement preserves controller/promotion separation.

## Output Contract

For substantive mutating runs report target/mode/objective, baseline/evaluator/source identities, baseline/final metrics, selected/accepted/rejected hypothesis and transformation/capability refs, changed files, exact validation commands/outcomes, change-gate decision, protected paths, termination and rollback/recovery, arms/partitions/trials/runtime/contamination when applicable, final candidate identity, evidence-layer limits, residual risk, and validated package/receipt hashes. Search candidates also report request/parent/donor/operator identities and generation-receipt v3; self-improvement reports controller/generation/last-known-good and external promotion status.
