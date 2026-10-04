---
name: skill-hardening
description: Harden existing Agent Skills-compatible packages with evidence-backed validation, trust intake, portability checks, reproducibility controls, traceable changes, and deterministic packaging. Use when an existing skill must be audited, repaired, matured, validated, or packaged; do not use for net-new skills, generic repositories, product planning, ordinary documentation, or benchmark-only scoring.
---

# Skill Hardening

## Purpose

Harden one existing Agent Skills-compatible package without equating package size with maturity. Own package-level audit, bounded repair, validation, freeze, and delivery for `SKILL.md`, optional host adapters, references, scripts, assets/templates, examples/evals, validators, output contracts, and packaging hygiene.

Keep the open Agent Skills semantic core portable. Host-specific metadata is an optional adapter, never a prerequisite for correctness.

## Required inputs

Resolve or infer before mutation:

1. `TARGET_SKILL_PATH`: one folder/extracted ZIP with exactly one root `SKILL.md`.
2. Mode: `audit-only`, `plan-only`, `apply-hardening`, `validation-only`, or `package`.
3. `SOURCE_CLASS`: `trusted-owned`, `trusted-local`, or `external-untrusted-skill`; unknown third-party/downloaded skills default to `external-untrusted-skill`.
4. `TARGET_HOSTS`: always include `portable-core`; add `openai`, `codex`, `claude`, `copilot`, and/or `cursor` when compatibility is requested. Full multi-platform hardening defaults to all six profiles.
5. Scope: target folder only unless explicitly narrowed/expanded.
6. Baseline: immutable before-state plus deterministic target identity before material edits.
7. Protected evidence: `.git`, secrets, credentials, user fixtures, expected outputs, benchmark baselines, frozen evaluators, generated evidence/reports, old packages, escaping symlinks, and user-declared read-only files.
8. Evidence: target files, failed prompts, prior outputs, benchmark/harness results, domain docs, repository truth, or a bounded research corpus.
9. Reproducibility ceiling: `objective-artifact`, `tool-action`, `research-analytic`, or `constrained-subjective`.
10. Evaluation claim: structural repair, behavioral improvement, runtime compatibility, or subjective quality. Require only evidence profiles that the claim actually needs.

Default for “harden it”: trust preflight when needed -> inspect/baseline -> audit -> contract/freeze -> trace research-backed requirements when applicable -> apply one bounded batch -> validate -> freeze -> package only when requested or clearly expected.

## Authority boundary

- **Standalone:** own hardening, validation, freeze, and package delivery within the target skill.
- **Delegated:** respect frozen evaluators, peer contracts, promotion rules, and protected paths supplied by an upstream orchestrator.
- Do not silently change peer-facing schemas, CLIs, handoffs, or evaluator thresholds.
- If a sound fix requires a breaking peer contract, stop independent promotion and report the coordinated change required.
- Do not add legacy adapters merely to preserve a contract the caller has explicitly retired.

## Modes

| Intent | Mode | Output | Closure |
|---|---|---|---|
| Understand weaknesses | `audit-only` | audit + prioritized findings | structural audit complete |
| Decide changes/resources | `plan-only` | bounded hardening map | evidence and gates mapped |
| Improve package | `apply-hardening` | changed target + evidence | applicable gates pass |
| Check readiness | `validation-only` | pass/fail/blocked gates | exact candidate validated |
| Deliver package | `package` | validated `skill.zip` + receipt | frozen candidate and archive match |

Use one primary mode. Do not enter multi-candidate search merely because several improvements are possible.

## Load only needed resources

- [references/mature-skill-patterns.md](references/mature-skill-patterns.md): control plane, progressive loading, truthful closure.
- [references/resource-hardening-playbook.md](references/resource-hardening-playbook.md): need-aware resource add/integrate/remove rules.
- [references/evaluator-contract.md](references/evaluator-contract.md): claim layers, frozen evaluators, scenario/evaluation gates.
- [references/evidence-policy.md](references/evidence-policy.md): evidence order, research traceability, claim vocabulary.
- [references/scenario-suite.md](references/scenario-suite.md): activation, boundary, coexistence, semantic-collision, regression, adversarial scenarios.
- [references/reproducibility-controls.md](references/reproducibility-controls.md): baseline identity, variability map, conditional evidence profiles, freeze-after-pass.
- [references/host-portability.md](references/host-portability.md): portable core and OpenAI/Codex/Claude/Copilot/Cursor profiles.
- [references/packaging-and-validation.md](references/packaging-and-validation.md): folder/archive validation, deterministic package, provenance-lite receipt.
- [assets/templates/hardening-contract.json.template](assets/templates/hardening-contract.json.template): v2 machine-readable hardening/reproducibility contract.
- [assets/templates/hardening-plan.md.template](assets/templates/hardening-plan.md.template), [assets/templates/hardening-report.md.template](assets/templates/hardening-report.md.template), [assets/templates/reference-file.md.template](assets/templates/reference-file.md.template), [assets/templates/scenario-suite.json.template](assets/templates/scenario-suite.json.template): optional reusable shapes.
- [scripts/trust_intake.py](scripts/trust_intake.py): static trust preflight; never executes target-owned code.
- [scripts/inventory_skill.py](scripts/inventory_skill.py): deterministic inventory.
- [scripts/hardening_audit.py](scripts/hardening_audit.py): need-aware structural maturity audit.
- [scripts/validate_portability.py](scripts/validate_portability.py): structural portable-core/host-profile validation.
- [scripts/validate_hardened_skill.py](scripts/validate_hardened_skill.py): claim-sensitive readiness gates.
- [scripts/reproducibility_controls.py](scripts/reproducibility_controls.py): tree identity, v1/v2 contract validation, evaluator freeze/verify.
- [scripts/package_skill.py](scripts/package_skill.py): deterministic package builder, archive validator, atomic replacement, provenance-lite receipt.
- [evals/activation-scenarios.json](evals/activation-scenarios.json), [examples/hardening-scenarios.json](examples/hardening-scenarios.json): planned/calibration scenarios; never call them measured until executed.

Keep `SKILL.md` as router/control plane. Optional directories are not maturity requirements by themselves.

## Workflow

1. **Trust intake before target execution.** For `external-untrusted-skill`, run `scripts/trust_intake.py` against the directory/ZIP before any target-owned script, installer, hook, binary, package-manager command, or generated command. Resolve `block` findings; explicitly review `requires-review` findings. Passing intake is authorization to continue, not a security guarantee.
2. **Establish portable baseline.** Read target `SKILL.md`, validate the portable core/profile, preserve an immutable before-state, inventory the package, and compute a deterministic tree identity. Only after trust intake may target-owned validators/tests run.
3. **Audit without bloat incentives.** Run `scripts/hardening_audit.py`. Treat the score as structural evidence only. Do not require or reward scripts, references, templates, examples, scenario counts, or a target-owned package builder solely because they exist. Existing resources must still be integrated and valid.
4. **Contract and freeze.** Classify the reproducibility ceiling and map variance across `activation -> input normalization -> routing -> references -> decisions -> generation -> validation -> repair -> delivery -> packaging`. Fill the v2 hardening contract. Declare host profiles and explicitly mark environment/provenance, stochastic-evaluation, and execution-lineage profiles applicable or not applicable with reasons. Freeze only evaluators that decide acceptance.
5. **Trace research-backed changes.** When external research materially drives mutation, preserve a bounded research artifact and maintain the chain `source -> finding -> disposition -> requirement -> change -> evaluation`. Account for every material finding; reject gold plating with no reverse justification. Structural trace coverage does not replace semantic trace review.
6. **Map and select.** For each proposed change record evidence/hypothesis, affected files, expected effect, evaluator, acceptance gate, rollback, and disposition. Prefer the smallest coherent batch. Absence of an optional resource is not itself a defect.
7. **Apply and repair diagnostically.** Use scripts/schemas for mechanical rules, explicit defaults for constrained heuristics, and rubrics/review for irreducible judgment. After a failure, fix one causal issue and rerun the same narrow gate. Stop a branch after two non-improving rounds unless new evidence changes the hypothesis. Never weaken frozen evaluators or hard gates to pass.
8. **Validate claims at the right layer.** Run folder/spec validation and requested host profiles. Require scenario coverage only when the claim needs behavioral evidence; predeclare category/minimum coverage rather than using a universal scenario count. Include coexistence/semantic-collision cases when neighboring skills can affect routing. Strong stochastic claims require repeated trials and comparable environment evidence; ordinary static repairs do not.
9. **Freeze the passing candidate.** Verify frozen evaluators and material source identities, rerun target-owned mandatory tests/validators, compute final identity, and make no later unvalidated edit.
10. **Package atomically.** When requested, package the frozen candidate with this skill's packager unless the target already owns a required packager contract. Build privately, validate, hash, atomically replace, preserve last-good output on failure, and emit receipt v3 with candidate/package, builder/profile, and optional baseline identities.

## Output contract

Report applicable:

1. mode, target, source class, requested hosts, runtime capabilities, and exact Python launcher;
2. baseline and candidate identities, inventory, structural audit, and non-saturated auxiliary signals;
3. reproducibility ceiling, variability controls, applicable/non-applicable advanced evidence profiles, and irreducible judgment;
4. research trace counts/dispositions/coverage and semantic-review status when research drove changes;
5. accepted/rejected changes with evidence, requirements, files, evaluators, and gates;
6. commands executed with `pass`/`fail`/`blocked`/`not-run` and evidence labels;
7. structural, semantic-review, behavioral, runtime, perceptual, portability, and package evidence separately;
8. protected paths respected and files changed;
9. remaining risks/uncertainty and unmeasured behavior;
10. package path, candidate hash, builder/profile identity, and archive hash only when produced and validated.

## Stop conditions

Stop or return a bounded partial result when the target root is ambiguous; mutation lacks a safe baseline; external trust blockers remain unresolved; protected evidence must be changed without authorization; required facts/evidence are absent; a frozen evaluator changed; a requested improvement claim lacks comparable execution; portability requires a host-private core dependency; passing requires weakening a hard gate; or package/receipt cannot be validated against the frozen candidate.

## Finalization checklist

Before claiming hardened status: portable frontmatter passes the requested profile; optional resources were added only for justified needs; external target code was not executed before applicable trust intake; baseline/source/evaluator/candidate identities are recorded; v2 contract profiles are explicit; research-backed changes are traceable and semantically reviewed when applicable; referenced files exist; added/modified scripts ran on representative inputs or blockers are stated; scenario sufficiency matches the claim rather than a universal count; requested host profiles pass structurally; evidence layers remain separate; no measured metric is fabricated; frozen evaluators remain unchanged; no edit occurred after final pass; and package/receipt hashes match the delivered frozen candidate.
