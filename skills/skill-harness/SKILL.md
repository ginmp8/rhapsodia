---
name: skill-harness
description: use to design, run, audit, validate, compare, harden, or package evidence-based harnesses for existing Agent Skills-compatible skill packages, including ChatGPT/OpenAI, Claude, GitHub Copilot, Cursor, and other hosts. Supports portable-core validation, host adapters, auto/context/full research modes, audit-only/plan-only/apply/validation-only/package mutation, scenarios, isolated execution evidence, evaluator-visibility boundaries, trace manifests, metrics, gates, immutable baselines, recovery-aware packaging, and skill.zip delivery. Do not use for generic code, normal docs/reports, product planning, prompt advice, net-new skill creation, or skill explanations.
---

# Skill Harness

## Purpose

Build an evidence harness around an existing Agent Skills-compatible skill so it can be audited, improved, validated, compared, and packaged without ad hoc rewriting. Keep semantic behavior in the portable Agent Skills core and isolate host-specific adapters at the edges.

## Activate / Do Not Activate

Use when asked to inspect, audit, harden, benchmark, validate, package, or harness an existing skill package; make an existing skill portable across agent hosts; edit a skill folder/extracted zip with evidence; define activation, non-activation, ambiguous, edge, regression, adversarial, or output-contract scenarios; create metrics, gates, evaluators, validators, reports, or packaging checks; or compare baseline/final skill quality after bounded edits.

Do not use for generic code review, application refactors, CI work, implementation outside a reusable skill, one-off prompt writing/advice, ordinary document/slide/spreadsheet/report generation, net-new skill creation, skill explanations, or autonomous mutation without a target, scope, protected paths, and gates. Use `skill-creator` for new skills or skill explanations.

## Inputs, Assumptions, Scope

Resolve before mutation: `TARGET_SKILL_PATH` with exactly one target `SKILL.md`; harness mode `auto|context|full`; mutation mode `audit-only|plan-only|apply|validation-only|package`; portability profile `portable|openai|claude|copilot|cursor`; detected runtime capabilities; writable scope; protected paths; evidence policy/source list; gates; and final artifact.

Defaults for “improve this skill”: `auto`, `apply`, `portable`, target-folder-only edits, protected fixtures/secrets, immutable baseline first, one bounded patch batch, validation, and package only when requested or clearly expected.

Protected paths: secrets, credentials, `.git`, evaluator fixtures, expected outputs, generated baseline evidence, benchmark baselines, generated reports, old packages, and user-declared read-only paths. Gates: valid Agent Skills core, no scaffold markers, references exist, deterministic validators pass, target tests pass when present, source/evaluator identity is preserved, portability gates pass, and package validation passes before any `skill.zip` claim.

## Mode Selection and Mutation Rights

Harness modes: `auto` inspects first and researches only concrete weaknesses; `context` uses target and supplied context only; `full` combines target evidence, user context, and approved current primary sources. If research is forbidden, use `context` behavior.

Mutation modes: `audit-only` reports inventory/audit findings without edits; `plan-only` writes a harness map without edits; `apply` makes target-scope edits and validates; `validation-only` reports pass/fail gates without edits unless explicitly allowed; `package` returns a validated `skill.zip` only after package checks pass.

## Host Portability

Treat the open Agent Skills format as the canonical semantic core. Do not make correctness depend on ChatGPT/OpenAI, Claude, GitHub Copilot, Cursor, or another single host. Host metadata may be retained as optional adapters.

Read [`references/host-portability.md`](references/host-portability.md) whenever portability is requested, the host is uncertain, or runtime capabilities affect execution. Detect capabilities before product names: filesystem read/write, Python 3.10+, command execution, network/research, independent evaluators, and artifact delivery.

Use `<PYTHON>` as the logical token for the host's available Python 3.10+ execution method. Do not assume `python`, Bash, POSIX paths, or a specific product tool API.

## Skill Root Convention

Use `<skill-root>` for this harness package root and `<TARGET_SKILL_PATH>` for the target skill root. Resolve both from the active filesystem/tool environment; never require a particular host installation directory for semantic behavior.

## Resources and Progressive Loading

Always read target `SKILL.md` first. Load only needed branches:

- [`references/harness-principles.md`](references/harness-principles.md): harness map, integration, decisions, evidence.
- [`references/host-portability.md`](references/host-portability.md): portable Agent Skills core, host adapters, capability contract, host profiles.
- [`references/integrity-and-recovery.md`](references/integrity-and-recovery.md): immutable baseline, VCS/source identity, output aliases, atomic commit, receipts, rollback.
- [`references/mode-research-policy.md`](references/mode-research-policy.md): source policy and conflicts.
- [`references/skill-improvement-playbook.md`](references/skill-improvement-playbook.md): bounded changes and common fixes.
- [`references/evaluation-and-gates.md`](references/evaluation-and-gates.md): scores, required gates, saturated metrics, decisions.
- [`references/evaluation-tiers-and-holdout.md`](references/evaluation-tiers-and-holdout.md): focused/harness/holdout scenario tiers, candidate-visible vs evaluator-only partitions, and holdout reuse rules.
- [`references/multi-candidate-execution.md`](references/multi-candidate-execution.md): isolation/comparability rules for executing the same frozen scenario partition across several search candidates.
- [`references/scenario-suite-guidelines.md`](references/scenario-suite-guidelines.md): activation, non-activation, ambiguous, edge, regression, adversarial scenario schema.
- [`references/harness-quality-patterns.md`](references/harness-quality-patterns.md): entry-point coverage, determinism, isolation, observability, anti-patterns.
- [`references/isolated-execution-contract.md`](references/isolated-execution-contract.md): candidate/evaluator visibility separation, isolated-run contract, trace evidence, leakage gates, control-arm rules, and optional self-hosted generation provenance.
- [`references/report-contract.md`](references/report-contract.md): report shape and evidence labels.
- [`references/cli-and-packaging-contract.md`](references/cli-and-packaging-contract.md): command contracts, profiles, exits, exclusions, packaging order.
- [`assets/templates/harness-plan.md.template`](assets/templates/harness-plan.md.template), [`assets/templates/harness-report.md.template`](assets/templates/harness-report.md.template), [`assets/templates/scenario-suite.json.template`](assets/templates/scenario-suite.json.template), [`assets/templates/execution-evidence.json.template`](assets/templates/execution-evidence.json.template): copy/fill/render when useful.
- [`scripts/skill_harness_snapshot.py`](scripts/skill_harness_snapshot.py): immutable baseline snapshot and identity verification.
- [`scripts/skill_harness_inventory.py`](scripts/skill_harness_inventory.py), [`scripts/skill_harness_audit.py`](scripts/skill_harness_audit.py), [`scripts/skill_harness_portability.py`](scripts/skill_harness_portability.py), [`scripts/skill_harness_validate.py`](scripts/skill_harness_validate.py), [`scripts/skill_harness_package.py`](scripts/skill_harness_package.py): inventory, static audit, portability, validation, atomic packaging.
- [`scripts/validate_execution_evidence.py`](scripts/validate_execution_evidence.py): validate identity-bound behavioral execution evidence, evaluator-visibility separation, trace references, and leakage status before measured claims.
- `tests/test_snapshot.py`, `tests/test_portability_and_delivery.py`: self-regressions for baseline identity, portability, output aliases, last-good preservation, canonical ZIP root, and receipt/package hash agreement; run when changing harness runtime or packaging.
- [`examples/harness-hardening-cases.md`](examples/harness-hardening-cases.md): human-review activation and boundary examples.

Templates are operational when copied, filled, rendered, validated, or declared in workflow. Keep this file as control plane; keep rubrics, host details, schemas, examples, and script contracts in references/examples.

## Harness Map

Define before editing: decision; object under test; portable core vs host adapters; runtime capabilities; writable/read-only/protected scope; dependencies; target entry points; scenario groups; input corpus/model; candidate-visible inputs; evaluator-only assets; source identities; optional self-hosting generation/controller/baseline/candidate identities; evidence sources; runner commands/adapters; execution isolation level; trace manifest; evaluators; optional control arm; metrics; hard gates; recovery policy; and evidence record for baseline, plan, changes, command outputs, final comparison, package path, hashes, risks, and rollback.

- `scripts/validate_multi_candidate_manifest.py`: validates candidate/run/workdir uniqueness, frozen comparability identities, and holdout leakage claims for multi-candidate runs.

## Workflow

1. **Inspect and snapshot** target `SKILL.md`, confirm exactly one target root, inventory support directories, and capture an immutable before-state before mutation.

   ```text
   <PYTHON> <skill-root>/scripts/skill_harness_snapshot.py capture --target <TARGET_SKILL_PATH> --snapshot-dir <work-dir>/baseline-snapshot --manifest <work-dir>/baseline-manifest.json
   <PYTHON> <skill-root>/scripts/skill_harness_inventory.py --target <TARGET_SKILL_PATH> --output <report-dir>/inventory.json
   ```

   If snapshotting is blocked by sensitive-looking files, escaping symlinks, or ambiguous roots, stop mutation and report the blocker.

2. **Baseline and portability** with static audit plus the selected host-neutral/profile check. Treat scores as structural evidence, not behavior proof. If a metric is saturated, add auxiliary metrics before claiming improvement.

   ```text
   <PYTHON> <skill-root>/scripts/skill_harness_audit.py --target <TARGET_SKILL_PATH> --output <report-dir>/harness-audit.md --json-output <report-dir>/harness-audit.json
   <PYTHON> <skill-root>/scripts/skill_harness_portability.py --target <TARGET_SKILL_PATH> --profile <PROFILE> --output <report-dir>/portability.json
   ```

3. **Plan** evidence policy, hypotheses, portable-core/adapter changes, target entry points, input corpus/model, scenarios, metrics, evaluators, hard gates, validation, packaging, recovery, and risk. When staged evaluation is requested, partition scenarios into `L2-focused`, `L3-harness`, and optional `L5-holdout` using `references/evaluation-tiers-and-holdout.md`. Prefer `assets/templates/harness-plan.md.template` for durable plans. For high-risk or saturated-score targets, add auxiliary coverage/integrity metrics before claiming improvement.

4. **Establish execution visibility when behavioral evidence is requested.** Separate candidate-visible inputs from evaluator-only rubrics, expected outcomes, hidden graders, and holdouts. For multi-candidate/search runs, follow `references/multi-candidate-execution.md`: give each candidate an isolated work area, identical frozen scenario/evaluator identities, and a distinct trace identity; do not reuse mutable state between candidates. For self-hosted runs, also bind execution to `generation_id`, immutable controller identity, baseline identity, and candidate identity; Harness verifies isolation/provenance but does not own promotion or specialist routing. Use capability-based isolation: a dedicated work directory is the minimum; process/container isolation is stronger when the host supports it. Do not require Docker as portable core semantics. Capture a run/trace manifest and validate it before treating outcomes as measured. Read `references/isolated-execution-contract.md`.

5. **Freeze evidence and apply** bounded edits only inside allowed scope. Protect baseline snapshots, evaluator fixtures, expected outputs, scoring thresholds, and source identities. If an evaluator must change, invalidate that comparison and restart from a new frozen baseline. Preserve target behavior; isolate host extensions; move long branches to references; add scripts only for deterministic work; never invent benchmark, validation, install, or package evidence.

6. **Validate and compare** by rerunning inventory/audit, portability, validator, modified-script checks/tests, target tests when present, and baseline/final comparison. For behavioral results, validate execution evidence and reject measured claims when evaluator leakage, missing trace identity, or mutable-state contamination is detected. Verify the frozen baseline snapshot itself has not changed.

   ```text
   <PYTHON> <skill-root>/scripts/skill_harness_validate.py --target <TARGET_SKILL_PATH> --profile <PROFILE> --output <report-dir>/validation.json
   <PYTHON> <skill-root>/scripts/skill_harness_snapshot.py verify --manifest <work-dir>/baseline-manifest.json --snapshot-only --output <report-dir>/baseline-verification.json
   ```

7. **Freeze final candidate** after all applicable gates pass. Use explicit **freeze after pass** semantics: once frozen, do not edit the candidate without reopening the affected gates. Do not perform unvalidated cleanup after this point. Any later edit reopens affected gates.

8. **Package atomically** only when gates pass. Validate authored and resolved output paths, reject aliases, preserve last-good package/report on failure, and use recovery-aware commit semantics.

   ```text
   <PYTHON> <skill-root>/scripts/skill_harness_package.py --target <TARGET_SKILL_PATH> --output <artifact-dir>/skill.zip --report <report-dir>/package-validation.json --profile <PROFILE> --strict
   ```

   The archive root must match `SKILL.md:name`, independent of the temporary staging directory.

9. **Verify delivery identity**: compare the final target tree hash with the package receipt's `source_tree_sha256`; verify package SHA-256/ZIP integrity; report recovery paths if rollback was incomplete.

10. **Report** with `assets/templates/harness-report.md.template` when durable output helps. Return a package path only when the file exists, package receipt says `status: pass`, and final candidate identity still matches the receipt.

## Output Contract

Final response/report includes mode and target; portability profile/capabilities; self-hosting generation/controller/baseline/candidate provenance when applicable; decision; evidence policy/source identities; baseline snapshot identity; baseline inventory/audit/portability gates; harness map/plan; hypotheses; scenario status; candidate-visible vs evaluator-only boundary; isolation level; trace/execution-evidence identity and leakage status when behavioral execution exists; metrics/evaluators and freeze status; optional no-skill/control-arm status when relevant; changes; validation commands/outcomes; before/after comparison; auxiliary metrics for saturated scores; final candidate/package hashes; recovery status; residual risks/assumptions; recommendation; and package artifact path only when valid.

Evidence labels: `measured` for executed commands/tests/validators/package/scenario results; `derived` for file/context inspection; `researched` for cited current research; `proposed` for planned checks; `unknown` for unavailable facts. Scenario pass rates, activation precision/recall, and behavioral conformance are measured only after prompts execute and evaluator decisions are captured.

Keep evidence identities separate: live source, immutable baseline snapshot, evaluator set, final candidate tree, delivered package, and persisted receipt.

## Stop Conditions

Stop before editing when the target lacks exactly one `SKILL.md`; is not an Agent Skills-compatible package; mutation lacks a safe immutable baseline; required source truth is unavailable; sensitive-looking files or escaping symlinks block safe snapshotting; requested changes touch protected evidence; an evaluator would need to be weakened to pass; portability requires a host-only dependency that would break the requested portable core; required capabilities are unavailable for a claimed gate; evaluator-only assets or hidden expected outcomes are exposed to the evaluated candidate in a way that invalidates the comparison; execution trace/identity evidence required for a measured claim is missing; output/package/report paths alias protected/input/sibling targets; validation fails after structural changes and cannot be fixed within scope; or rollback cannot restore/preserve recoverable evidence.

## Finalization Checklist

Before success claims, verify: baseline snapshot/inventory/audit ran; portability profile and capabilities were recorded; evidence policy was followed; harness map existed before edits; evaluator/source evidence stayed frozen or the experiment was explicitly restarted; evaluator-only assets stayed outside candidate-visible inputs for hidden-grader/holdout claims; execution evidence passed leakage/identity validation when behavioral results are called measured; every added resource is integrated; scaffold markers/generated noise are absent; modified scripts/tests ran or blockers are reported; portable core remains valid when host adapters are ignored; output aliases were rejected; last-good delivery is preserved on failure; receipts are complete and correspond to committed bytes; protected paths stayed unchanged; final target identity matches package receipt; and any returned `skill.zip` exists with passing package validation.
