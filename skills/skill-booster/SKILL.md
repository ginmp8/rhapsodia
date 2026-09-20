---
name: skill-booster
description: "use when optimizing, improving, benchmarking, hardening, compressing, validating, normalizing portability, packaging, or running explicit evidence-guided evolutionary/multi-candidate optimization on an existing Agent Skills-compatible or SKILL.md-based skill, including third-party skills downloaded from the internet, across ChatGPT/OpenAI, Codex, Claude, GitHub Copilot, Cursor, or another compatible host; owns global optimization orchestration, trust intake, specialist routing, bounded mutation/evaluation, optional Skill Evolution search, final promotion gates, freeze, and atomic packaging; do not use for net-new skill creation, generic repository refactors, or unsupported measured-improvement claims"
---

# Skill Booster

## Mission

Optimize one existing skill package end to end with evidence while keeping the workflow host-neutral. Use the open Agent Skills package model as the portable core, isolate host-specific adapters, and never assume a ChatGPT-, Claude-, Copilot-, Cursor-, or vendor-private invocation API. Preserve baseline/frozen evidence, benchmark/harness signals, reproducibility routing, bounded patches, change gates, validation, compression, hardening, final candidate freeze, deterministic packaging, and truthful readiness claims.

## Required inputs and defaults

Resolve or infer before mutation:

- `TARGET_SKILL_PATH`: folder or extracted zip with exactly one root `SKILL.md`.
- Mode: `audit-only`, `plan-only`, `apply-optimization`, `evolutionary-optimization`, `validation-only`, or `package`. Full optimization defaults to `apply-optimization`; use `evolutionary-optimization` only when the user explicitly requests multi-candidate/evolutionary search or an already-approved plan requires it.
- Objective: activation, output quality, architecture, docs, scripts, security, validation, hygiene, token cost, or complete optimization.
- Writable scope: target folder only unless narrowed.
- Protected paths: `.git`, secrets, credentials, fixtures, expected outputs, benchmark baselines, generated evidence/reports, old zips, read-only paths, unrelated repos, and frozen evaluator assets.
- Evaluator: target validator/CI, `skill-benchmark`, harness, static validator, or planned evaluator when execution is impossible.
- Final artifact: report, patched folder, validated `skill.zip`, or install-ready package.
- `SOURCE_CLASS`: classify the source as `trusted-owned`, `trusted-local`, or `external-untrusted-skill`. Downloaded/uploaded third-party skills default to `external-untrusted-skill` until intake completes.
- `TARGET_HOSTS`: hosts the result must support. `portable-core` is always mandatory for mutating optimization. For `complete optimization`, use `DEFAULT_MULTI_HOSTS = portable-core,openai,codex,claude,copilot,cursor` unless the user explicitly narrows support. A narrowed matrix must remain explicit and must not be described as fully multi-platform.
- `PYTHON`: an available Python 3 launcher chosen by the active host/environment (`python`, `python3`, `py -3`, or equivalent). Record the exact launcher used; do not assume one spelling. Bundled scripts require no third-party Python packages; they use the standard library plus bundled sibling modules.
- `skill-hypothesis-discovery`: required after baseline evidence; if no delegate is executable, apply its checklist and record evidence.
- `skill-change-gate`: required for candidate acceptance and final regression review; if no delegate is executable, apply its checklist and record evidence.
- `reproducibility-engineer`: conditionally required when the reproducibility decision gate finds a material controllable variance. Default applicable mode is `audit-only`; use `apply` only when reproducibility is the explicit objective or a selected bounded hypothesis is clearly owned by that specialist.
- `skill-evolution`: conditional search controller used only for `evolutionary-optimization`. Booster remains the global orchestrator and final promotion owner; Skill Evolution owns population/search state, lineage, recombination, non-dominance, novelty, survivor/finalist selection, and termination. It must not mutate target bytes or self-promote a candidate.
- Explicit specialist sequence: when the user names required specialists, invoke each available specialist; classify unavailable, blocked, unsafe, or not-applicable passes separately from checklist-only review.
- Self-improvement profile: when the target is improving itself, read `references/self-improvement-orchestration.md`; keep the controller immutable, route evidence providers proportionally, and prevent downstream specialists from becoming global orchestrators.
- `TARGET_CLASS`: classify the target as `deterministic-tool`, `code-engineering`, `research-analytic`, `orchestration-meta`, `subjective-design`, or `mixed-other`; use the class for routing and evidence interpretation, never as a score.
- Pre-evolution state: for complex/full optimization, maintain capability, transformation, experiment, and evaluation artifacts outside the target worktree unless the target explicitly owns such contracts. These artifacts prepare future multi-candidate search but do not imply that evolutionary mode is active.

## Mode selection

- `audit-only`: inspect maturity, risks, and candidate hypotheses; no mutation or package claim.
- `plan-only`: produce backlog, sequence, and gates before edits.
- `apply-optimization`: mutate the target with accepted bounded patches, then validate.
- `evolutionary-optimization`: keep the canonical optimization strategy as a protected comparator, invoke `skill-evolution` with a validated handoff, generate/evaluate candidates through existing mutation/evaluation owners, then independently prove/promote the selected finalist(s). Do not silently fall back to this expensive mode from ordinary optimization.
- `validation-only`: check an already changed target; write reports outside the target only.
- `package`: build `skill.zip` only from a validated target; repair first only when safe and in scope.

## Resource loading

Load only phase-relevant files:

- [references/optimization-workflow.md](references/optimization-workflow.md): six canonical phases, provider/mutator ordering, and gates.
- [references/pre-evolution-foundation.md](references/pre-evolution-foundation.md): target classes, capability map, change-intent taxonomy, transformation/experiment registries, evaluation ladder, ablation, promotion separation, and evolutionary-readiness gate.
- [references/evolutionary-search-routing.md](references/evolutionary-search-routing.md): optional `skill-evolution` handoff, authority boundary, search inputs/outputs, canonical comparator, and final promotion return path.
- [references/integration-impact-contract.md](references/integration-impact-contract.md): machine-readable cross-skill contract manifests, producer/consumer version checks, public-surface change detection, and ecosystem-compatibility claims.
- [references/specialist-passbook.md](references/specialist-passbook.md): required pass sequence, statuses, and skip rules.
- [references/evaluation-contract.md](references/evaluation-contract.md): freeze rules, metrics, hypothesis records, reproducibility routing evidence, and change-gate integration.
- [references/reproducibility-routing.md](references/reproducibility-routing.md): material-signal test, optional `reproducibility-engineer` modes, ownership, and decision record.
- [references/self-improvement-orchestration.md](references/self-improvement-orchestration.md): global provider routing for self-improvement, evidence ownership, sequencing, and anti-coupling rules.
- [references/host-compatibility.md](references/host-compatibility.md): portable Agent Skills core, default host matrix, capability model, installation/discovery notes, Python launcher policy, and optional host adapters.
- [references/external-skill-intake.md](references/external-skill-intake.md): quarantine/trust preflight for downloaded or otherwise external skill packages before any target-owned executable code is run.
- [references/mutation-and-safety-policy.md](references/mutation-and-safety-policy.md): allowed edits, blocked paths, rollback, and security floor.
- [references/integrity-and-recovery.md](references/integrity-and-recovery.md): immutable source snapshots, VCS evidence identity, output alias preflight, last-known-good preservation, recovery, and durable receipts.
- [references/reporting-contract.md](references/reporting-contract.md): final report sections and evidence language.
- [scripts/validate_skill_booster.py](scripts/validate_skill_booster.py): dependency-free structural validator and target preflight with stable machine-readable diagnostic codes.
- [scripts/inspect_external_skill.py](scripts/inspect_external_skill.py): static external-skill trust intake for a directory or ZIP; inventories provenance/security/host-coupling risks without executing target code.
- [scripts/validate_portability.py](scripts/validate_portability.py): validates the portable core and requested host profiles without requiring vendor-private APIs.
- [scripts/run_activation_harness.py](scripts/run_activation_harness.py): deterministic activation-scenario schema/coverage check; not live LLM precision evidence.
- [scripts/validate_specialist_reconciliation.py](scripts/validate_specialist_reconciliation.py): hard gate for user-required specialist sequence reconciliation before final readiness or package claims.
- [scripts/validate_reproducibility_decision.py](scripts/validate_reproducibility_decision.py): validates the conditional reproducibility routing record before hypothesis discovery.
- [scripts/validate_pre_evolution_state.py](scripts/validate_pre_evolution_state.py): validates capability-map, transformation-registry, experiment-registry, and evaluation-plan artifacts plus cross-artifact references.
- [scripts/validate_evolution_handoff.py](scripts/validate_evolution_handoff.py): validates Booster -> Skill Evolution search handoff and returned finalist/promotion envelope structure.
- [scripts/build_evolution_contract.py](scripts/build_evolution_contract.py): compiles canonical Booster pre-evolution artifacts into the Skill Evolution v2 search contract without leaking Booster-internal schemas into the search controller.
- [scripts/analyze_integration_impacts.py](scripts/analyze_integration_impacts.py): validates `contracts/integration-manifest.json`, detects unversioned public-surface changes, and checks known peer consumers/providers before ecosystem-safe finalization.
- [scripts/build_candidate_evaluation.py](scripts/build_candidate_evaluation.py): normalizes frozen Benchmark/Harness evidence plus hard-gate results into the Skill Evolution candidate-evaluation v2 envelope before returning evidence to the search controller.
- [assets/templates/evolution-handoff.json.template](assets/templates/evolution-handoff.json.template): portable handoff shape for explicit evolutionary mode.
- [assets/templates/capability-map.json.template](assets/templates/capability-map.json.template), [assets/templates/transformation-registry.json.template](assets/templates/transformation-registry.json.template), [assets/templates/experiment-registry.json.template](assets/templates/experiment-registry.json.template), and [assets/templates/evaluation-plan.json.template](assets/templates/evaluation-plan.json.template): portable pre-evolution interchange templates.
- [scripts/freeze_candidate.py](scripts/freeze_candidate.py): freezes or verifies the exact final candidate after the last passing validation.
- [scripts/snapshot_sources.py](scripts/snapshot_sources.py): captures exact external source bytes before analysis and verifies source/snapshot identity before acceptance.
- [scripts/package_skill.py](scripts/package_skill.py): validates with the booster validator, can enforce a reconciliation ledger, creates a deterministic temporary archive, verifies it, emits hashes, and atomically replaces `skill.zip` only on success.
- [assets/templates/optimization-report.md.template](assets/templates/optimization-report.md.template): reusable report template.
- [examples/sample-optimization-run.md](examples/sample-optimization-run.md): calibrated compact run.
- [evals/activation-scenarios.json](evals/activation-scenarios.json): planned activation, non-activation, ambiguous, and edge coverage.

## Workflow

Use `references/optimization-workflow.md` as the detailed contract. The canonical architecture is six phases; the passbook is an execution ledger inside those phases.

1. **Establish**: resolve one target, source trust, host/runtime capabilities, `TARGET_CLASS`, writable/protected scope, portable-core requirements, baseline identity, evaluator/scenario identity, and material external-source snapshots. Run Booster-owned structural/trust/portability preflight before target-owned code when required. Build or consume a capability map when semantic-loss risk is material. If the target declares `contracts/integration-manifest.json` or exposes machine-readable handoffs/CLIs consumed by peer skills, preserve the baseline manifest and resolve available peer roots/catalog for later impact gating.
2. **Diagnose**: run the evidence providers needed for the target class and touched surfaces. Initial benchmark/harness and the reproducibility decision happen here. Quality, architecture/context, activation/prompt, consistency, docs, code, security, validation, cleanup, and token specialists are read-only/audit/checklist providers by default in this phase. They emit evidence; they do not independently rewrite the candidate.
3. **Select**: reconcile provider evidence by ownership, classify proposed work as `repair`, `optimization`, or `experiment`, run `skill-hypothesis-discovery`, and choose one bounded hypothesis/batch. Record capability refs, expected effect, evaluator, acceptance rule, rollback, mutation owner, and transformation id before mutation.
4. **Mutate**: create or use an isolated candidate and allow exactly one declared owner for the transformation batch. Default owner is `skill-improver`; `reproducibility-engineer` may own a bounded `invoke-apply` batch; another specialist may own a batch only when explicitly delegated and within its contract. Never let multiple providers silently co-edit the same batch.
5. **Evaluate / Search branch**: in canonical mode, use the staged ladder from `references/pre-evolution-foundation.md`: `L0-structural` -> `L1-deterministic` -> `L2-focused` -> optional `L3-harness` -> optional `L4-benchmark` -> optional `L5-holdout`. In `evolutionary-optimization`, validate the v2 handoff, compile canonical pre-evolution artifacts with `scripts/build_evolution_contract.py`, validate the resulting Skill Evolution v2 search contract with the search controller, keep the canonical result/reference in every comparison, service candidate-generation/evaluation requests through the existing owners, and receive finalists without delegating final promotion authority. Fail required lower levels before spending on higher ones. Run `skill-change-gate` independently per material candidate and retain accepted, rejected, reverted, and inconclusive experiment records.
6. **Prove**: perform hardening and affected revalidation, final `skill-change-gate`, final benchmark/holdout when the claim requires them, final token/readiness closure, source/evaluator verification, candidate freeze, portability closure, and atomic packaging. Before an ecosystem-safe/package claim, run the integration-impact gate for any declared or discovered cross-skill contract surface. A known incompatible consumer/provider is blocking; missing peer evidence means integration compatibility is `not-proven`, not `pass`. Separate target-candidate promotion from any future Booster workflow-policy promotion; a single target win never changes canonical policy.

For `complete` / `full` optimization, every material actionable finding from Diagnose or final closure must end as `fixed`, `rejected`, `accepted-trade-off`, `blocked`, or `not-applicable`. Do not report complete optimization while a material finding remains only follow-up/planned/deferred. A material token-efficiency finding therefore opens another bounded transformation batch and affected revalidation rather than being silently deferred.

For complete/full optimization, validate the pre-evolution artifacts when produced:

```text
<PYTHON> scripts/validate_pre_evolution_state.py \
  --capability-map <WORK>/capability-map.json \
  --transformation-registry <WORK>/transformation-registry.json \
  --experiment-registry <WORK>/experiment-registry.json \
  --evaluation-plan <WORK>/evaluation-plan.json
```

The canonical workflow remains single-candidate by default. Evolutionary semantics are implemented only through the explicit `evolutionary-optimization` branch and the separate `skill-evolution` search controller. Never execute population search implicitly for an ordinary optimization request.
## Output contract

Final reports must include:

1. target skill path, mode, objective, requested hosts, resolved host capabilities, and exact Python launcher used;
2. baseline inventory, evaluator, score, gates, warnings, frozen inputs, and protected blocked paths;
3. required specialist sequence reconciliation, including:
   - required count;
   - invoked-skill count;
   - checklist-only count;
   - blocked count;
   - unavailable count;
   - not-applicable count;
   - not-run count;
   - full sequence satisfied: yes/no;
   - finalization allowed: yes/no;
4. specialist pass ledger with status, execution_type, and evidence;
5. reproducibility decision state, material signals, selected mode, specialist invocation status, downstream owner, and decision-validator result;
6. hypothesis-discovery status, candidate backlog count, selected hypotheses, and deferred hypotheses;
7. accepted/rejected hypotheses with files, expected effect, validation, change-gate decision, and evidence;
8. material finding closure ledger with terminal disposition (`fixed`, `rejected`, `accepted-trade-off`, `blocked`, `not-applicable`) and evidence;
9. required repairs kept without measured improvement;
10. files changed by phase;
11. protected paths respected statement;
12. validation commands and pass/fail/not-run outcomes;
13. before/after benchmark or static score when measured;
14. skill-change-gate and final skill-change-gate status;
15. final benchmark result;
16. portability matrix for `portable-core`, OpenAI/ChatGPT, Codex, Claude, GitHub Copilot, and Cursor (or the explicitly narrowed target set), including evidence level, optional adapter status, degradation, and blocked/unavailable capabilities;
17. total/local token deltas, local trade-offs, and final token-efficiency closure;
18. final candidate manifest identity and freeze verification;
19. source snapshot/provenance identity and final source verification when material external evidence was used;
20. package path, candidate hash, archive hash, receipt version/stage, atomic-delivery status, last-known-good preservation, and recovery paths only when `skill.zip` exists and package validation passed;
21. remaining risks, assumptions, rollback notes, and next hypothesis or no-mutation recommendation;
22. for self-improvement, controller/baseline/candidate identities, selected evidence providers with ownership/status, promotion receipt status, and confirmation that no downstream specialist re-owned global orchestration;
23. target class and capability-map status when material;
24. repair/optimization/experiment classification for accepted candidate work;
25. transformation registry and experiment registry identities/counts for work performed;
26. highest evaluation-ladder level reached for the accepted candidate and why higher levels were or were not required;
27. target-promotion status kept separate from any workflow-policy recommendation;
28. integration-impact status, peer catalog coverage, changed exported contract surfaces, incompatible/unresolved consumers, and whether ecosystem compatibility is proven;
29. for evolutionary mode: validated search handoff identity, search id/budget, candidate count, canonical comparator identity, search termination reason, Pareto/finalist ids, highest evidence level per finalist, and the Booster-owned final promotion decision.

Use `measured` only for executed commands, validators, scenario results, package checks, or supplied data.

Use `observed`, `inferred`, `planned`, `checklist-only`, or `blocked` for other evidence.

Do not claim benchmark improvement, specialist execution, security review, scenario pass rate, package readiness, full specialist sequence satisfaction, token reduction, or final readiness without evidence.

Manual checklist review must never be described as a specialist invocation.

## Stop conditions

Stop before mutation when an `external-untrusted-skill` has not completed the trust preflight; the target has zero/multiple root `SKILL.md` files; a multi-platform claim depends on host-private core instructions that have not been isolated or adapted; a required deterministic gate needs Python 3 or another declared runtime that the active host cannot execute; edits touch protected paths; measured improvement is required but no evaluator can be frozen; material external source evidence cannot be snapshotted or pinned safely; source truth is missing and a patch would invent facts; no evidence-backed hypothesis exists; the reproducibility gate is applicable but required evidence cannot be frozen safely; `skill-change-gate` finds an unfixable blocking regression; validation fails and cannot be fixed in scope; final freeze verification fails; package/report outputs alias protected inputs or each other; packaging would include secrets, caches, generated reports/evidence, old zips, or files outside the final skill folder; or `evolutionary-optimization` was explicitly requested but a valid Skill Evolution handoff/search controller/result cannot be established without fabricating search execution.

## Finalization checklist

Before completion, confirm: when evolutionary mode ran, its handoff/result validates, baseline/canonical references stayed available, candidate lineage is identity-bound, no hard-gate failure was promoted, holdout blindness was preserved when claimed, and final promotion remained Booster-owned; target class is recorded; pre-evolution artifacts used by the run validate when present; capability-loss-sensitive work has an evidence-backed capability map or explicit reason it was unnecessary; every mutation batch has one declared owner and a repair/optimization/experiment classification; rejected/inconclusive experiments are retained rather than rewritten as successes; source trust classification is recorded; external-untrusted intake completed before target code execution; `portable-core` validation passed; complete optimization produced an explicit result for OpenAI, Codex, Claude, Copilot, and Cursor unless the user deliberately narrowed the matrix; every host claimed as validated has matching evidence; the portable core does not require vendor-private tool names or installation paths; optional host adapters are not prerequisites; reproducibility routing was explicitly classified and its decision record validated; required specialist reconciliation passed when supplied; frontmatter is lowercase hyphen-case; activation/non-activation/ambiguous/edge scenarios exist or are planned; local refs resolve; resources are integrated or retained; no scaffold, caches, old packages, secrets, or generated noise remain; modified scripts ran or blockers are stated; discovery precedes improvement claims; material patches have gate decisions; material external evidence was snapshotted/pinned and reverified when applicable; compression was revalidated; local token growth is compressed or accepted as semantic trade-off; final token closure preserves activation, safety, validation, output, stop, routing, and evidence duties; final gate has no blocking regression; final benchmark separates measured from planned checks; final candidate freeze verifies immediately before packaging; package/report alias preflight passed; package validation and committed hash receipt pass before sharing `skill.zip`; last-known-good/recovery guarantees were preserved; no target edit occurred after the final verified freeze.
