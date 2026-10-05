---
name: skill-harness
description: use when the primary task is to design, run, audit, validate, compare, harden, or package an evidence harness around one existing Agent Skills-compatible skill. Owns immutable baselines, target-trust preflight, scenario/evaluator design, isolated execution, evaluator visibility, reproducibility/provenance evidence, repeated trials, gates, and validated skill.zip delivery across portable/OpenAI/Codex/Claude/Copilot/Cursor hosts. Prefer skill-booster for end-to-end skill optimization when the harness is only supporting evidence; prefer skill-benchmark for a score/report without harness construction; use skill-creator for net-new skills or skill explanations. Do not use for generic code, ordinary docs/reports, product planning, or one-off prompt advice.
---

# Skill Harness

## Mission

Build an evidence harness around one existing Agent Skills-compatible skill so claims about activation, behavior, portability, reproducibility, regressions, or packaging are tied to frozen identities and executable gates rather than ad hoc judgment. Keep semantic behavior in the portable Agent Skills core and host-specific adapters at the edges.

## Activation and Routing

Use this skill when the **harness/evidence system itself is part of the work**, including one or more of: defining activation/non-activation/ambiguous/edge/regression/adversarial/metamorphic scenarios; freezing baseline/evaluator/source identities; creating validators, metrics, gates, or provenance; executing isolated baseline/candidate comparisons; calibrating graders; measuring repeated stochastic trials; tracking holdout exposure; validating trace/lineage; or producing a recovery-aware validated package.

Do not activate for generic code review, application refactors, CI work, implementation outside a reusable skill, ordinary document/slide/spreadsheet/report generation, or autonomous mutation without one target, writable scope, protected paths, and gates.

Route nearby intents deliberately:
- **`skill-booster`**: optimize one existing skill end to end when harnessing is only an evidence provider, not the primary deliverable.
- **`skill-benchmark`**: score/compare/report maturity from a bounded benchmark without building or operating a broader harness.
- **`skill-change-gate`**: make a read-only accept/reject decision on an already proposed skill change.
- **`skill-creator`**: create a net-new skill or explain how skills work.

## Modes and Defaults

Harness modes: `auto` inspects first and researches only concrete weaknesses; `context` uses target and supplied context only; `full` combines target evidence, user context, and approved current primary sources. If research is forbidden, behave as `context`.

Mutation modes: `audit-only` reports without target edits; `plan-only` produces a harness map without edits; `apply` makes bounded target-scope edits and validates; `validation-only` reports pass/fail without edits unless explicitly authorized; `package` returns a validated `skill.zip` only after all required package checks pass.

Default for “improve this skill”: `auto` + `apply` + `portable`, target-folder-only writes, protected fixtures/secrets/evaluator evidence, immutable baseline before mutation, one bounded patch batch, fresh validation, and packaging only when requested or clearly expected.

## Critical Invariants

- Resolve exactly one `<TARGET_SKILL_PATH>` containing one root `SKILL.md` before mutation.
- Freeze an immutable baseline before edits; keep source, evaluator, scenario, environment, workflow/lineage, candidate, package, and receipt identities distinct.
- Never edit/package secrets, credentials, `.git`, evaluator fixtures, expected outputs, frozen benchmark/baseline evidence, generated reports, old packages, or user-declared read-only paths.
- External/unknown targets with executable content require static trust preflight and the required isolation boundary before any target-owned code runs.
- Preserve a portable Agent Skills semantic core; host adapters may extend discovery/metadata but cannot become correctness dependencies.
- For behavioral evidence, separate `candidate-visible`, `runner-only`, `evaluator-only`, and `post-run-only` inputs; evaluator leakage invalidates the affected measured claim.
- If evaluator/scenario/threshold inputs change after results are visible, invalidate or re-baseline the comparison; do not silently reuse prior results.
- Prefer outcome/end-state correctness over trajectory conformance unless the path itself is a safety or authority requirement.
- Call results `measured` only after commands/tests/validators/scenario executions and evaluator decisions are captured; structural audits are not behavioral proof.
- Strong stochastic claims require predeclared trial budgets/stop rules and uncertainty evidence; strong LLM-grader promotion requires declared calibration strength.
- Any edit after the final candidate freeze reopens affected gates. Package only the exact frozen candidate, with passing package validation and identity-matching receipt.
- Missing capabilities, isolation, provenance, trace/lineage, calibration, or holdout blindness are `not-run`/blocked states, never implicit passes.

## Workflow at a Glance

1. **Inspect and trust-classify**: read target `SKILL.md`, confirm one root, inventory support files, resolve source class/capabilities, and run static trust preflight.
2. **Snapshot baseline**: capture immutable before-state and identity before any target mutation.
3. **Baseline structure/portability**: run inventory, static audit, selected portability profile, and full host matrix when making multi-platform claims.
4. **Freeze the harness map**: declare object under test, writable/protected scope, evidence policy, scenarios/oracles, evaluators, metrics, gates, environment sensitivity, holdout policy, recovery, and final artifact.
5. **Establish execution validity** when behavioral evidence is used: isolate mutable state, separate visibility zones, bind environment/evaluator/scenario identities, calibrate graders when required, and define repeated-trial rules before execution.
6. **Apply one bounded edit batch** only in an authorized mutation mode; keep evaluator assets and frozen evidence unchanged or explicitly re-baseline.
7. **Validate and compare** with the same frozen evidence: inventory/audit, portability, target tests, self-tests when harness runtime/contracts changed, sidecar validators, and leakage/identity checks.
8. **Review suite health** for long-lived/repeated suites: saturation, chronic 0%/100% cases, failure clustering, evaluator drift, and representative traces/transcripts.
9. **Freeze final candidate**, then package atomically with alias preflight, ZIP validation, receipt/hash verification, and last-good recovery.
10. **Report evidence boundaries**: distinguish measured/derived/researched/proposed/unknown, list residual risks, and return a package path only when the validated file exists and still matches the frozen candidate.

## Direct Resource Routing

Load only the branch that changes the current decision; all required Markdown is directly reachable from this file.

- **Harness structure / decision map:** [`references/harness-principles.md`](references/harness-principles.md).
- **Portability / host capability decision:** [`references/host-portability.md`](references/host-portability.md).
- **Baseline, rollback, freeze, atomic delivery:** [`references/integrity-and-recovery.md`](references/integrity-and-recovery.md).
- **Research/source policy:** [`references/mode-research-policy.md`](references/mode-research-policy.md).
- **Bounded target mutation:** [`references/skill-improvement-playbook.md`](references/skill-improvement-playbook.md).
- **Evaluation levels, metrics, gates, claims:** [`references/evaluation-and-gates.md`](references/evaluation-and-gates.md).
- **Behavioral isolation / evaluator visibility:** [`references/isolated-execution-contract.md`](references/isolated-execution-contract.md).
- **Holdout and visibility exposure:** [`references/evaluation-tiers-and-holdout.md`](references/evaluation-tiers-and-holdout.md) and [`references/holdout-exposure.md`](references/holdout-exposure.md).
- **Scenario/oracle and metamorphic design:** [`references/scenario-suite-guidelines.md`](references/scenario-suite-guidelines.md) and [`references/metamorphic-evaluation.md`](references/metamorphic-evaluation.md).
- **Reproducibility/provenance:** [`references/environment-provenance.md`](references/environment-provenance.md), [`references/stochastic-evaluation.md`](references/stochastic-evaluation.md), [`references/execution-lineage.md`](references/execution-lineage.md), and [`references/evaluation-provenance.md`](references/evaluation-provenance.md).
- **Deterministic CLI / packaging mechanics:** [`references/cli-and-packaging-contract.md`](references/cli-and-packaging-contract.md).

## Required Inputs and Scope

Resolve before mutation: `TARGET_SKILL_PATH`; source class `trusted-owned|trusted-local|external-untrusted|unknown`; harness mode; mutation mode; portability profile `portable|openai|codex|claude|copilot|cursor`; detected runtime/isolation capabilities; writable scope; protected paths; evidence policy/source list; evaluator/scenario identities; environment sensitivity; gates; and final artifact.

Protected paths and hard gates follow the invariants above. Core gates are: valid Agent Skills structure, no scaffold markers, all local references resolve, deterministic validators pass, target tests pass when present, source/evaluator identity remains valid, portability gates pass for the claim being made, and package validation passes before any `skill.zip` success claim.

## Host Portability and Runtime Convention

Treat the open Agent Skills format as the canonical semantic core. Detect capabilities before product names: filesystem read/write, Python 3.10+, command execution, isolation boundary, network/current research, independent evaluators, and artifact delivery.

Use `<PYTHON>` for the host's available Python 3.10+ execution method, `<skill-root>` for this harness package root, and `<TARGET_SKILL_PATH>` for the target skill root. Never require a specific executable name, shell, OS path, Docker, product-private tool API, or host installation directory for core semantics.

Read [`references/host-portability.md`](references/host-portability.md) whenever portability is requested, the host is uncertain, or runtime capabilities affect execution.

## Reference Catalog

The routing section above is the decision surface; this catalog is for deeper implementation detail and remains one hop from `SKILL.md`.

- [`references/evaluation-suite-health.md`](references/evaluation-suite-health.md): detect saturated suites, chronic pass/fail cases, failure clusters, evaluator drift, and when transcript/trace sampling is required.
- [`references/grader-calibration.md`](references/grader-calibration.md): decide whether LLM/human graders are calibrated strongly enough for the intended promotion claim, including abstention/order-swap/verbosity probes.
- [`references/untrusted-target-execution.md`](references/untrusted-target-execution.md): decide whether target-owned executable content can run and which isolation/trust constraints apply.
- [`references/multi-candidate-execution.md`](references/multi-candidate-execution.md): evidence contract for several distinct candidate identities.
- [`references/multi-candidate-execution-strict.md`](references/multi-candidate-execution-strict.md): stricter repeated-execution contract for the same identity-bound candidate.
- [`references/harness-quality-patterns.md`](references/harness-quality-patterns.md): review entry-point coverage, determinism, isolation, observability, and common harness anti-patterns.
- [`references/workflow-execution-evidence.md`](references/workflow-execution-evidence.md): separate adaptive orchestration plan/trace evidence from target-skill evidence when multi-stage execution can change independently.
- [`references/report-contract.md`](references/report-contract.md): final report fields and evidence-label semantics.

Templates and schemas under `assets/` become operational only when copied/filled/rendered/validated or explicitly declared in the workflow. Start durable planning from [`assets/templates/harness-plan.md.template`](assets/templates/harness-plan.md.template) and scenario authoring from [`assets/templates/scenario-suite.json.template`](assets/templates/scenario-suite.json.template). Bundled scripts under `scripts/` provide snapshot, inventory, audit, portability, host-matrix, validation, evidence-sidecar, self-test, and packaging mechanics; [`references/cli-and-packaging-contract.md`](references/cli-and-packaging-contract.md) is the authoritative command/exit/exclusion map.

Planned activation coverage lives in [`evals/activation-scenarios.json`](evals/activation-scenarios.json); never call it measured until scenarios are actually executed. Human-review boundary examples live in [`examples/harness-hardening-cases.md`](examples/harness-hardening-cases.md).

## Harness Map

Define before editing: decision; object under test; target source/trust class; portable core vs adapters; runtime/isolation capabilities; writable/read-only/protected scope; dependencies; target entry points; scenario groups and optional metamorphic relations; input corpus/model; candidate-visible inputs; evaluator-only assets; source/evaluator/environment identities; reference-solution/oracle status; grader calibration status; repeated-trial stop rule when stochastic reliability matters; optional self-hosting identities; runner commands/adapters; isolation level; trace/lineage evidence; evaluators; metrics; hard gates; holdout exposure policy; evaluation provenance; recovery policy; and evidence records for baseline, plan, changes, commands, final comparison, package, hashes, risks, and rollback.

- `scripts/validate_multi_candidate_manifest.py` validates `skill-opt.harness-multi-candidate-evidence` v4 for distinct candidates with frozen evaluator/policy identities, candidate-byte uniqueness, trace identity, and trace-manifest provenance.
- `scripts/validate_multi_candidate_manifest_strict.py` validates additive `skill-opt.harness-multi-candidate-evidence-strict` v2 for repeated executions of the same identity-bound candidate.
- `contracts/integration-manifest.json` declares these public contracts plus additive reproducibility/evaluation sidecar contracts. Preserve existing contract versions; incompatible changes require a new version.

When a scenario uses adaptive multi-stage execution, keep target-skill evidence separate from orchestration evidence. A changed workflow-plan identity invalidates a same-plan execution comparison even when target skill bytes are unchanged; use `references/workflow-execution-evidence.md`, and use `references/execution-lineage.md` only when replay/invalidation depends on the dependency graph.

## Detailed Workflow

1. **Inspect, trust-classify, and snapshot.** Read target `SKILL.md`, confirm one root, inventory support directories, run static trust preflight, and capture an immutable before-state before mutation. For external/unknown targets with executable content, do not run target-owned code until the required isolation boundary exists.

   ```text
   <PYTHON> <skill-root>/scripts/assess_target_trust.py --target <TARGET_SKILL_PATH> --source-class <SOURCE_CLASS> --json <report-dir>/target-trust.json
   <PYTHON> <skill-root>/scripts/skill_harness_snapshot.py capture --target <TARGET_SKILL_PATH> --snapshot-dir <work-dir>/baseline-snapshot --manifest <work-dir>/baseline-manifest.json
   <PYTHON> <skill-root>/scripts/skill_harness_inventory.py --target <TARGET_SKILL_PATH> --output <report-dir>/inventory.json
   ```

2. **Baseline and portability.** Run static audit plus the selected profile. Treat static scores as structural evidence, not behavioral proof. For multi-platform delivery, validate the full supported host matrix.

3. **Plan before mutation.** Freeze evidence policy, source/evaluator identities, hypotheses, target entry points, scenarios, metrics, gates, validation, packaging, recovery, and risk. Add reference solutions/oracle probes for hard behavioral gates when feasible. Add metamorphic relations for semantic invariants when they improve coverage without inventing golden answers. Predeclare repeated-trial stop rules/budgets for strong stochastic claims.

4. **Establish execution validity for behavioral evidence.** Separate candidate-visible, runner-only, evaluator-only, and post-run-only inputs. Use fresh mutable state per arm/trial. Record environment identity when runtime/provider/tool/resource state can affect comparison. Calibrate LLM graders before they alone control a strong promotion claim. Track holdout exposure by lineage. Use multi-candidate contracts only when several candidates/repeated runs actually exist.

5. **Freeze evidence and apply bounded edits.** Protect baseline snapshots, evaluator fixtures, expected outputs, scoring thresholds, source identities, and holdouts. If an evaluator changes after results are visible, invalidate/re-baseline the comparison. Preserve target semantics; isolate host extensions; add deterministic mechanics only where they reduce real variance.

6. **Validate and compare.** Rerun inventory/audit, portability, package validator, self-tests, target tests, and affected sidecar validators. Use outcome/end-state correctness before trajectory conformance unless the path itself is a safety/authority requirement. Reject measured claims on evaluator leakage, material environment drift, missing required trace/lineage evidence, invalid holdout blindness, or uncalibrated strong LLM-grader gates.

   ```text
   <PYTHON> <skill-root>/scripts/skill_harness_validate.py --target <TARGET_SKILL_PATH> --profile <PROFILE> --output <report-dir>/validation.json
   <PYTHON> <skill-root>/scripts/skill_harness_host_matrix.py --target <TARGET_SKILL_PATH> --profiles all --strict --output <report-dir>/host-matrix.json
   <PYTHON> <skill-root>/scripts/run_self_tests.py --output <report-dir>/self-tests.json
   <PYTHON> <skill-root>/scripts/skill_harness_snapshot.py verify --manifest <work-dir>/baseline-manifest.json --snapshot-only --output <report-dir>/baseline-verification.json
   ```

   When applicable, validate sidecars with `scripts/validate_reproducibility_profiles.py --kind environment|stochastic|lineage`, `scripts/validate_grader_calibration.py`, `scripts/validate_metamorphic_suite.py`, `scripts/validate_holdout_exposure.py`, and `scripts/validate_evaluation_provenance.py`.

7. **Review suite health.** For long-lived or repeatedly optimized suites, check saturation, chronic 0%/100% scenarios, failure clustering, evaluator drift, and representative transcripts/traces. Do not interpret repeated zero as model weakness until task/oracle validity is checked.

8. **Freeze final candidate.** After all applicable gates pass, make the candidate immutable for delivery. Any later edit reopens affected gates.

9. **Package atomically.** Preflight authored/resolved output aliases; validate/stage ZIP and receipt; preserve last-good artifacts; commit atomically; package only the exact frozen candidate.

   ```text
   <PYTHON> <skill-root>/scripts/skill_harness_package.py --target <TARGET_SKILL_PATH> --output <artifact-dir>/skill.zip --report <report-dir>/package-validation.json --profile <PROFILE> --strict
   ```

10. **Verify provenance and delivery identity.** Compare final target tree hash with package receipt; verify package SHA-256/ZIP integrity; bind material evaluation identities in an evaluation-provenance receipt when comparison provenance matters; report recovery paths if rollback was incomplete.

11. **Report.** Use `assets/templates/harness-report.md.template` when durable output helps. Return a package path only when the file exists, package receipt says `status: pass`, and final candidate identity still matches the receipt.

## Output Contract

Final response/report includes mode/target; portability profile and capabilities; target trust/execution policy; evidence/source identities; baseline identity; baseline audit/portability; scenarios and oracle status; candidate-visible/evaluator-only boundary; isolation/environment identity; grader calibration when applicable; repeated-trial metrics/uncertainty for stochastic claims; trace/lineage identity; holdout exposure/blindness state; evaluation-provenance identity when material; changes; validation outcomes; before/after comparison; auxiliary metrics for saturated scores; final candidate/package hashes; recovery status; residual risks/assumptions; recommendation; and package path only when valid.

Evidence labels: `measured` for executed commands/tests/validators/package/scenario results; `derived` for deterministic inspection/calculation; `researched` for cited current research; `proposed` for planned checks; `unknown` for unavailable facts. Scenario pass rates, activation precision/recall, stochastic reliability, and behavioral conformance are measured only after executions and evaluator decisions are captured.

Keep identities separate: live source/research snapshot, baseline snapshot, evaluator, environment, workflow plan/lineage, candidate, delivered package, and persisted receipts.

## Stop Conditions

Stop before editing/execution when the target lacks exactly one `SKILL.md`; mutation lacks a safe baseline; source truth is unavailable; sensitive-looking files or unsafe symlinks block safe intake; an external/unknown executable target requires isolation that is unavailable; requested changes touch protected evidence; an evaluator would need to be weakened; portability requires a host-private core dependency; required capabilities are unavailable; evaluator-only assets leaked to the candidate; strong LLM-grader promotion depends on unknown calibration; material paired environment drift is unresolved; holdout feedback informed mutation while a blind claim is still asserted; required execution trace/lineage/provenance is missing; output paths alias protected/input/sibling targets; validation fails and cannot be safely repaired; or rollback cannot preserve recoverable evidence.

## Finalization Checklist

Before success claims, verify: baseline snapshot/inventory/audit ran; target trust policy was respected; portability capabilities were recorded; multi-platform claims used all six supported profiles or an explicitly narrowed matrix; self-tests executed after runtime/test changes; evidence policy was followed; harness map existed before edits; evaluator/source evidence stayed frozen or comparison was re-baselined; reference solutions/oracle probes were used for hard behavioral gates when appropriate; hidden evaluator/holdout assets stayed outside candidate visibility; material environment identity was comparable; stochastic claims used the declared trial evidence; LLM graders met the declared calibration strength; execution evidence passed leakage/identity validation; holdout exposure state matches blind-claim language; lineage/provenance is valid when claimed; every added resource is integrated; modified scripts/tests ran or blockers are reported; portable core remains valid without adapters; output aliases were rejected; last-good delivery is preserved on failure; receipts correspond to committed bytes; protected paths stayed unchanged; final target identity matches package receipt; and any returned `skill.zip` exists with passing package validation.
