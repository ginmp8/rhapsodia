---
name: research-traceability
description: Create, improve, audit, or refresh an Agent Skill when a bounded research corpus must materially govern the skill and every relevant finding/change needs explicit source-to-requirement-to-implementation/evaluation traceability. Do not use for standalone research, ordinary skill edits without research evidence, generic requirements traceability, or benchmark/security/documentation/packaging work whose acceptance does not depend on the research-to-skill chain.
---

# Research Traceability

## Mission and authority

Convert one bounded research corpus into a verifiable Agent Skill change set while preserving:

`research evidence -> atomic findings -> dispositions -> requirements -> implementation + evaluations -> trace audit`

Own only the convergence layer between research and skill authoring. Do not replace research collection, generic skill authoring/optimization, benchmarking, security review, documentation review, packaging governance, or release governance. Keep the semantic core host-neutral.

## Activation and routing

Activate only when all are true:

- the target is an Agent Skill or proposed Agent Skill;
- a bounded research corpus exists, or the user explicitly requested end-to-end research followed by skill transformation;
- research findings must materially determine requirements, behavior, or acceptance of the skill;
- the result needs explicit accounting from evidence through implementation and evaluation.

Do not activate for standalone research/summaries; ordinary skill edits with no research corpus; generic product/software requirements traceability; or benchmark, security, documentation, or packaging work whose acceptance does not depend on research-to-skill traceability.

If research and transformation are requested together, finish and freeze the requested research corpus before deriving findings. Never substitute a shallow ad hoc search for a requested deep-research phase.

## Modes

| Mode | Use when | Mutation |
|---|---|---|
| `create` | Build a new skill from a frozen research corpus | yes |
| `improve` | Apply research-backed improvements to an existing skill | yes |
| `audit` | Measure research accounting/justification without changing the target | no |
| `refresh` | Reconcile new research with a previously traced skill and update only impacted behavior | yes |

## Non-negotiable invariants

- Completeness is **corpus-bounded**, never universal: prove accounting of recorded findings, not completeness of human knowledge or the web.
- Every finding gets exactly one disposition plus rationale: `implement`, `already-covered`, `rejected`, `not-applicable`, `uncertain`, or `conflict`.
- Every substantive target change must reverse-trace to at least one accepted requirement and finding; remove probable gold plating rather than inventing justification.
- Freeze evaluator assets before related mutation when feasible. Never change an oracle, expected outcome, threshold, fixture, or protected evidence merely to obtain a pass.
- Structural coverage is not semantic proof: source support, deduplication, derivation validity, implementation satisfaction, evaluation adequacy, and Top-100 semantic quality require judgment.
- In `improve`/`refresh`, use paired baseline-vs-candidate execution with identical frozen evaluator inputs before claiming measured behavioral improvement.
- Preserve target discovery/control behavior: when `SKILL.md` exceeds 100 lines, its first 100 physical lines must contain scope/routing, material modes, usable workflow, critical constraints/finalization gates, and direct required-resource pointers.
- Editable supporting Markdown over 100 lines needs an early decision-useful preview plus accurate contents map; required instructions must not depend on hidden Markdown-to-Markdown hops.
- A passing candidate is immutable. Any later content change invalidates affected evidence and requires revalidation.
- Stop instead of inventing evidence, weakening semantics/safety/coverage/evaluators, mutating protected evidence, or finalizing through an unresolved material conflict.

## Quick-start workflow

1. **Resolve and freeze** — choose mode; identify corpus, target, writable/protected scope, output, baseline/evaluator identities; freeze mutable evidence.
2. **Normalize and extract** — register `S-*` sources; derive atomic `F-*` findings; run omission/duplicate/conflict/qualifier review; disposition every finding.
3. **Derive and map** — translate accepted findings into testable `R-*` requirements; map existing behavior and context-loading topology before proposing edits.
4. **Freeze evaluation and plan** — define/freeze `E-*` evaluations before related mutation when feasible; create only reverse-justified `C-*` changes.
5. **Mutate minimally and evaluate** — apply the smallest coherent change; run deterministic/target-owned checks, paired behavior when claimed, and semantic trace review.
6. **Repair, freeze, deliver** — repair one causal defect at a time; rerun the same gate plus adjacent gates; freeze passing bytes; package atomically only after final validation.

## Finalization and claim gate

For `create`, `improve`, and `refresh`, require all applicable conditions before calling the result final: `finding_accounting = 100%`; complete bidirectional `F -> R -> C/E` justification; no unresolved required conflict; no required evaluation left `fail` or `planned`; mandatory target validators/tests pass; applicable Top-100/direct-reference checks pass; frozen evaluator/protected evidence is unchanged; no candidate edit follows the last passing validation; and any delivered package/receipt matches the frozen candidate. `not-run` is allowed only for unavailable required capability/runtime, must carry a limitation, and cannot support the missing proof. In `audit`, report gaps without mutating the target.

Never present structural trace coverage, marker presence, or a Top-100 structure check as semantic correctness. Never claim measured behavioral improvement without paired comparable execution.

## Direct resource map

All required Markdown is one hop from this file. Load only what changes the active decision:

- [references/workflow.md](references/workflow.md) — load for the exact ordered execution, freeze/mutation timing, validation, repair, and delivery sequence.
- [references/traceability-model.md](references/traceability-model.md) — load when creating/reviewing `S/F/R/C/E/K` records, dispositions, bidirectional links, coverage, or conflicts.
- [references/workspace-contract.md](references/workspace-contract.md) — load when initializing, persisting, resuming, versioning, or allocating IDs in `traceability.json`.
- [references/semantic-review.md](references/semantic-review.md) — load before final semantic acceptance or whenever source->finding->requirement->change/evaluation truth must be judged.
- [references/reproducibility.md](references/reproducibility.md) — load when freezing evidence/evaluators, comparing baseline vs candidate, controlling variance, or packaging exact accepted bytes.
- [references/refresh-impact.md](references/refresh-impact.md) — load only in `refresh` mode to compute research deltas and downstream invalidation.
- [assets/schemas/traceability.schema.json](assets/schemas/traceability.schema.json) — machine-readable workspace contract.
- `scripts/init_traceability.py` initializes state; `scripts/validate_traceability.py` checks referential integrity/coverage; `scripts/snapshot_evidence.py` freezes local evidence; `scripts/validate_target_skill.py` checks portable target structure; `scripts/package_target.py` builds validated hash-addressed ZIPs.

## Required inputs and defaults

Resolve or infer one bounded research corpus (or explicit research phase), exactly one target identity, mode, writable/protected paths, available capabilities, and package expectation. Default to an external traceability workspace, `corpus-bounded` completeness, portable Agent Skills core, evidence snapshots when possible, evaluator definition before related mutation, objective scripts for mechanics, and explicit semantic review for judgment.

## Detailed execution

Use [references/workflow.md](references/workflow.md) for the full 14-step order. The root workflow above is authoritative for phase ordering; the reference adds branch detail rather than changing authority.

## Output contract

For substantive runs, report mode/target/workspace; frozen research/target/evaluator identities; `S/F/R/C/E/K` counts and dispositions; trace metrics; deterministic versus semantic-review status; files changed and satisfied requirements; exact target-owned test/validator outcomes; structural/behavioral/runtime/semantic evidence separately; context-loading/Top-100 status when applicable; unresolved uncertainty/conflicts/capability limits; and final package path/hash only after applicable gates pass.

## Stop conditions

Stop or return a bounded partial result when the required research corpus cannot be obtained; target identity is ambiguous; material source conflict cannot be resolved without invention; mutation would alter frozen/protected evidence, secrets, or unrelated files; green requires weakening semantics/safety/coverage/evaluators; output/receipt aliases protected inputs; context-loading repair would delete required semantics instead of reorganizing them; final freeze/validation fails; or the user requests unsupported universal completeness claims.
