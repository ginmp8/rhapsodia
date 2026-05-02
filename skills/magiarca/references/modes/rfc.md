# RFC Mode

Use `rfc-proposal` to create/update governance RFC entries in `rfc-proposals.md` before a material governance decision is made. It supports stakeholder comparison and alignment on roadmap, scope, sequencing, ownership, process, policy, vendor/tool, budget, accepted risk, go/no-go, or Mago handoff readiness.

Do not use for technical RFCs, TDDs, implementation task decomposition, code changes, execution ADRs, or decisions already made. Use Mago `technical-design`, planned ADRs, or RFC-style planning for spec-scoped architecture/design choices. Use Magia implementation ADRs for execution-grounded runtime decisions. Use `governance-decision` after the decision is accepted, rejected, deferred, deprecated, corrected, or superseded.

## Rules

`BOARD_ROOT` is required. Keep `rfc-proposals.md` directly under `BOARD_ROOT`. Create it with `scripts/write_artifact_scaffold.py <BOARD_ROOT>/rfc-proposals.md` when absent. Create/update entries with `scripts/upsert_rfc_entry.py`; do not freehand shape when the script can represent the proposal. Preserve proposal id and links during review. Define decision criteria before options. Include at least two options plus `Do Nothing`/status quo when relevant. Leave `Outcome` as `pending` until approvers decide. Record decided proposals with `governance-decision`. Validate with `scripts/validate_artifact.py <BOARD_ROOT>/rfc-proposals.md`.

## Required Entry Meaning

- `Status`: `draft`, `in_review`, `accepted`, `rejected`, `deferred`, or `superseded`.
- `Impact`: `high`, `medium`, or `low`.
- `Driver`: person or role driving the proposal.
- `Approvers`: people or roles that must approve.
- `Contributors`: people or roles consulted, or `none`.
- `Informed`: people or groups notified, or `none`.
- `Due Date`: `YYYY-MM-DD` or `unknown`.
- `Background`: current state, problem, why now, and cost of not deciding.
- `Assumptions`: assumptions with confidence and invalidation trigger where known.
- `Decision Criteria`: prioritized criteria used to evaluate options.
- `Options`: two or more options with honest trade-offs.
- `Recommendation`: preferred option or `unknown`.
- `Outcome`: `pending` until decided, then decision summary.
- `Links`: related roadmap, spec, ticket, ADR, or `none`.

When Mago `technical-design.md` exists, link it as evidence only if the RFC needs stakeholder alignment on options, accepted risk, sequencing, ownership, or go/no-go. Do not copy its architecture contract into the RFC.
When Magia `implementation-adr.md`, `implementation-notes.md`, or `validation-evidence.md` exists, cite it only to show execution reality, residual delivery risk, or release readiness evidence. Do not convert it into governance approval or a technical decision owned by Magiarca.
