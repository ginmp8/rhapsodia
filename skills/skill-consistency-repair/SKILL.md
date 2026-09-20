---
name: skill-consistency-repair
description: use when asked to audit, validate, diagnose, repair, or package agent skill packages for consistency across skill.md, activation, scope, ownership, references, scripts, assets, examples, evals, validators, metadata, reports, and packaging. especially use for contradictions, ownership drift, orphaned or duplicated resources, stale scaffold, broken references, migration leakage, validator drift, weak handoffs, or unsupported evidence claims. do not use for ordinary application code review, product planning, target-domain implementation, or benchmark-only scoring without consistency repair.
---

# Skill Consistency Repair

## Purpose

Audit and repair reusable Agent Skills packages so activation, authority, workflow, resources, outputs, validation, recovery, and packaging form one evidence-grounded contract. Optimize for reproducible diagnosis and minimal repairs, not for maximizing a cosmetic score.

## Scope Boundary

Use only for target skill packages. The host-neutral core covers `SKILL.md`, `references/`, `scripts/`, `assets/`, templates, `examples/`, `evals/`, tests/validators, and package metadata. Host-specific files such as `agents/openai.yaml` are optional adapters: preserve them when intentional, but never let them broaden core scope or weaken gates.

Out of scope: target-domain implementation, unrelated repositories, generic benchmark-only work, evaluator/expected-output edits made solely to force a pass, and behavioral claims without executed or supplied evidence.

## Required Inputs

Resolve before mutation:

1. exactly one `TARGET_SKILL_PATH` with a root `SKILL.md`;
2. primary mode: `audit-only`, `repair-plan`, `apply-repair`, `validation-only`, or `package`;
3. writable target scope and protected paths;
4. work/evidence directory outside the target, plus immutable snapshots/pins for material external evidence used to decide ownership, compatibility, or removal;
5. available runtime capabilities, including an available Python 3.10+ launcher when bundled validators are required; record the exact launcher instead of assuming `python` or `python3`;
6. baseline/last-known-good strategy;
7. evaluator inputs used for acceptance and their freeze status.

For archives, extract to a work directory and resolve the single skill root first.

## Mode Router

| Intent | Mode | Mutation | Closure |
|---|---|---:|---|
| Find inconsistencies | `audit-only` | no | versioned consistency report |
| Decide repairs | `repair-plan` | no | each repair maps to evidence, owner, rollback, and gate |
| Repair target | `apply-repair` | yes | before/after validation + evaluator integrity + candidate receipt |
| Check repaired target | `validation-only` | no, except external reports | all declared gates rerun |
| Deliver archive | `package` | only safe repair/package work | exact frozen candidate packaged atomically |

Use one primary mode. Combined requests run audit -> plan -> repair -> validation -> package without skipping gates.

## Progressive Loading

Load only what the active finding needs:

- `references/consistency-taxonomy.md`: severity, closed resource statuses, evidence minimums, tie-breakers.
- `references/resource-integration.md`: consumer/reference tracing and deletion-safety gate.
- `references/authority-and-conflict-resolution.md`: authority by concern and contradiction resolution.
- `references/semantic-ownership-review.md`: ownership drift and handoffs.
- `references/repair-workflow.md`: baseline, evaluator freeze, minimal repair loop, validation, packaging.
- `references/recovery-and-receipts.md`: rollback, last-known-good, recovery evidence, receipts.
- `references/report-contract.md`: machine-readable report v2 and evidence labels.
- `references/scenario-guidelines.md`: activation, regression, adversarial, and evaluator-freeze rules.

Operational tools:

- `scripts/inventory_skill.py`: sorted inventory, per-file SHA-256, deterministic fingerprint, reference/consumer graph.
- `scripts/consistency_audit.py`: provisional classifications plus findings; static evidence only.
- `scripts/validate_consistency_report.py`: report schema validation.
- `scripts/freeze_evaluators.py`: evaluator SHA-256 freeze/verify.
- `scripts/create_consistency_receipt.py`: receipt bound to the exact final candidate and evaluator manifest.
- `scripts/package_skill.py`: canonical portable package entrypoint; emits deterministic ZIP bytes, validates before commit, preserves last-known-good output, and writes a versioned JSON receipt.
- `scripts/package_target_skill.py`: package implementation used by the canonical entrypoint.
- `tests/test_tools.py`: self-tests for deterministic inventory, deletion safety, report v2 validation, and evaluator freeze integrity.

Operational templates are `assets/templates/consistency-report.md.template`, `assets/templates/repair-plan.md.template`, `assets/templates/patch-decision-record.md.template`, and `assets/templates/scenario-suite.json.template`; copy/fill them only for their declared report/plan/decision/scenario roles.

`evals/activation-scenarios.json` is the authoritative planned evaluator suite. `examples/activation-scenarios.json` is illustrative only. Scenario metrics are planned unless executed evidence is supplied.

## Workflow

1. **Identity and baseline.** Resolve one target root; canonicalize paths; keep work outputs outside the target; preserve baseline/last-known-good; snapshot or pin exact material external source evidence before it influences a decision; run inventory/audit/report validation before edits.
2. **Freeze evaluators.** Freeze the evaluator inputs that will decide acceptance. If evaluator design must change, do that as a separate phase, invalidate the old comparison, refreeze, then restart candidate acceptance.
3. **Trace ownership and consumers.** For every material resource/finding trace authority plus imports, links, references, consumers, tests, validators, examples, packaging, migration paths, and handoffs.
4. **Classify.** Use only: `current`, `duplicate`, `obsolete`, `migration-only`, `contradictory`, `orphaned`, `integrable`, `blocked`, `unknown`. Static classification is provisional; semantic judgment follows the evidence rubric.
5. **Resolve conflicts.** Apply concern-specific authority. Never choose a source merely because it is newer, longer, or named `SKILL.md`. Frozen evaluator expectations cannot be changed during candidate acceptance.
6. **Repair by diagnosis.** Record one bounded hypothesis; apply the smallest coherent patch directly tied to that diagnosis; rerun the same gate before adjacent gates. Stop a branch after two non-improving objective repair rounds.
7. **Removal gate.** Never delete a resource because it appears unused. Removal requires full trace evidence, an allowed final status, migrated consumers/compatibility, rollback evidence, and post-removal validation.
8. **Post-repair validation.** Rerun inventory/audit/report validator, target-owned tests/validators, evaluator integrity, applicable package validation, and material external-source identity verification. Repeated inventory fingerprints must match when no bytes changed.
9. **Freeze final candidate.** After the last pass, make no further edits. Any change invalidates the affected evidence and requires revalidation.
10. **Receipt/delivery.** Create the consistency receipt outside the target. Package only the exact frozen candidate; preserve last-known-good/recovery evidence on failure.

## Portability Contract

The portable core is host-neutral. `agents/openai.yaml` is an optional adapter, not a runtime dependency. Use package-local relative paths, `pathlib`/standard-library filesystem APIs, and the host's available Python 3 launcher. Do not require vendor-private tool names, installation paths, Unix-only commands, or host-specific discovery locations for correctness.

Package delivery must normalize ZIP entry ordering, timestamps, permission metadata, and POSIX archive paths so filesystem metadata differences do not change the archive identity for the same candidate bytes. Package outputs and receipts stay outside the frozen target.

## Semantic Judgment Boundary

Keep model judgment only where semantics require it: ownership, semantic duplication, obsolescence, contradiction meaning, and usefulness/integration. For each such decision, require explicit subjects, direct evidence, authority owner, consumer impact, migration/compatibility impact, confidence, chosen status, and evidence that would change the decision. `unknown` or `blocked` is preferable to invented certainty.

## Output Contract

For substantive runs report:

1. target, mode, capabilities, writable/protected scope;
2. baseline and last-known-good identity;
3. evaluator manifest/freeze status;
4. deterministic inventory identity and trace summary;
5. resource classification and authority/ownership findings;
6. accepted/rejected repairs with diagnosis and rollback;
7. exact validation commands with pass/fail/not-run;
8. before/after structural evidence without calling it behavioral improvement;
9. final candidate identity and machine-readable receipt;
10. package path only when a real validated archive exists;
11. remaining semantic uncertainty, `unknown`/`blocked` resources, and residual risk.

## Stop Conditions

Stop or return a bounded partial result when target root is ambiguous; baseline/last-known-good cannot be preserved; required authority or consumer evidence is unavailable for a destructive action; a protected evaluator changes after freeze; repair requires changing fixtures/expected outputs merely to pass; source truth is missing; candidate/report identity mismatches; validation cannot pass safely; output aliases target/protected evidence; rollback cannot be trusted; or passing would require weakening a hard gate.

## Finalization Checklist

Before claiming completion verify: portable frontmatter; aligned activation/scope/modes/stops; no broken local links; all material resources classified with trace evidence; no deletion from absence-of-reference alone; authority conflicts resolved or explicitly blocked; target scripts/tests pass; evaluator manifest verifies; final report validates; independent package validation passes when applicable; receipt matches final candidate bytes; last-known-good/recovery evidence is preserved; and no file changed after the final pass.
