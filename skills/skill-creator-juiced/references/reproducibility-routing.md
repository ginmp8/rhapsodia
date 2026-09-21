# Reproducibility Routing

Use this reference to decide whether `reproducibility-engineer` should participate and what it owns.

## Goal

Use reproducibility engineering only when it can materially reduce avoidable variance or create stronger evidence. Do not add schemas, scripts, evaluators, or repair machinery merely because those mechanisms are available.

Skill Creator Juiced always performs the lightweight local design pass in `references/reproducibility-by-design.md` for substantive creation/redesign. This routing file decides whether a dedicated `reproducibility-engineer` pass is still warranted after those proportional controls are considered.

## Decision gate

Evaluate these signals after target identity, capability boundary, and activation boundaries are known.

Invoke `reproducibility-engineer` when one or more **material** signals are present:

- equivalent valid inputs produce materially inconsistent semantic outcomes;
- critical behavior exists only as free-form prose although it can be expressed as a contract, schema, deterministic transform, or validator;
- mode selection, routing, or defaults are ambiguous enough to change outcomes;
- repetitive mechanics are rewritten by the model instead of executed by a deterministic helper;
- structured output lacks an enforceable schema or equivalent validator;
- validation depends unnecessarily on the same model judgment that generated the candidate;
- evaluators can change together with the candidate they judge;
- repair loops are open-ended, taste-driven, or lack stop conditions;
- external versions, source snapshots, immutable VCS identity, or runtime capabilities materially affect results but are not pinned or recorded;
- output destinations can alias inputs, protected files, evaluators, or receipts;
- a failed write/rollback can destroy the last-known-good artifact or recovery evidence;
- package identity, validated state, or delivery artifact cannot be traced with durable hashes/receipts tied to exact committed bytes;
- the user explicitly asks for deterministic, repeatable, reproducible, Archify-like, cross-agent-consistent, or regression-controlled behavior.

Mark `not-applicable` when:

- remaining variation is intentionally subjective and bounded by an adequate rubric;
- the target is a low-risk text-only skill whose semantics are already clear and no objective mechanism would improve reliability;
- existing validators/contracts already control the material variability;
- adding machinery would increase complexity without eliminating an observed source of variance.

## Mode selection

| Situation | Reproducibility mode |
|---|---|
| diagnose ceiling and gaps only | `audit-only` |
| user wants a transformation plan but no mutation | `plan-only` |
| material reproducibility gaps exist and mutation is authorized | `apply` |
| candidate was changed elsewhere and only reproducibility verification is needed | `validation-only` |
| no material gap | `not-applicable` |

For ordinary net-new skills, specialist routing may remain `not-applicable` after the local design pass. Re-evaluate after drafting for objective-artifact, tool-action, repository-evidence, benchmark, migration, and package-building skills, or whenever the user explicitly requires strong reproducibility. `not-applicable` means the specialist is unnecessary, not that reproducibility-by-design was skipped.

## Ordering

Recommended order for an existing skill:

```text
baseline
  -> package architecture
  -> activation/boundary review
  -> local reproducibility-by-design pass
  -> reproducibility decision gate
  -> reproducibility audit/apply when applicable
  -> documentation / code / testing / security / consistency
  -> harness / benchmark / hypothesis discovery / measured improvement
  -> change gate
  -> hardening
  -> final validation and package
```

A downstream specialist may find a new reproducibility defect. Route back only when it is a new, concrete issue with evidence; do not restart the whole pipeline.

## Ownership boundaries

- `skill-creator-juiced`: orchestrates, preserves target intent, chooses specialists, and owns final package workflow.
- `reproducibility-engineer`: owns the bounded reproducibility transformation or audit assigned to it.
- `skill-harness`: owns repeatable scenario execution and evidence capture infrastructure.
- `skill-benchmark`: owns scorecards and benchmark interpretation.
- `skill-improver`: owns bounded measured experiments after evaluator freeze.
- `skill-change-gate`: owns accept/reject decisions for material candidate changes.
- `skill-hardening`: owns final broad maturity review when requested/applicable.

Do not let two specialists independently edit the same concern. Assign one owner, then validate the result downstream.

## Cycle guards

- If the target skill is `reproducibility-engineer`, do not invoke `reproducibility-engineer` recursively. Apply this routing checklist and the target's own validators instead.
- If a specialist tries to route back to `skill-creator-juiced` while Juiced already owns the active workflow, keep Juiced as owner and treat the handoff as a recommendation.
- Do not invoke a specialist solely because another specialist named it. Require a new unmet responsibility and evidence.
- Record `cycle-prevented` in the specialist ledger when a recursion request is intentionally suppressed.

## Evidence contract

For every reproducibility routing decision record:

- target and current mode;
- material signals found or absent;
- selected reproducibility mode;
- specialist status: `invoked`, `checklist-only`, `not-applicable`, `unavailable`, or `cycle-prevented`;
- local reproducibility-by-design controls already present or intentionally omitted;
- files or control layers affected;
- validation required after the pass;
- remaining irreducible nondeterminism.

Do not call structural hardening measured behavioral improvement without executed scenario evidence.
