---
name: research-traceability
description: Create, improve, audit, or refresh Agent Skills from research evidence by turning source-backed findings into explicit skill requirements, implementation links, evaluations, and a bidirectional traceability matrix. Use when research results must be transferred into a new or existing skill with evidence that every relevant finding was accounted for and every substantive change is justified. Do not use for standalone research, ordinary skill edits without research evidence, or generic requirements traceability unrelated to Agent Skills.
---

# Research Traceability

## Mission

Convert a bounded research corpus into a verifiable skill change set. Preserve a bidirectional chain from evidence to findings, requirements, implementation, and evaluation so the final result can prove corpus-bounded coverage without pretending the research itself was exhaustive.

## Scope

Own the convergence layer between research and skill authoring:

`research evidence -> atomic findings -> dispositions -> skill requirements -> implementation changes -> evaluations -> trace audit`

Support one target skill at a time. Keep the semantic core host-neutral and use capabilities rather than vendor-private tool names.

Do not replace a research workflow, generic skill authoring framework, benchmark framework, or security review. Invoke or reuse those capabilities when available, but keep this skill's acceptance authority limited to research-to-skill traceability.

## Modes

| Mode | Use when | Mutation |
|---|---|---|
| `create` | Build a new skill from a completed or concurrently obtained research corpus | yes |
| `improve` | Apply research-backed improvements to an existing skill | yes |
| `audit` | Measure research coverage and justification without changing the target | no |
| `refresh` | Reconcile new research against a prior traceability workspace and update only impacted skill behavior | yes |

If the user asks for research and skill transformation in one request, obtain and freeze the research corpus before deriving findings. Do not substitute a shallow ad hoc search for a requested deep-research phase.

## Required inputs and defaults

Resolve or infer before mutation:

- a bounded research corpus or a research capability that can produce one;
- one target skill identity, or a proposed skill identity in `create` mode;
- the requested mode;
- writable and protected paths;
- available filesystem, command, web, repository, and evaluation capabilities;
- package/delivery expectations.

Defaults:

- keep the traceability workspace outside the target skill tree;
- treat research completeness as `corpus-bounded`, never universal;
- preserve one portable Agent Skills core across hosts;
- snapshot material local evidence and the target baseline before mutation when possible;
- define and freeze evaluation cases before implementing the corresponding changes;
- prefer objective scripts and schemas for mechanics, and explicit semantic review for judgment.

## Reproducibility ceiling

Classify this skill as a mixed `research-analytic` plus `tool-action` workflow.

Guarantee mechanically:

- schema shape and IDs;
- referential integrity and bidirectionality;
- finding accounting;
- implementation and verification coverage calculations;
- source/target/evaluator identity when snapshots are available;
- package integrity, hashes, and receipts when the bundled packager is used.

Keep as bounded model judgment:

- whether a source supports a finding;
- whether two findings are semantically duplicates;
- whether a finding is relevant to the target skill;
- whether a requirement correctly preserves the finding's intent;
- whether an implementation truly satisfies a requirement;
- whether an evaluation is semantically adequate.

Never describe structural trace coverage as proof of semantic correctness.

## Resource loading

Load only what the active step needs:

- Read [references/workflow.md](references/workflow.md) for the ordered create/improve/audit/refresh workflow.
- Read [references/traceability-model.md](references/traceability-model.md) when creating or interpreting sources, findings, requirements, changes, evaluations, conflicts, and dispositions.
- Read [references/workspace-contract.md](references/workspace-contract.md) when creating, resuming, validating, or migrating a traceability workspace.
- Read [references/semantic-review.md](references/semantic-review.md) for the independent semantic trace review and anti-cheating checks.
- Read [references/reproducibility.md](references/reproducibility.md) when source identity, evaluator freezing, baseline preservation, packaging, recovery, or evidence claims matter.
- Read [references/refresh-impact.md](references/refresh-impact.md) only in `refresh` mode.
- Use [assets/schemas/traceability.schema.json](assets/schemas/traceability.schema.json) as the machine-readable data contract.
- Use `scripts/init_traceability.py` to initialize the canonical JSON workspace.
- Use `scripts/validate_traceability.py` for deterministic trace checks and coverage metrics.
- Use `scripts/snapshot_evidence.py` to freeze local research, target, or evaluator inputs when exact bytes matter.
- Use `scripts/validate_target_skill.py` for portable static checks of a generated or modified target skill.
- Use `scripts/package_target.py` for validated, hash-addressed, recovery-safe ZIP delivery when packaging is requested.

## Workflow

Follow [references/workflow.md](references/workflow.md). The mandatory control sequence is:

1. **Resolve mode and identities.** Identify the bounded research corpus, target, writable scope, protected evidence, and intended output.
2. **Freeze mutable evidence.** Snapshot material local research inputs and the existing target before analysis when feasible. Record pinned repository revisions or stable source identities for non-file evidence.
3. **Normalize sources.** Register evidence as `S-*` records. Preserve provenance and authority; do not treat a citation alone as a finding.
4. **Extract atomic findings.** Create one independently actionable claim per `F-*`. Consolidate semantic duplicates without erasing conflicting evidence.
5. **Account for every finding.** Assign exactly one disposition: `implement`, `already-covered`, `rejected`, `not-applicable`, `uncertain`, or `conflict`. Require rationale for every disposition.
6. **Derive requirements.** Translate accepted findings into testable `R-*` requirements. Do not copy research prose directly into `SKILL.md` when a narrower operational contract is sufficient.
7. **Inspect the target.** In `improve`, `audit`, and `refresh`, map current behavior before proposing changes. In `create`, establish the smallest cohesive package architecture.
8. **Define and freeze evaluations.** Create `E-*` records and concrete evaluator assets before implementing the related candidate changes whenever feasible. Preserve pre-existing evaluator assets unchanged.
9. **Plan changes.** Create `C-*` records. Every substantive change must satisfy at least one requirement; every accepted requirement must resolve to implementation or an explicit audit-only gap.
10. **Apply the smallest coherent mutation.** Preserve unrelated target behavior. Reject changes without reverse justification as probable gold plating.
11. **Compare baseline vs candidate when claiming improvement.** In `improve` and `refresh`, use the same frozen evaluator inputs for both arms when behavioral execution is available. Treat repairs as repairs when no comparable behavioral run exists; do not manufacture an improvement score from static checks.
12. **Validate mechanically.** Run `scripts/validate_traceability.py` and target-owned validators/tests. Run `scripts/validate_target_skill.py` when applicable.
13. **Review semantically.** Use [references/semantic-review.md](references/semantic-review.md) with fresh context or an independent reviewer when available. Validate source-to-finding fidelity, requirement derivation, implementation satisfaction, and evaluation adequacy.
14. **Repair diagnostically.** Fix one causal trace or implementation problem, rerun the same gate, then adjacent gates. Stop random repair after two non-improving rounds on the same objective diagnostic set.
15. **Freeze the passing candidate.** Verify frozen evaluator and source identities when used. Any later content change invalidates affected evidence and requires revalidation.
16. **Package atomically when requested.** Validate before commit, reject output aliases with the target or receipt, preserve the last-good package on failure, and emit a durable stage-aware receipt tied to exact bytes.

## Acceptance gates

For `create`, `improve`, and `refresh`, require all applicable hard gates:

- `finding_accounting = 100%`;
- every `implement` or `already-covered` finding traces to at least one requirement;
- every requirement traces backward to one or more findings;
- every final requirement traces to implementation and evaluation;
- every applied or existing substantive change traces backward to one or more requirements;
- every evaluation traces backward to one or more requirements;
- bidirectional references agree in both directions;
- no unresolved required conflict remains;
- no required evaluation is `fail` or still `planned` at finalization;
- no target-owned mandatory validator/test fails;
- no frozen evaluator or protected evidence changed after freeze;
- no final candidate edit occurs after the last passing validation;
- package/receipt identity matches the frozen candidate when delivered.

Allow `not-run` evaluations only when the required runtime/capability is unavailable. Record the limitation and do not claim runtime or behavioral proof from structural evidence.

For `audit`, report missing coverage as findings instead of mutating the target. Do not fail merely because proposed changes are intentionally unapplied.

## Trace completeness versus research completeness

Use precise claim language:

- Allowed: "100% of the relevant findings extracted from the frozen corpus were accounted for."
- Allowed: "All findings accepted for implementation trace to implemented changes and evaluations."
- Forbidden: "All relevant knowledge about the subject was applied" unless an external research method independently supports that completeness claim.

A complete trace matrix proves coverage of the recorded corpus and extraction, not completeness of human knowledge or the web.

## Output contract

For substantive runs, report:

1. mode, target identity, and workspace path;
2. frozen research, target, and evaluator identities when available;
3. source/finding/requirement/change/evaluation/conflict counts;
4. finding disposition counts;
5. trace coverage metrics and deterministic validator status;
6. semantic review status separately from mechanical validation;
7. files changed and the requirements they satisfy;
8. target-owned tests/validators and exact pass/fail/not-run status;
9. structural, behavioral, runtime, and semantic-review evidence separately;
10. unresolved uncertainty, conflicts, and capability limitations;
11. final package path and hash only when the package exists and applicable gates pass.

## Stop conditions

Stop or return a bounded partial result when:

- the research corpus required to justify changes is unavailable and cannot be obtained in scope;
- the target skill identity is ambiguous and choosing one risks mutating the wrong files;
- a material source conflict cannot be resolved without inventing evidence;
- a requested mutation requires changing frozen evaluator assets, protected evidence, secrets, or unrelated files;
- a final gate fails and the only path to green is weakening semantics, safety, coverage, or evaluator thresholds;
- output or receipt paths alias the source/target or one another;
- the user asks for universal research-completeness guarantees unsupported by the research method.
