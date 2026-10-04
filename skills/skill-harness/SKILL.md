---
name: skill-harness
description: use to design, run, audit, validate, compare, harden, or package evidence-based harnesses for existing Agent Skills-compatible skill packages across portable, OpenAI/ChatGPT, Codex, Claude, GitHub Copilot, Cursor, and other hosts. Supports immutable baselines, target-trust preflight, portable-core validation, isolated execution, evaluator visibility, environment/provenance profiles, repeated stochastic trials, grader calibration, metamorphic scenarios, holdout exposure, trace/lineage evidence, gates, recovery-aware packaging, and skill.zip delivery. Do not use for generic code, ordinary docs/reports, product planning, one-off prompt advice, net-new skill creation, or skill explanations.
---

# Skill Harness

## Purpose

Build an evidence harness around an existing Agent Skills-compatible skill so it can be audited, improved, validated, compared, and packaged without ad hoc rewriting. Keep semantic behavior in the portable Agent Skills core and isolate host-specific adapters at the edges.

## Activate / Do Not Activate

Use when asked to inspect, audit, harden, benchmark, validate, package, or harness an existing skill package; make an existing skill portable across agent hosts; edit a skill folder/extracted zip with evidence; define activation, non-activation, ambiguous, edge, regression, adversarial, metamorphic, or output-contract scenarios; create metrics, gates, evaluators, validators, provenance, or packaging checks; or compare baseline/final skill quality after bounded edits.

Do not use for generic code review, application refactors, CI work, implementation outside a reusable skill, one-off prompt writing/advice, ordinary document/slide/spreadsheet/report generation, net-new skill creation, skill explanations, or autonomous mutation without a target, scope, protected paths, and gates. Use `skill-creator` for new skills or skill explanations.

## Inputs, Assumptions, Scope

Resolve before mutation: `TARGET_SKILL_PATH` with exactly one target `SKILL.md`; source class `trusted-owned|trusted-local|external-untrusted|unknown`; harness mode `auto|context|full`; mutation mode `audit-only|plan-only|apply|validation-only|package`; portability profile `portable|openai|codex|claude|copilot|cursor`; detected runtime/isolation capabilities; writable scope; protected paths; evidence policy/source list; evaluator/scenario identities; environment sensitivity; gates; and final artifact.

Defaults for “improve this skill”: `auto`, `apply`, `portable`, target-folder-only edits, protected fixtures/secrets, immutable baseline first, one bounded patch batch, validation, and package only when requested or clearly expected.

Protected paths: secrets, credentials, `.git`, evaluator fixtures, expected outputs, generated baseline evidence, benchmark baselines, generated reports, old packages, and user-declared read-only paths. Gates: valid Agent Skills core, no scaffold markers, references exist, deterministic validators pass, target tests pass when present, source/evaluator identity is preserved, portability gates pass, and package validation passes before any `skill.zip` claim.

## Mode Selection and Mutation Rights

Harness modes: `auto` inspects first and researches only concrete weaknesses; `context` uses target and supplied context only; `full` combines target evidence, user context, and approved current primary sources. If research is forbidden, use `context` behavior.

Mutation modes: `audit-only` reports inventory/audit findings without edits; `plan-only` writes a harness map without edits; `apply` makes target-scope edits and validates; `validation-only` reports pass/fail gates without edits unless explicitly allowed; `package` returns a validated `skill.zip` only after package checks pass.

## Host Portability

Treat the open Agent Skills format as the canonical semantic core. Do not make correctness depend on ChatGPT/OpenAI, Codex, Claude, GitHub Copilot, Cursor, or another single host. Host metadata may be retained as optional adapters.

Read [`references/host-portability.md`](references/host-portability.md) whenever portability is requested, the host is uncertain, or runtime capabilities affect execution. Detect capabilities before product names: filesystem read/write, Python 3.10+, command execution, isolation boundary, network/research, independent evaluators, and artifact delivery.

Use `<PYTHON>` as the logical token for the host's available Python 3.10+ execution method. Do not assume `python`, Bash, POSIX paths, Docker, or a specific product tool API.

## Skill Root Convention

Use `<skill-root>` for this harness package root and `<TARGET_SKILL_PATH>` for the target skill root. Resolve both from the active filesystem/tool environment; never require a particular host installation directory for semantic behavior.

## Resources and Progressive Loading

Always read target `SKILL.md` first. Load only needed branches:

- [`references/harness-principles.md`](references/harness-principles.md): harness map, integration, decisions, evidence.
- [`references/host-portability.md`](references/host-portability.md): portable Agent Skills core, host adapters, capability contract, host profiles.
- [`references/integrity-and-recovery.md`](references/integrity-and-recovery.md): immutable baseline, VCS/source identity, output aliases, atomic commit, receipts, rollback.
- [`references/mode-research-policy.md`](references/mode-research-policy.md): source policy, research identity, and conflicts.
- [`references/skill-improvement-playbook.md`](references/skill-improvement-playbook.md): bounded changes and common fixes.
- [`references/evaluation-and-gates.md`](references/evaluation-and-gates.md): evidence layers, outcome-first grading, grader calibration, scores, gates, and claims.
- [`references/evaluation-tiers-and-holdout.md`](references/evaluation-tiers-and-holdout.md) and [`references/holdout-exposure.md`](references/holdout-exposure.md): focused/harness/holdout partitions, visibility, reuse, and lineage exposure.
- [`references/scenario-suite-guidelines.md`](references/scenario-suite-guidelines.md): scenario schema plus reference-solution/oracle discipline.
- [`references/metamorphic-evaluation.md`](references/metamorphic-evaluation.md): semantic-preserving transformations and relation checks.
- [`references/evaluation-suite-health.md`](references/evaluation-suite-health.md): saturation, failure clustering, evaluator drift, and transcript sampling.
- [`references/grader-calibration.md`](references/grader-calibration.md): LLM/human grader calibration, abstention, order-swap and verbosity probes.
- [`references/environment-provenance.md`](references/environment-provenance.md): material execution-environment identity and comparability.
- [`references/stochastic-evaluation.md`](references/stochastic-evaluation.md): repeated trials, Wilson uncertainty, reliability-under-repetition, and replication rules.
- [`references/execution-lineage.md`](references/execution-lineage.md): multi-stage dependency identity, invalidation, replay, and canonical outputs.
- [`references/evaluation-provenance.md`](references/evaluation-provenance.md): provenance-lite binding of harness, process, dependencies, identities, and outputs.
- [`references/untrusted-target-execution.md`](references/untrusted-target-execution.md): trust classification and safe target-owned code execution.
- [`references/multi-candidate-execution.md`](references/multi-candidate-execution.md) and [`references/multi-candidate-execution-strict.md`](references/multi-candidate-execution-strict.md): isolated distinct-candidate and repeated-run evidence contracts.
- [`references/harness-quality-patterns.md`](references/harness-quality-patterns.md): entry-point coverage, determinism, isolation, observability, anti-patterns.
- [`references/isolated-execution-contract.md`](references/isolated-execution-contract.md): candidate/evaluator visibility, isolated-run contract, leakage gates, control arms, self-hosting provenance.
- [`references/workflow-execution-evidence.md`](references/workflow-execution-evidence.md): orchestration plan/trace evidence separated from target-skill evidence.
- [`references/report-contract.md`](references/report-contract.md): report shape and evidence labels.
- [`references/cli-and-packaging-contract.md`](references/cli-and-packaging-contract.md): commands, profiles, exits, exclusions, packaging order.
- [`assets/templates/harness-plan.md.template`](assets/templates/harness-plan.md.template), [`assets/templates/harness-report.md.template`](assets/templates/harness-report.md.template), [`assets/templates/scenario-suite.json.template`](assets/templates/scenario-suite.json.template), [`assets/templates/execution-evidence.json.template`](assets/templates/execution-evidence.json.template), [`assets/templates/workflow-execution-evidence.json.template`](assets/templates/workflow-execution-evidence.json.template): core planning/report/execution envelopes.
- [`assets/templates/execution-environment.json.template`](assets/templates/execution-environment.json.template), [`assets/templates/stochastic-evaluation.json.template`](assets/templates/stochastic-evaluation.json.template), [`assets/templates/execution-lineage.json.template`](assets/templates/execution-lineage.json.template): reproducibility profiles validated against [`assets/schemas/execution-environment.schema.json`](assets/schemas/execution-environment.schema.json), [`assets/schemas/stochastic-evaluation.schema.json`](assets/schemas/stochastic-evaluation.schema.json), and [`assets/schemas/execution-lineage.schema.json`](assets/schemas/execution-lineage.schema.json).
- [`assets/templates/grader-calibration.json.template`](assets/templates/grader-calibration.json.template), [`assets/templates/metamorphic-suite.json.template`](assets/templates/metamorphic-suite.json.template), [`assets/templates/evaluation-provenance.json.template`](assets/templates/evaluation-provenance.json.template), [`assets/templates/holdout-exposure.json.template`](assets/templates/holdout-exposure.json.template): evaluation sidecars with matching schemas under `assets/schemas/`.
- [`assets/templates/multi-candidate-manifest.json.template`](assets/templates/multi-candidate-manifest.json.template), [`assets/templates/multi-candidate-manifest-strict.json.template`](assets/templates/multi-candidate-manifest-strict.json.template): multi-candidate envelopes.
- [`scripts/skill_harness_snapshot.py`](scripts/skill_harness_snapshot.py): immutable baseline snapshot and identity verification.
- [`scripts/skill_harness_inventory.py`](scripts/skill_harness_inventory.py), [`scripts/skill_harness_audit.py`](scripts/skill_harness_audit.py), [`scripts/skill_harness_portability.py`](scripts/skill_harness_portability.py), [`scripts/skill_harness_validate.py`](scripts/skill_harness_validate.py), [`scripts/skill_harness_package.py`](scripts/skill_harness_package.py): inventory, static audit, portability, validation, atomic packaging.
- [`scripts/skill_harness_host_matrix.py`](scripts/skill_harness_host_matrix.py): aggregate gate over `portable`, `openai`, `codex`, `claude`, `copilot`, and `cursor` without forking core semantics.
- [`scripts/assess_target_trust.py`](scripts/assess_target_trust.py): static trust preflight before target-owned executable code runs.
- [`scripts/validate_execution_evidence.py`](scripts/validate_execution_evidence.py): identity-bound behavioral execution, evaluator visibility, trace, and leakage checks.
- [`scripts/validate_reproducibility_profiles.py`](scripts/validate_reproducibility_profiles.py): environment, stochastic, and execution-lineage evidence validation.
- [`scripts/validate_grader_calibration.py`](scripts/validate_grader_calibration.py), [`scripts/validate_metamorphic_suite.py`](scripts/validate_metamorphic_suite.py), [`scripts/validate_evaluation_provenance.py`](scripts/validate_evaluation_provenance.py), [`scripts/validate_holdout_exposure.py`](scripts/validate_holdout_exposure.py): deterministic evaluation sidecar validators.
- [`scripts/run_self_tests.py`](scripts/run_self_tests.py): dependency-free self-test runner; fail closed when no tests are discovered.
- `tests/test_snapshot.py`, `tests/test_portability_and_delivery.py`, `tests/test_portable_self_verification.py`, `tests/test_advanced_reproducibility.py`, `tests/test_integration_contracts.py`: core regressions; run after harness runtime/contracts change.
- [`evals/activation-scenarios.json`](evals/activation-scenarios.json): planned activation/boundary scenarios; never call them measured until executed.
- [`examples/harness-hardening-cases.md`](examples/harness-hardening-cases.md): human-review activation and boundary examples.

Templates become operational only when copied/filled/rendered/validated or explicitly declared in the workflow. Keep this file as control plane; keep schemas, rubrics, examples, and branch detail in references.

## Harness Map

Define before editing: decision; object under test; target source/trust class; portable core vs adapters; runtime/isolation capabilities; writable/read-only/protected scope; dependencies; target entry points; scenario groups and optional metamorphic relations; input corpus/model; candidate-visible inputs; evaluator-only assets; source/evaluator/environment identities; reference-solution/oracle status; grader calibration status; repeated-trial stop rule when stochastic reliability matters; optional self-hosting identities; runner commands/adapters; isolation level; trace/lineage evidence; evaluators; metrics; hard gates; holdout exposure policy; evaluation provenance; recovery policy; and evidence records for baseline, plan, changes, commands, final comparison, package, hashes, risks, and rollback.

- `scripts/validate_multi_candidate_manifest.py`: validates `skill-opt.harness-multi-candidate-evidence` v4 for distinct candidates with frozen evaluator/policy identities, candidate-byte uniqueness, trace identity, and trace-manifest provenance.
- `scripts/validate_multi_candidate_manifest_strict.py`: validates additive `skill-opt.harness-multi-candidate-evidence-strict` v2 for repeated executions of the same identity-bound candidate.
- `contracts/integration-manifest.json`: declares these public contracts plus the additive reproducibility/evaluation sidecar contracts. Preserve existing contract versions; incompatible changes require a new version.

When a scenario uses adaptive multi-stage execution, keep target-skill evidence separate from orchestration evidence. A changed workflow-plan identity invalidates a same-plan execution comparison even when target skill bytes are unchanged; use `references/workflow-execution-evidence.md`, and use `references/execution-lineage.md` only when replay/invalidation depends on the dependency graph.

## Workflow

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
