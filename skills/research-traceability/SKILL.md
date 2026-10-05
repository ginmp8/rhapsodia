---
name: research-traceability
description: Create, improve, audit, or refresh Agent Skills from a bounded research corpus by tracing source-backed findings into requirements, implementation, evaluations, and bidirectional evidence. Use when research must materially govern a skill change and every relevant finding/change needs explicit accounting. Do not use for standalone research, ordinary skill edits without research evidence, generic requirements traceability, or benchmark/security work whose acceptance does not depend on a research-to-skill chain.
---

# Research Traceability

## Mission and authority

Convert one bounded research corpus into a verifiable Agent Skill change set while preserving:

`research evidence -> atomic findings -> dispositions -> requirements -> implementation -> evaluations -> trace audit`

Own only the convergence layer between research and skill authoring. Do not replace the research workflow, generic skill authoring, benchmarking, security review, documentation review, packaging governance, or release governance. Keep the semantic core host-neutral and describe capabilities rather than vendor-private tool names.

## Activation and routing

Use this skill only when research evidence must materially determine a new or existing Agent Skill and the result needs explicit evidence accounting, justification, and verification.

Do not activate for standalone research/summaries; ordinary skill edits with no research corpus; generic product/software requirements traceability; or benchmark, security, documentation, or packaging work whose acceptance does not depend on research-to-skill traceability.

If research and skill transformation are requested together, obtain and freeze the requested research corpus before deriving findings. Never substitute a shallow ad hoc search for a requested deep-research phase.

## Modes

| Mode | Use when | Mutation |
|---|---|---|
| `create` | Build a new skill from a completed or concurrently obtained research corpus | yes |
| `improve` | Apply research-backed improvements to an existing skill | yes |
| `audit` | Measure research coverage and justification without changing the target | no |
| `refresh` | Reconcile new research against an earlier traced corpus and update only impacted behavior | yes |

## Core invariants

- Completeness is **corpus-bounded**, never universal: prove accounting of recorded findings, not completeness of human knowledge or the web.
- Every finding gets exactly one disposition plus rationale: `implement`, `already-covered`, `rejected`, `not-applicable`, `uncertain`, or `conflict`.
- Every substantive target change must reverse-trace to at least one accepted requirement and finding; remove probable gold plating.
- Freeze evaluator assets before related mutation when feasible. Never change an oracle, expected outcome, threshold, or protected evidence merely to obtain a pass.
- Separate mechanical proof from model judgment: structural coverage does not prove source support, derivation validity, implementation satisfaction, evaluation adequacy, or Top-100 semantic quality.
- In `improve`/`refresh`, use paired baseline-vs-candidate execution with identical frozen evaluator inputs before claiming measured behavioral improvement.
- Preserve the target discovery/control plane. If target `SKILL.md` exceeds 100 lines, keep purpose/scope, activation/routing, material modes, usable workflow, critical constraints, and direct branch-resource pointers within the first 100 physical lines.
- For editable supporting Markdown over 100 lines, require an early summary plus an accurate contents/section map. Prefer `SKILL.md -> supporting file`; required instructions must not depend on multi-hop Markdown chains.
- A passing candidate is immutable. Any later content change invalidates affected evidence and requires revalidation.
- Stop rather than invent or weaken evidence when the corpus is unavailable, target identity is ambiguous, a material conflict is unresolved, protected evidence would need mutation, or green would require weaker semantics/safety/coverage/evaluators.

## Quick-start workflow

1. **Resolve and freeze** — choose mode; identify corpus, target, writable/protected scope, output, baseline/evaluator identities, and freeze mutable evidence.
2. **Normalize and extract** — register `S-*` sources, derive atomic `F-*` findings, run an omission/duplicate/conflict/qualifier pass, and disposition every finding.
3. **Derive and map** — translate accepted findings into testable `R-*` requirements; map existing coverage and context-loading topology before proposing edits.
4. **Freeze evaluation and plan** — define/freeze `E-*` evaluations before related mutation when feasible; create justified `C-*` changes; preserve pre-existing evaluators.
5. **Mutate minimally and evaluate** — apply the smallest coherent change, compare baseline/candidate when claiming improvement, then run deterministic, target-owned, context-loading, behavioral when available, and semantic checks.
6. **Repair, freeze, deliver** — repair one causal defect at a time, rerun the same gate plus adjacent gates, freeze the passing candidate, and package atomically only after final validation.

## Minimum finalization gates

For `create`, `improve`, and `refresh`: require `finding_accounting = 100%`; complete bidirectional `F -> R -> C/E` justification; no unresolved required conflict; no required evaluation left `fail` or `planned`; mandatory target validators/tests passing; applicable Top-100/direct-reference checks passing; frozen evaluator/protected evidence unchanged; no candidate edit after the last passing validation; and delivered package/receipt identity matching the frozen candidate. Allow `not-run` only when the required runtime/capability is unavailable, record the limitation, and do not claim unavailable proof. In `audit`, report gaps without mutating the target.

## Direct resource map

All required Markdown is one hop from this file. Load only the active branch:

- [references/workflow.md](references/workflow.md) — ordered create/improve/audit/refresh execution and repair flow.
- [references/traceability-model.md](references/traceability-model.md) — `S/F/R/C/E/K` entities, dispositions, relations, coverage vs validity.
- [references/workspace-contract.md](references/workspace-contract.md) — canonical workspace, identity separation, IDs, schema lifecycle, resumption.
- [references/semantic-review.md](references/semantic-review.md) — independent semantic trace review, gold-plating checks, and Top-100 semantic review.
- [references/reproducibility.md](references/reproducibility.md) — evidence identities, evaluator freeze, paired comparison, repair/freeze/package boundaries.
- [references/refresh-impact.md](references/refresh-impact.md) — dependency invalidation only for `refresh` mode.
- [assets/schemas/traceability.schema.json](assets/schemas/traceability.schema.json) — machine-readable workspace contract.
- `scripts/init_traceability.py` initializes canonical JSON state; `scripts/validate_traceability.py` checks referential integrity/coverage; `scripts/snapshot_evidence.py` freezes local evidence; `scripts/validate_target_skill.py` runs portable target checks; `scripts/package_target.py` builds validated hash-addressed ZIPs.

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
