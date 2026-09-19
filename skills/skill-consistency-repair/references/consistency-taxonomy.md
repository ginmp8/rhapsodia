# Consistency Taxonomy

Use this taxonomy for findings and final resource classification. Static scripts may emit only mechanically provable provisional statuses; semantic statuses require the evidence rules below.

## Finding severity

- `blocker`: safe repair/package acceptance is impossible: ambiguous root, broken required link, protected evaluator drift, secret exposure, failed mandatory validator, candidate identity mismatch, or unresolved core authority conflict.
- `high`: likely wrong activation, ownership, normal-flow behavior, or output contract.
- `medium`: runnable but brittle: orphaned/integrable resources, duplicate contracts, stale validator bindings, scenario gaps, undocumented operational scripts, weak recovery.
- `low`: clarity or non-critical hygiene with no current contract break.

## Resource status enum

Every material resource should end with exactly one primary status and may include qualifiers. Allowed primary statuses:

- `current`: has a legitimate current owner/consumer or is an explicitly declared control/runtime asset.
- `duplicate`: duplicates bytes or semantics of another resource and no stronger status is proven. Duplication alone never authorizes removal.
- `obsolete`: an authoritative successor is proven, all current consumers are migrated, compatibility/migration commitments are resolved, and removal gates are satisfied.
- `migration-only`: legitimately required only for migration, legacy compatibility, rollback, or conversion paths. Normal-flow reachability is a defect unless explicitly intended.
- `contradictory`: conflicts with another authoritative source and the conflict is not yet resolved.
- `orphaned`: no inbound consumer/reference was found, but purpose or safety is not sufficient to call it obsolete.
- `integrable`: useful and in scope, but not yet wired into loading rules, consumers, validators, templates, examples, or workflow.
- `blocked`: classification or action cannot safely proceed because required evidence/protected state is unavailable or conflicting.
- `unknown`: evidence is insufficient for any stronger classification. `unknown` is a valid safe result and blocks removal.

## Evidence minimums and tie-breakers

1. `blocked` wins whenever protected evidence, target identity, or required consumer evidence is unavailable.
2. `contradictory` wins while authoritative sources disagree.
3. `migration-only` requires evidence that all legitimate consumers are migration/compatibility paths and that normal flow should not load it.
4. `current` requires at least one legitimate current owner/consumer or an explicit asset-only rationale.
5. `duplicate` requires byte identity or an evidenced semantic-contract duplication; path similarity is not enough.
6. `integrable` requires a documented useful purpose plus an identified integration point.
7. `obsolete` has the highest deletion burden: successor + zero live consumers + migration/rollback handled + owner approval/evidence + validation.
8. If evidence supports both `obsolete` and `unknown`, choose `unknown`. If it supports both `current` and `duplicate`, primary status may be `current` with `duplicate` as a qualifier.
9. No status produced only from "not referenced" permits deletion.

## Finding categories

1. **Package structure**: root identity, frontmatter, links, generated/noise files, symlink/path safety.
2. **Activation and scope**: description, positive/negative triggers, modes, stops, adjacent-skill boundaries.
3. **Ownership and role**: decision/artifact ownership, handoffs, authority drift.
4. **Resource integration**: classification, consumer graph, duplicate/obsolete/migration-only resources.
5. **Output and evidence**: report schema, claims, receipts, candidate/evaluator identity.
6. **Workflow and modes**: routing, mutation rights, baseline-before-repair, stop rules.
7. **Validation and packaging**: validators, evaluator freeze, package gates, last-known-good, atomic delivery.
8. **Authority conflict**: contradictions among control plane, references, scripts, schemas/validators, examples/evals, assets, and host metadata.

## Finding record

Each material finding includes: stable id; severity; category; subjects; evidence label; evidence; observed problem; smallest repair; validation gate; confidence. For semantic judgment, record the rubric dimension and why alternative classifications were rejected.
