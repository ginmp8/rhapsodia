---
name: skill-hardening
description: "Harden one existing Agent Skills-compatible package when the primary goal is package integrity: trust intake, package-level audit/repair, portability, evidence controls, validation/freeze, and deterministic skill.zip delivery. Use for hardening, readiness, bounded repair, or packaging of an existing skill. Do not use for net-new skills or ownership redesign, evidence-led optimization/benchmark/compression as the primary goal, testing/validator work only, or read-only scoring."
---

# Skill Hardening

## Activation and scope

Harden one existing Agent Skills-compatible package without treating package size as maturity. Own package-level audit, bounded repair, validation, freeze, and delivery for `SKILL.md`, optional host adapters, references, scripts, templates/assets, examples/evals, validators, output contracts, and packaging hygiene.

- Use when the desired end state is a safer, coherent, portable, validated, and optionally packaged existing skill.
- Route net-new skills or responsibility/architecture redesign to `skill-creator-juiced` when available.
- Route evidence-led optimization, benchmarking, compression, or multi-candidate search whose primary goal is quality improvement to `skill-booster` when available.
- Route test/validator/build/lint work only to `skill-testing-and-validation`; route read-only score/review work to the appropriate benchmark/reviewer skill.
- Keep the open Agent Skills semantic core host-neutral. Host metadata is an optional adapter, never a correctness dependency.

## Core invariants

- Resolve exactly one root `SKILL.md`; preserve an immutable baseline and deterministic identity before material edits.
- For `external-untrusted-skill`, run static trust intake before any target-owned code, installer, hook, binary, package-manager command, or generated command.
- Protect `.git`, secrets, credentials, user fixtures, expected outputs, benchmark baselines, frozen evaluators, generated evidence/reports, old packages, escaping symlinks, and user-declared read-only files.
- When delegated, honor upstream frozen evaluators, peer contracts, promotion rules, and protected paths. Do not silently change peer-facing schemas, CLIs, handoffs, thresholds, or authority; a breaking peer contract blocks independent promotion.
- Optional resources are never maturity points by presence alone; add, keep, or remove them only from evidence and actual workflow need.
- For any target `SKILL.md` over 100 physical lines, its first 100 must expose purpose/scope, discriminative activation/non-use boundaries, mode choice, usable workflow, critical rules, and direct resource pointers. Long editable supporting Markdown needs an early decision-useful `Purpose` / `Load when` / `Decision impact` preview. Prefer `SKILL.md -> supporting file`; never hide required instructions behind multi-hop Markdown chains.
- Freeze only evaluators that decide acceptance. Never weaken validators, tests, thresholds, fixtures, or expected outputs to obtain a pass.
- Separate structural, semantic-review, behavioral, runtime, perceptual/editorial, portability, and package evidence; a pass in one layer does not prove another.
- Do not enter multi-candidate search merely because several improvements are possible. Prefer the smallest coherent repair batch.
- After the final passing validation, freeze the candidate. Any later material edit invalidates affected evidence and requires rerun.

## Modes

| Intent | Mode | Closure |
|---|---|---|
| Understand weaknesses | `audit-only` | prioritized structural audit |
| Decide changes/resources | `plan-only` | bounded hardening map + gates |
| Improve package | `apply-hardening` | applicable gates pass |
| Check readiness | `validation-only` | exact candidate pass/fail/blocked |
| Deliver archive | `package` | frozen candidate and validated archive/receipt match |

Use one primary mode.

## Default workflow

1. **Establish trust and baseline.** Resolve target, source class, hosts, writable/protected scope, runtime capabilities, immutable before-state, inventory, and tree identity; run trust intake first when source is external/untrusted.
2. **Audit without bloat incentives.** Run structural/package audit; treat scores as diagnostic evidence only and inspect existing resources for actual integration/validity.
3. **Contract and freeze.** Classify reproducibility ceiling as `objective-artifact`, `tool-action`, `research-analytic`, or `constrained-subjective`; map material variance; fill the v2 contract; mark `environment_provenance`, `stochastic_evaluation`, and `execution_lineage` applicable/not-applicable with reasons; freeze deciding evaluators.
4. **Trace research-backed changes when applicable.** Preserve `source -> finding -> disposition -> requirement -> change -> evaluation`; account for every material finding and semantically review the trace.
5. **Map and select.** For each change record evidence/hypothesis, affected files, expected effect, evaluator, acceptance gate, rollback, and disposition; absence of an optional resource is not itself a defect.
6. **Apply diagnostically.** Use deterministic helpers for mechanical rules, explicit defaults for constrained heuristics, and rubrics/review for irreducible judgment. Fix one causal issue at a time; stop a branch after two non-improving rounds unless new evidence changes the hypothesis.
7. **Validate at the claimed layer.** Run folder/spec validation and requested host profiles; require scenarios only for behavioral claims, including coexistence/semantic-collision when neighboring skills affect routing. Strong stochastic claims need repeated trials and comparable environment evidence.
8. **Freeze and package.** Verify evaluator/source identities, rerun mandatory tests/validators, compute final identity, then package atomically only when requested/expected, using this skill's packager unless the target owns a required packager contract; preserve last-good output on failure and bind receipt v3 to candidate/archive/builder/profile identities.

## Required inputs

Resolve or infer: `TARGET_SKILL_PATH`; primary mode; `SOURCE_CLASS` (`trusted-owned`, `trusted-local`, `external-untrusted-skill`, with unknown third-party/downloaded skills defaulting to external-untrusted); `TARGET_HOSTS` including `portable-core` plus requested profiles; writable/protected scope; evidence/baseline identity; reproducibility ceiling; claim layer (`structural repair`, `behavioral improvement`, `runtime compatibility`, or `subjective quality`); exact Python launcher when bundled scripts run. Require only evidence profiles the claim needs.

Full multi-platform hardening defaults to `portable-core,openai,codex,claude,copilot,cursor`. Default for "harden it": trust preflight when needed -> baseline -> audit -> contract/freeze -> trace research when applicable -> one bounded repair batch -> validate -> freeze -> package only when requested or clearly expected.

## Direct resource map

- [references/mature-skill-patterns.md](references/mature-skill-patterns.md): package control-plane patterns, Top-100/progressive loading, authority, and truthful closure.
- [references/resource-hardening-playbook.md](references/resource-hardening-playbook.md): evidence-based add/integrate/remove decisions for references, scripts, templates, examples, and evals.
- [references/evaluator-contract.md](references/evaluator-contract.md): frozen evaluator boundaries, claim-sensitive gates, evidence-layer separation, and static-score limits.
- [references/evidence-policy.md](references/evidence-policy.md): evidence precedence, research traceability, claim vocabulary, freshness, and source identity.
- [references/scenario-suite.md](references/scenario-suite.md): activation/non-activation, ambiguity, edge, coexistence, semantic-collision, regression, and adversarial coverage.
- [references/reproducibility-controls.md](references/reproducibility-controls.md): tree/evaluator identities, variability map, conditional evidence profiles, repair/freeze rules.
- [references/host-portability.md](references/host-portability.md): portable core, host profiles, capability-based execution, and runtime-proof limits.
- [references/packaging-and-validation.md](references/packaging-and-validation.md): folder/archive gates, deterministic packaging, atomic delivery, and receipt v3 correspondence.
- [scripts/trust_intake.py](scripts/trust_intake.py), [scripts/inventory_skill.py](scripts/inventory_skill.py), [scripts/hardening_audit.py](scripts/hardening_audit.py): trust preflight, deterministic inventory, and structural maturity audit.
- [scripts/validate_portability.py](scripts/validate_portability.py), [scripts/validate_hardened_skill.py](scripts/validate_hardened_skill.py), [scripts/reproducibility_controls.py](scripts/reproducibility_controls.py), [scripts/package_skill.py](scripts/package_skill.py): portability/readiness gates, identities/evaluator freeze, and deterministic package delivery.
- [assets/templates/hardening-contract.json.template](assets/templates/hardening-contract.json.template), [assets/templates/hardening-plan.md.template](assets/templates/hardening-plan.md.template), [assets/templates/hardening-report.md.template](assets/templates/hardening-report.md.template), [assets/templates/reference-file.md.template](assets/templates/reference-file.md.template), [assets/templates/scenario-suite.json.template](assets/templates/scenario-suite.json.template): optional durable run artifacts; use only when needed.
- [evals/activation-scenarios.json](evals/activation-scenarios.json) and [examples/hardening-scenarios.json](examples/hardening-scenarios.json): planned/calibration coverage only; never call them measured until executed.

## Closure and stop conditions

Report target/mode/source/hosts/runtime/Python; inventory and baseline/candidate/evaluator/source identities; audit plus reproducibility ceiling/variance/profile decisions; accepted/rejected changes with files/evaluators/gates; exact commands with `pass`/`fail`/`blocked`/`not-run`; separated evidence layers; research trace status when applicable; protected paths/files changed; residual risk/unmeasured behavior; and package/candidate/builder/archive identities only when produced and validated.

Stop or return a bounded partial result when target identity is ambiguous, no safe baseline exists, trust blockers remain, protected evidence must change without authorization, required evidence is missing, frozen evaluator/source identity drifts, claimed improvement lacks comparable execution, portability requires a host-private core dependency, passing requires weakening a hard gate, a breaking peer contract needs coordinated change, or package/receipt cannot be validated against the frozen candidate.

Before claiming hardened status, verify portable frontmatter, direct references, Top-100/reference-depth closure, justified resources, required tests/validators and requested host profiles, unchanged frozen evidence, truthful evidence labels, final candidate freeze, and exact package/receipt correspondence. No unvalidated edit may follow the final pass.
