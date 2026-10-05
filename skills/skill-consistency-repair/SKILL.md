---
name: skill-consistency-repair
description: use when one existing Agent Skills-compatible package has internal contract drift across SKILL.md, activation, scope, ownership, references, scripts, assets, examples, evals, validators, metadata, reports, or packaging. especially use for contradictions, broken or stale references, ownership/handoff drift, orphaned or duplicated resources, migration-only leakage, schema/validator drift, unsupported evidence claims, or package/receipt inconsistency. do not use for net-new skills, ordinary application code review, product/domain work, benchmark-only scoring, or generic hardening/cleanup unless consistency repair is the primary task.
---

# Skill Consistency Repair

## Mission

Audit, diagnose, repair, validate, and package an existing skill so its activation, authority, workflow, resources, outputs, evidence, recovery, and packaging form one evidence-grounded contract. Prefer reproducible diagnosis and the smallest coherent repair; never optimize for a cosmetic score.

## Activation and Routing

Use this skill when the primary problem is inconsistency **inside a skill package or between its representations**: contradictory instructions, activation/scope drift, ownership drift, broken references, resource integration ambiguity, validator/schema drift, migration leakage, evaluator/report mismatch, or packaging/receipt inconsistency.

Do not use as primary owner for net-new skill creation, ordinary application/code review, product planning, target-domain implementation, benchmark-only scoring, general security hardening, package cleanup, or token optimization unless an evidenced consistency defect is the reason for that work. For broad requests such as "improve" or "harden this skill", establish a consistency finding first; otherwise hand off to the appropriate skill workflow.

The host-neutral core covers `SKILL.md`, `references/`, `scripts/`, `assets/`, templates, `examples/`, `evals/`, tests/validators, and package metadata. Host-specific files such as `agents/openai.yaml` are adapters only: preserve them when intentional, and never let them broaden core scope or weaken gates.

## Mode Router

| Intent | Mode | Mutation | Required closure |
|---|---|---:|---|
| Find inconsistencies | `audit-only` | no | versioned consistency report |
| Decide repairs | `repair-plan` | no | evidence + owner + rollback + gate per repair |
| Repair target | `apply-repair` | yes | before/after validation + evaluator integrity + candidate receipt |
| Check repaired target | `validation-only` | no, except external reports | all declared gates rerun |
| Deliver archive | `package` | safe repair/package only | exact frozen candidate packaged atomically |

Use one primary mode. Combined requests run audit -> plan -> repair -> validation -> package without skipping gates.

## Required Inputs and Context

Resolve exactly one target root with `SKILL.md`; canonical writable/protected paths; an external work/evidence directory; baseline/last-known-good identity; material external evidence pins; runtime capabilities and exact Python 3.10+ launcher when bundled validators are needed; and acceptance evaluator inputs with freeze status. For archives, extract first and resolve the single skill root.

## Critical Invariants

- Preserve baseline/last-known-good before edits; keep run evidence, receipts, reports, and package outputs outside the target.
- Freeze acceptance evaluators before candidate mutation. If evaluator design changes, invalidate the old comparison, refreeze, then restart acceptance.
- Resolve contradictions by **concern-specific authority**, never by recency, verbosity, filename, or "SKILL.md always wins". Keep unresolved authoritative conflict visible as `contradictory` or `blocked`.
- Classify material resources only as `current`, `duplicate`, `obsolete`, `migration-only`, `contradictory`, `orphaned`, `integrable`, `blocked`, or `unknown`; static classification is provisional until semantic evidence is reviewed.
- Never delete from missing references alone. Trace imports, links, exact mentions, runtime consumers, tests, validators, examples/evals, packaging, migration/rollback/compatibility paths, and handoffs. `inspected-none` is not external absence; `unknown`/`blocked` blocks removal.
- Repair by diagnosis: one bounded hypothesis, smallest coherent patch, same causal gate first, then adjacent gates. Stop a branch after two objective non-improving repair rounds.
- Hard identity/evaluator/safety gates are non-waivable. Never edit fixtures/expected outputs merely to force acceptance, weaken a gate to pass, or claim runtime/behavioral/readiness improvement without matching evidence.
- Keep portable-core/spec conformance separate from host compatibility and runtime proof. Host adapters may narrow host behavior but cannot broaden core ownership or turn a core failure into pass.
- Use model judgment only for ownership, semantic duplication, obsolescence, contradiction meaning, and usefulness/integration; record direct evidence, authority owner, consumer/migration impact, confidence, chosen status, and evidence that would change the decision.
- After the last passing validation, freeze the exact candidate and make no further target edits. Package only that candidate, atomically, with recovery/last-known-good preserved.

## Quick-Start Workflow

1. **Establish identity and baseline:** resolve the root, canonical paths, protected scope, baseline, evidence pins, capabilities, and initial inventory/audit/report validation.
2. **Freeze evaluators:** freeze the exact inputs that decide acceptance before candidate changes.
3. **Trace relations and consumers:** build typed relations and per-dimension coverage; inspect authority, consumers, validators, examples/evals, packaging, migration, rollback, and handoffs for each material finding.
4. **Classify and resolve authority:** assign the closed status enum, apply concern-specific authority, use stricter behavior temporarily for unresolved safety/validation/deletion/packaging conflicts, and use differential schema/validator checks only when both interfaces are explicitly known and safe to execute.
5. **Repair minimally:** record the diagnosis and rollback, apply the smallest coherent patch, rerun the causal gate, then only the adjacent gates justified by impact.
6. **Apply the deletion gate:** remove only proven `obsolete` or approved duplicate consolidation after full trace, migrated consumers/compatibility, rollback evidence, and post-removal validation.
7. **Validate:** rerun deterministic inventory/audit/report validation, target-owned tests/validators, evaluator integrity, applicable package/conformance checks, and material external-source identity checks. Impact analysis suggests gates; it never replaces final validation.
8. **Freeze and deliver:** freeze exact final bytes, create the consistency receipt outside the target, package only the frozen candidate, and preserve recovery evidence on failure.

## Direct Decision Map

Load only the branch needed, directly from this root:

- Classification/removal: `references/consistency-taxonomy.md` for severity/status/evidence thresholds; `references/resource-integration.md` for tracing and deletion safety.
- Authority/ownership/relations: `references/authority-and-conflict-resolution.md` for concern ownership/conflicts; `references/semantic-ownership-review.md` for role drift/handoffs; `references/consistency-relations.md` for typed relations/coverage/disclosure depth.
- Equivalence/temporary exceptions: `references/contract-equivalence.md` for schema-validator differential checks; `references/managed-inconsistency.md` for bounded waivers and non-waivable gates.
- Repair/recovery: `references/repair-workflow.md` for executable repair/validation/package sequence; `references/recovery-and-receipts.md` for rollback and receipts.
- Claims/evaluation/reporting: `references/portability-and-conformance.md` for core/host/runtime claim separation; `references/report-contract.md` for report v3/evidence vocabulary; `references/scenario-guidelines.md` for evaluator/scenario integrity.

## Evidence and Output Contract

For substantive runs report target/mode/scope; baseline and evaluator identities; deterministic inventory/relations/trace coverage; classifications, conformance and authority/ownership findings; accepted/rejected repairs with diagnosis/rollback; exact validation outcomes; structural before/after evidence without relabeling it behavioral improvement; frozen candidate/receipt/package identities; active waivers; `unknown`/`blocked` items; and residual risk. Use behavioral/runtime/readiness claims only when matching executed or supplied evidence exists.

## Stop and Completion Gate

Stop or return a bounded partial result when target identity is ambiguous; baseline/recovery cannot be preserved; destructive action lacks authority/consumer evidence; protected evaluator state changed; source truth is missing; candidate/report/package identity mismatches; validation cannot pass safely; output aliases protected evidence; or success would require weakening a hard gate. Completion requires aligned activation/scope/modes/stops, direct critical-reference discovery, classified material resources, resolved-or-blocked authority conflicts, passing applicable target tests/validators, verified evaluator integrity, validated report/package evidence, receipt-to-candidate identity, and no edit after final freeze.

## Detailed Resource Map

Operational references remain one hop from `SKILL.md`; the summary above is sufficient to choose the correct branch before loading detail.

- `references/consistency-taxonomy.md`: finding severity, closed resource statuses, evidence minimums, and tie-breakers.
- `references/resource-integration.md`: deterministic trace dimensions, integration evidence, and deletion-safety gate.
- `references/authority-and-conflict-resolution.md`: authority by concern, stricter-gate default, and contradiction algorithm.
- `references/semantic-ownership-review.md`: ownership drift, adjacent-owner evidence, and handoff contract.
- `references/consistency-relations.md`: typed artifact relations, trace-coverage states, and progressive-disclosure topology.
- `references/portability-and-conformance.md`: portable-core/spec conformance, host compatibility, and runtime-proof separation.
- `references/contract-equivalence.md`: safe schema/validator differential verification when both interfaces are explicitly known.
- `references/managed-inconsistency.md`: bounded temporary waivers and non-waivable gates.
- `references/repair-workflow.md`: baseline, evaluator freeze, minimal repair loop, validation, and packaging commands.
- `references/recovery-and-receipts.md`: rollback, last-known-good, recovery evidence, and receipt semantics.
- `references/report-contract.md`: machine-readable report v3, evidence classes, conformance separation, and v1/v2 compatibility.
- `references/scenario-guidelines.md`: activation, regression, adversarial, and evaluator-freeze rules.

Operational tools:

- `scripts/inventory_skill.py`: deterministic inventory/fingerprint, typed relation/consumer graph, trace coverage, disclosure topology, and portable path-collision analysis.
- `scripts/consistency_audit.py`: report v3 with provisional classifications, relations, conformance dimensions, evidence classes, and static findings.
- `scripts/validate_consistency_report.py`: report schema validation.
- `scripts/freeze_evaluators.py`: evaluator SHA-256 freeze/verify.
- `scripts/create_consistency_receipt.py`: receipt bound to exact candidate, evaluator manifest, verifier identity, and policy identity.
- `scripts/impact_analysis.py`: deterministic changed/direct/transitive relation impact and narrow-to-broad gate suggestions.
- `scripts/package_skill.py`: canonical portable package entrypoint; validates before commit, emits deterministic ZIP bytes, preserves last-known-good output, and writes a versioned JSON receipt.
- `scripts/package_target_skill.py`: package implementation used by the canonical entrypoint; rejects portable path collisions before archive commit.
- `tests/test_tools.py`: self-tests for deterministic inventory, deletion safety, report validation compatibility, evaluator integrity, and packaging behavior.

Operational templates are `assets/templates/consistency-report.md.template`, `assets/templates/repair-plan.md.template`, `assets/templates/patch-decision-record.md.template`, `assets/templates/scenario-suite.json.template`, and `assets/templates/inconsistency-waiver.json.template`; copy/fill them only for their declared roles. `evals/activation-scenarios.json` is authoritative planned evaluator input; `examples/activation-scenarios.json` is illustrative only. Scenario metrics remain planned unless executed evidence is supplied. `agents/openai.yaml` is an optional host adapter and `assets/icon.svg` is its presentation asset, not a portable-core runtime dependency.

## Detailed Workflow Rules

1. **Identity and baseline.** Resolve one target root; canonicalize paths; keep work outputs outside the target; preserve baseline/last-known-good; snapshot or pin exact material external source evidence before it influences a decision; run inventory/audit/report validation before edits.
2. **Freeze evaluators.** Freeze the evaluator inputs that will decide acceptance. If evaluator design must change, do that as a separate phase, invalidate the old comparison, refreeze, then restart candidate acceptance.
3. **Trace relations, coverage, ownership, and consumers.** Build the typed relation graph and per-dimension coverage states first. For every material resource/finding trace authority plus imports, links, references, consumers, tests, validators, examples, packaging, migration paths, and handoffs. `inspected-none` is not equivalent to `not-inspected` and never proves external absence.
4. **Classify.** Use only: `current`, `duplicate`, `obsolete`, `migration-only`, `contradictory`, `orphaned`, `integrable`, `blocked`, `unknown`. Static classification is provisional; semantic judgment follows the evidence rubric.
5. **Resolve conflicts and equivalence.** Apply concern-specific authority. Never choose a source merely because it is newer, longer, or named `SKILL.md`. When a declarative schema and executable validator represent the same known interface, use a frozen shared differential corpus when safe/available; never guess or silently execute arbitrary validator interfaces. A known temporary inconsistency may use a bounded waiver only under `managed-inconsistency.md`; hard identity/evaluator/safety gates are non-waivable.
6. **Repair by diagnosis.** Record one bounded hypothesis; apply the smallest coherent patch directly tied to that diagnosis; rerun the same gate before adjacent gates. Stop a branch after two non-improving objective repair rounds.
7. **Removal gate.** Never delete a resource because it appears unused. Removal requires full trace evidence, an allowed final status, migrated consumers/compatibility, rollback evidence, and post-removal validation.
8. **Post-repair validation.** Use `scripts/impact_analysis.py` to identify the narrow causal and adjacent gates, then rerun inventory/audit/report validator, target-owned tests/validators, evaluator integrity, applicable package validation, and material external-source identity verification. Impact hints never replace final declared validation. Repeated inventory fingerprints must match when no bytes changed.
9. **Freeze final candidate.** After the last pass, make no further edits. Any change invalidates the affected evidence and requires revalidation.
10. **Receipt/delivery.** Create the consistency receipt outside the target. Package only the exact frozen candidate; preserve last-known-good/recovery evidence on failure.

## Portability Contract

The portable core is host-neutral. Keep portable-core/spec conformance separate from host compatibility: a host tolerance never turns a core failure into a pass. `agents/openai.yaml` is an optional adapter, not a runtime dependency. Use package-local relative paths, `pathlib`/standard-library filesystem APIs, and the host's available Python 3 launcher. Do not require vendor-private tool names, installation paths, Unix-only commands, or host-specific discovery locations for correctness.

Package delivery must reject casefold/Unicode-normalization path collisions and normalize ZIP entry ordering, timestamps, permission metadata, and POSIX archive paths so filesystem metadata differences do not change archive identity for the same candidate bytes. Package outputs and receipts stay outside the frozen target.

## Semantic Judgment Boundary

Keep model judgment only where semantics require it: ownership, semantic duplication, obsolescence, contradiction meaning, and usefulness/integration. For each such decision, require explicit subjects, direct evidence, authority owner, consumer impact, migration/compatibility impact, confidence, chosen status, and evidence that would change the decision. `unknown` or `blocked` is preferable to invented certainty.

## Output Contract

For substantive runs report:

1. target, mode, capabilities, writable/protected scope;
2. baseline and last-known-good identity;
3. evaluator manifest/freeze status;
4. deterministic inventory identity, typed relation/trace-coverage summary, and progressive-disclosure topology;
5. resource classification, portable-core/spec conformance, host-compatibility status, evidence classes, and authority/ownership findings;
6. accepted/rejected repairs with diagnosis and rollback;
7. exact validation commands with pass/fail/not-run;
8. before/after structural evidence without calling it behavioral improvement;
9. final candidate identity plus receipt-bound subject, verifier, policy, and evaluator identities;
10. package path only when a real validated archive exists;
11. active/expired managed-inconsistency waivers, remaining semantic uncertainty, `unknown`/`blocked` resources, and residual risk.

## Stop Conditions

Stop or return a bounded partial result when target root is ambiguous; baseline/last-known-good cannot be preserved; required authority or consumer evidence is unavailable for a destructive action; a protected evaluator changes after freeze; repair requires changing fixtures/expected outputs merely to pass; source truth is missing; candidate/report identity mismatches; validation cannot pass safely; output aliases target/protected evidence; rollback cannot be trusted; or passing would require weakening a hard gate.

## Finalization Checklist

Before claiming completion verify: portable frontmatter; aligned activation/scope/modes/stops; no broken local links; all material resources classified with trace evidence; no deletion from absence-of-reference alone; authority conflicts resolved or explicitly blocked; target scripts/tests pass; evaluator manifest verifies; final report validates; independent package validation passes when applicable; receipt matches final candidate bytes; last-known-good/recovery evidence is preserved; and no file changed after the final pass.
