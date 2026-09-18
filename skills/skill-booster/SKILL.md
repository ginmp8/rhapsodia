---
name: skill-booster
description: "use when optimizing, improving, benchmarking, hardening, compressing, validating, or packaging an existing Agent Skills-compatible or SKILL.md-based skill across ChatGPT/Codex, Claude, GitHub Copilot, Cursor, or another compatible host; runs evidence-driven specialist routing, optional reproducibility engineering, bounded changes, cross-host portability checks, validation, final freeze, atomic packaging, and truthful readiness reporting; do not use for net-new skill creation, generic repository refactors, or unsupported measured-improvement claims"
---

# Skill Booster

## Mission

Optimize one existing skill package end to end with evidence while keeping the workflow host-neutral. Use the open Agent Skills package model as the portable core, isolate host-specific adapters, and never assume a ChatGPT-, Claude-, Copilot-, Cursor-, or vendor-private invocation API. Preserve baseline/frozen evidence, benchmark/harness signals, reproducibility routing, bounded patches, change gates, validation, compression, hardening, final candidate freeze, deterministic packaging, and truthful readiness claims.

## Required inputs and defaults

Resolve or infer before mutation:

- `TARGET_SKILL_PATH`: folder or extracted zip with exactly one root `SKILL.md`.
- Mode: `audit-only`, `plan-only`, `apply-optimization`, `validation-only`, or `package`. Full optimization means `apply-optimization`, validation, then packaging when gates pass.
- Objective: activation, output quality, architecture, docs, scripts, security, validation, hygiene, token cost, or complete optimization.
- Writable scope: target folder only unless narrowed.
- Protected paths: `.git`, secrets, credentials, fixtures, expected outputs, benchmark baselines, generated evidence/reports, old zips, read-only paths, unrelated repos, and frozen evaluator assets.
- Evaluator: target validator/CI, `skill-benchmark`, harness, static validator, or planned evaluator when execution is impossible.
- Final artifact: report, patched folder, validated `skill.zip`, or install-ready package.
- `TARGET_HOSTS`: hosts the result must support. Default to `portable-core`; add `openai`, `claude`, `copilot`, and/or `cursor` only when requested or when portability is part of the objective.
- `PYTHON`: an available Python 3 launcher chosen by the active host/environment (`python`, `python3`, `py -3`, or equivalent). Record the exact launcher used; do not assume one spelling. Bundled scripts require no third-party Python packages; they use the standard library plus bundled sibling modules.
- `skill-hypothesis-discovery`: required after baseline evidence; if no delegate is executable, apply its checklist and record evidence.
- `skill-change-gate`: required for candidate acceptance and final regression review; if no delegate is executable, apply its checklist and record evidence.
- `reproducibility-engineer`: conditionally required when the reproducibility decision gate finds a material controllable variance. Default applicable mode is `audit-only`; use `apply` only when reproducibility is the explicit objective or a selected bounded hypothesis is clearly owned by that specialist.
- Explicit specialist sequence: when the user names required specialists, invoke each available specialist; classify unavailable, blocked, unsafe, or not-applicable passes separately from checklist-only review.

## Mode selection

- `audit-only`: inspect maturity, risks, and candidate hypotheses; no mutation or package claim.
- `plan-only`: produce backlog, sequence, and gates before edits.
- `apply-optimization`: mutate the target with accepted bounded patches, then validate.
- `validation-only`: check an already changed target; write reports outside the target only.
- `package`: build `skill.zip` only from a validated target; repair first only when safe and in scope.

## Resource loading

Load only phase-relevant files:

- [references/optimization-workflow.md](references/optimization-workflow.md): ordered phases and gates.
- [references/specialist-passbook.md](references/specialist-passbook.md): required pass sequence, statuses, and skip rules.
- [references/evaluation-contract.md](references/evaluation-contract.md): freeze rules, metrics, hypothesis records, reproducibility routing evidence, and change-gate integration.
- [references/reproducibility-routing.md](references/reproducibility-routing.md): material-signal test, optional `reproducibility-engineer` modes, ownership, and decision record.
- [references/host-compatibility.md](references/host-compatibility.md): portable Agent Skills core, host capability model, installation/discovery notes, Python launcher policy, and optional host adapters.
- [references/mutation-and-safety-policy.md](references/mutation-and-safety-policy.md): allowed edits, blocked paths, rollback, and security floor.
- [references/integrity-and-recovery.md](references/integrity-and-recovery.md): immutable source snapshots, VCS evidence identity, output alias preflight, last-known-good preservation, recovery, and durable receipts.
- [references/reporting-contract.md](references/reporting-contract.md): final report sections and evidence language.
- [scripts/validate_skill_booster.py](scripts/validate_skill_booster.py): dependency-free structural validator and target preflight with stable machine-readable diagnostic codes.
- [scripts/validate_portability.py](scripts/validate_portability.py): validates the portable core and requested host profiles without requiring vendor-private APIs.
- [scripts/run_activation_harness.py](scripts/run_activation_harness.py): deterministic activation-scenario schema/coverage check; not live LLM precision evidence.
- [scripts/validate_specialist_reconciliation.py](scripts/validate_specialist_reconciliation.py): hard gate for user-required specialist sequence reconciliation before final readiness or package claims.
- [scripts/validate_reproducibility_decision.py](scripts/validate_reproducibility_decision.py): validates the conditional reproducibility routing record before hypothesis discovery.
- [scripts/freeze_candidate.py](scripts/freeze_candidate.py): freezes or verifies the exact final candidate after the last passing validation.
- [scripts/snapshot_sources.py](scripts/snapshot_sources.py): captures exact external source bytes before analysis and verifies source/snapshot identity before acceptance.
- [scripts/package_skill.py](scripts/package_skill.py): validates with the booster validator, can enforce a reconciliation ledger, creates a deterministic temporary archive, verifies it, emits hashes, and atomically replaces `skill.zip` only on success.
- [assets/templates/optimization-report.md.template](assets/templates/optimization-report.md.template): reusable report template.
- [examples/sample-optimization-run.md](examples/sample-optimization-run.md): calibrated compact run.
- [evals/activation-scenarios.json](evals/activation-scenarios.json): planned activation, non-activation, ambiguous, and edge coverage.

## Workflow

1. **Preflight, host capabilities, and inventory**: confirm one root `SKILL.md`; read [references/host-compatibility.md](references/host-compatibility.md); resolve `TARGET_HOSTS`, writable filesystem/process capabilities, specialist-dispatch capability, and `PYTHON`. Run `<PYTHON> scripts/validate_skill_booster.py --target <TARGET_SKILL_PATH>`. When cross-host portability is requested or claimed, also run `<PYTHON> scripts/validate_portability.py --target <TARGET_SKILL_PATH> --hosts <HOSTS>`. Inventory core dirs, optional host adapters, validators, packages, and generated files. Do not treat `agents/openai.yaml`, Cursor-only frontmatter, Claude paths, Copilot paths, or any vendor-private API as part of the portable core.
2. **Baseline and freeze**: use the strongest available evaluator. Freeze scenarios, expected outputs, scoring config, validator scripts, benchmark inputs, fixtures, generated baseline reports, and blocked paths. When external files or repository evidence materially determine hypotheses or acceptance, capture the exact source bytes before analysis with `scripts/snapshot_sources.py` and prefer immutable VCS object reads for pinned revisions. Record score, gates, warnings, command, timestamp, source identity, and hashes when practical. For compatible activation scenarios, run `<PYTHON> scripts/run_activation_harness.py --scenarios <TARGET_SKILL_PATH>/evals/activation-scenarios.json --json` and label it schema/coverage only.
3. **Specialist sequence and reproducibility routing**: dispatch named specialists through the active host's native skill/delegation mechanism when available; never assume a specific tool name or vendor API. If a host cannot invoke a specialist, classify it using the passbook instead of fabricating execution. Run, apply by checklist, block, or mark not-applicable for every pass. After `skill-creator-juiced`, initial `skill-benchmark`, and `skill-harness`, evaluate [references/reproducibility-routing.md](references/reproducibility-routing.md) before `skill-hypothesis-discovery`. Record exactly one state: `invoke-audit`, `invoke-apply`, `not-applicable`, `blocked`, or `unavailable`; validate the decision with `<PYTHON> scripts/validate_reproducibility_decision.py <DECISION_JSON>`. When applicable and available, actually invoke `reproducibility-engineer`; checklist-only never counts as invocation. Then continue with `skill-hypothesis-discovery`, `skill-improver`, `skill-change-gate`, architecture/context/activation/prompt/consistency/docs/code/security/testing/cleanup/token passes, post-compression validation, hardening, final change gate, final benchmark, improver closure, and final token-efficiency closure. When the user supplies a required sequence, reconcile actual specialist invocations with `<PYTHON> scripts/validate_specialist_reconciliation.py --ledger <LEDGER_JSON>` before any completion, readiness, or full-sequence claim.
4. **Hypotheses and patches**: generate 5-10 evidence-backed hypotheses, including applicable reproducibility findings, dedupe/rank, select top 3-5 and next 1-3 to test. After `invoke-audit`, hypothesis discovery ranks the reproducibility findings and `skill-improver` normally owns selected patches. After `invoke-apply`, `reproducibility-engineer` owns only that bounded transformation batch and `skill-change-gate` must pass before the batch is accepted. Record changed files, expected effect, validation, gate decision, accept/reject/revert decision, and evidence for each material change.
5. **Validation, compression, hardening, and freeze**: rerun frozen evaluators and target validators after edits, cleanup, and compression. If a source snapshot was captured, verify it before acceptance; a changed live source requires evaluating the frozen snapshot or explicit re-baselining. Token closure checks total, per-file, and matching Markdown-section deltas; local growth must be compressed, accepted as semantic trade-off, or rejected. After the last passing final gate, freeze the candidate with `<PYTHON> scripts/freeze_candidate.py freeze --target <TARGET_SKILL_PATH> --out <WORK>/candidate-manifest.json`. Any later target edit invalidates the freeze and requires affected validation plus a new manifest.
6. **Package and close**: immediately before packaging, verify the frozen candidate with `<PYTHON> scripts/freeze_candidate.py verify --target <TARGET_SKILL_PATH> --manifest <WORK>/candidate-manifest.json`. Package only when verification, validation, source-identity checks when applicable, and required specialist reconciliation pass. Use `<PYTHON> scripts/package_skill.py --target <TARGET_SKILL_PATH> --output <OUTPUT_DIR>/skill.zip --report <REPORT_PATH>`; add `--reconciliation-ledger <LEDGER_JSON>` when required and `--portability-hosts <HOSTS>` when multi-platform readiness is part of the acceptance contract. Preflight package/report paths before mutation. The packager must commit archive+success receipt transactionally, preserve last-known-good archive/receipt on failure, preserve recovery evidence if rollback is incomplete, and bind hashes to the exact delivered archive.

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
8. required repairs kept without measured improvement;
9. files changed by phase;
10. protected paths respected statement;
11. validation commands and pass/fail/not-run outcomes;
12. before/after benchmark or static score when measured;
13. skill-change-gate and final skill-change-gate status;
14. final benchmark result;
15. requested-host portability results, optional adapter status, and blocked/unavailable capabilities;
16. total/local token deltas, local trade-offs, and final token-efficiency closure;
17. final candidate manifest identity and freeze verification;
18. source snapshot/provenance identity and final source verification when material external evidence was used;
19. package path, candidate hash, archive hash, receipt version/stage, atomic-delivery status, last-known-good preservation, and recovery paths only when `skill.zip` exists and package validation passed;
20. remaining risks, assumptions, rollback notes, and next hypothesis or no-mutation recommendation.

Use `measured` only for executed commands, validators, scenario results, package checks, or supplied data.

Use `observed`, `inferred`, `planned`, `checklist-only`, or `blocked` for other evidence.

Do not claim benchmark improvement, specialist execution, security review, scenario pass rate, package readiness, full specialist sequence satisfaction, token reduction, or final readiness without evidence.

Manual checklist review must never be described as a specialist invocation.

## Stop conditions

Stop before mutation when the target has zero/multiple root `SKILL.md` files; a multi-platform claim depends on host-private core instructions that have not been isolated or adapted; a required deterministic gate needs Python 3 or another declared runtime that the active host cannot execute; edits touch protected paths; measured improvement is required but no evaluator can be frozen; material external source evidence cannot be snapshotted or pinned safely; source truth is missing and a patch would invent facts; no evidence-backed hypothesis exists; the reproducibility gate is applicable but required evidence cannot be frozen safely; `skill-change-gate` finds an unfixable blocking regression; validation fails and cannot be fixed in scope; final freeze verification fails; package/report outputs alias protected inputs or each other; or packaging would include secrets, caches, generated reports/evidence, old zips, or files outside the final skill folder.

## Finalization checklist

Before completion, confirm: requested host profiles were resolved; portability validation passed for every host claimed; the portable core does not require vendor-private tool names or installation paths; optional host adapters are not prerequisites; reproducibility routing was explicitly classified and its decision record validated; required specialist reconciliation passed when supplied; frontmatter is lowercase hyphen-case; activation/non-activation/ambiguous/edge scenarios exist or are planned; local refs resolve; resources are integrated or retained; no scaffold, caches, old packages, secrets, or generated noise remain; modified scripts ran or blockers are stated; discovery precedes improvement claims; material patches have gate decisions; material external evidence was snapshotted/pinned and reverified when applicable; compression was revalidated; local token growth is compressed or accepted as semantic trade-off; final token closure preserves activation, safety, validation, output, stop, routing, and evidence duties; final gate has no blocking regression; final benchmark separates measured from planned checks; final candidate freeze verifies immediately before packaging; package/report alias preflight passed; package validation and committed hash receipt pass before sharing `skill.zip`; last-known-good/recovery guarantees were preserved; no target edit occurred after the final verified freeze.
