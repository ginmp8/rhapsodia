---
name: research-traceability
description: Create, improve, audit, or refresh Agent Skills from research evidence by turning source-backed findings into explicit skill requirements, implementation links, evaluations, and a bidirectional traceability matrix. Use when research results must be transferred into a new or existing skill with evidence that every relevant finding was accounted for and every substantive change is justified. Do not use for standalone research, ordinary skill edits without research evidence, generic requirements traceability unrelated to Agent Skills, or benchmark/security work that does not depend on a research-to-skill evidence chain.
---

# Research Traceability

## Mission and authority

Convert one bounded research corpus into a verifiable Agent Skill change set. Preserve a bidirectional chain:

`research evidence -> atomic findings -> dispositions -> requirements -> implementation -> evaluations -> trace audit`

Own only the convergence layer between research and skill authoring. Do not replace the research workflow, generic skill authoring, benchmarking, security review, or release governance. Keep the semantic core host-neutral and describe capabilities rather than vendor-private tool names.

## Activation and routing

Use this skill when research evidence must materially determine a new or existing Agent Skill and the result needs explicit evidence accounting, justification, and verification.

Do not activate for:

- standalone research or literature/web summaries;
- ordinary skill edits with no research corpus;
- generic product/software requirements traceability;
- benchmark, security, documentation, or packaging work whose acceptance does not depend on research-to-skill traceability.

If research and skill transformation are requested together, obtain and freeze the requested research corpus before deriving findings. Never substitute a shallow ad hoc search for a requested deep-research phase.

## Modes

| Mode | Use when | Mutation |
|---|---|---|
| `create` | Build a new skill from a completed or concurrently obtained research corpus | yes |
| `improve` | Apply research-backed improvements to an existing skill | yes |
| `audit` | Measure research coverage and justification without changing the target | no |
| `refresh` | Reconcile new research against an earlier traced corpus and update only impacted behavior | yes |

## Core invariants

- Treat completeness as **corpus-bounded**, never universal: traceability can prove accounting of recorded findings, not completeness of human knowledge or the web.
- Account for every finding with exactly one disposition: `implement`, `already-covered`, `rejected`, `not-applicable`, `uncertain`, or `conflict`, plus rationale.
- Require reverse justification: every substantive target change must trace back to at least one accepted requirement and finding; remove probable gold plating.
- Freeze evaluator assets before candidate mutation when feasible. Never change an oracle, expected outcome, threshold, or protected evidence merely to obtain a pass.
- Separate mechanical proof from model judgment. Structural coverage does not prove that a source supports a finding, a requirement preserves intent, a change satisfies it, or an evaluation is adequate.
- In `improve`/`refresh`, use paired baseline-vs-candidate execution with the same frozen evaluator inputs before claiming measured behavioral improvement.
- Preserve the target skill's discovery/control plane. If target `SKILL.md` exceeds 100 lines, keep purpose/scope, activation/routing, material modes, usable workflow, critical constraints, and direct branch-resource pointers within the first 100 physical lines. For supporting Markdown over 100 lines, expose an early summary plus contents/index. Prefer `SKILL.md -> supporting file`; do not hide required instructions behind multi-hop Markdown chains.
- A passing candidate is immutable: any later content change invalidates affected evidence and requires revalidation.

## Workflow at a glance

1. **Resolve and freeze** — choose mode; identify corpus, target, writable/protected scope, output, and baseline/evaluator identities; freeze mutable evidence.
2. **Normalize and extract** — register `S-*` sources, derive atomic `F-*` findings, detect duplicates/conflicts/qualifiers, and disposition every finding.
3. **Derive and map** — translate accepted findings into testable `R-*` requirements; map existing coverage and target control-plane quality before proposing edits.
4. **Freeze evaluation and plan** — create `E-*` evaluations before related mutation when feasible; create justified `C-*` changes; preserve pre-existing evaluators.
5. **Mutate minimally and evaluate** — apply the smallest coherent change, compare baseline/candidate when claiming improvement, then run deterministic, target-owned, context-loading, and semantic checks.
6. **Repair, freeze, deliver** — repair one causal defect at a time, rerun the same gate plus adjacent gates, freeze the passing candidate, and package atomically only after final validation.

## Resource loading

Load only the active branch; all required Markdown is directly reachable from this root:

- [references/workflow.md](references/workflow.md) — detailed ordered create/improve/audit/refresh workflow.
- [references/traceability-model.md](references/traceability-model.md) — `S/F/R/C/E/K` entities, dispositions, bidirectional relations, and coverage vs validity.
- [references/workspace-contract.md](references/workspace-contract.md) — canonical workspace, identity separation, IDs, resumption, and schema lifecycle.
- [references/semantic-review.md](references/semantic-review.md) — independent semantic trace review and anti-cheating checks.
- [references/reproducibility.md](references/reproducibility.md) — evidence identity, evaluator freeze, paired comparison, recovery, and claim boundaries.
- [references/refresh-impact.md](references/refresh-impact.md) — dependency invalidation only for `refresh` mode.
- [assets/schemas/traceability.schema.json](assets/schemas/traceability.schema.json) — machine-readable workspace contract.
- `scripts/init_traceability.py` — initialize canonical JSON state.
- `scripts/validate_traceability.py` — deterministic referential-integrity and coverage checks.
- `scripts/snapshot_evidence.py` — freeze local research, target, or evaluator bytes.
- `scripts/validate_target_skill.py` — portable static checks for a generated or modified target skill.
- `scripts/package_target.py` — validated, hash-addressed, recovery-safe ZIP delivery.

## Required inputs and defaults

Resolve or infer before mutation:

- one bounded research corpus, or a research capability that can produce one;
- exactly one target skill identity, or a proposed identity in `create` mode;
- mode, writable/protected paths, available capabilities, and package expectations.

Default to an external traceability workspace, `corpus-bounded` completeness, portable Agent Skills core, baseline/evidence snapshots when possible, pre-mutation evaluator definition, and objective scripts/schemas for mechanics with explicit semantic review for judgment.

## Reproducibility ceiling

Classify the workflow as mixed `research-analytic` plus `tool-action`.

Mechanically guarantee schema/ID shape, referential integrity, finding accounting, coverage calculations, available source/target/evaluator identities, context-loading structure checks, and package hashes/receipts. Keep source support, semantic deduplication, relevance, requirement derivation, implementation satisfaction, evaluation adequacy, and Top-100 semantic quality as bounded model judgment.

Never present structural trace coverage or Top-100 marker checks as semantic correctness.

## Detailed workflow

Follow [references/workflow.md](references/workflow.md). Preserve this sequence:

1. resolve mode and identities;
2. freeze mutable evidence and baseline;
3. register sources as `S-*`;
4. extract atomic findings as `F-*` with a second omission/duplicate/conflict pass;
5. disposition every finding with rationale;
6. derive testable `R-*` requirements;
7. inspect existing target behavior and context-loading topology;
8. define and freeze `E-*` evaluations before related mutation when feasible;
9. plan justified `C-*` changes;
10. apply the smallest coherent mutation;
11. compare frozen baseline vs candidate before measured improvement claims;
12. validate mechanically, including target-owned checks and context-loading structure;
13. review semantic trace validity with fresh context/independent review when available;
14. repair one causal defect at a time and stop a branch after two non-improving rounds on the same objective diagnostics;
15. freeze the passing candidate and invalidate affected evidence after any later edit;
16. package atomically when requested, preserving last-good output and exact-byte receipts.

## Acceptance gates

For `create`, `improve`, and `refresh`, require all applicable gates:

- `finding_accounting = 100%`;
- every `implement`/`already-covered` finding traces to a requirement;
- every requirement traces backward to findings and forward to implementation plus evaluation;
- every substantive applied/existing change traces backward to requirements;
- every evaluation traces backward to requirements and bidirectional references agree;
- no unresolved required conflict remains;
- no required evaluation is `fail` or `planned` at finalization;
- no mandatory target validator/test fails;
- target context-loading changes satisfy the Top-100/direct-reference contract when applicable, with semantic adequacy reviewed separately from mechanical structure;
- no frozen evaluator/protected evidence changes after freeze;
- no candidate edit occurs after the last passing validation;
- delivered package/receipt identity matches the frozen candidate.

Allow `not-run` only when required runtime/capability is unavailable; record the limitation and do not claim unavailable proof. In `audit`, report gaps without mutating the target.

## Trace completeness versus research completeness

Allowed: "100% of the relevant findings extracted from the frozen corpus were accounted for." Allowed: "All findings accepted for implementation trace to implemented changes and evaluations." Do not claim all relevant external knowledge was applied unless the research method independently supports that statement.

## Output contract

For substantive runs, report mode/target/workspace; frozen research/target/evaluator identities; `S/F/R/C/E/K` counts and dispositions; trace metrics; deterministic versus semantic-review status; files changed and satisfied requirements; exact target-owned test/validator outcomes; structural/behavioral/runtime/semantic evidence separately; context-loading/Top-100 status when applicable; unresolved uncertainty/conflicts/capability limits; and final package path/hash only after applicable gates pass.

## Stop conditions

Stop or return a bounded partial result when the required research corpus cannot be obtained; target identity is ambiguous; material source conflict cannot be resolved without invention; mutation would alter frozen/protected evidence, secrets, or unrelated files; green requires weakening semantics/safety/coverage/evaluators; output/receipt aliases protected inputs; context-loading repair would delete required semantics instead of reorganizing them; final freeze/validation fails; or the user requests unsupported universal completeness claims.
