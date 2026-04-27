# RFC Mode

Use for `rfc-proposal`.

`rfc-proposal` creates or updates governance RFC entries in `rfc-proposals.md`. Use it before a material decision is made when stakeholders need to compare options and align on roadmap, scope, sequencing, ownership, process, policy, vendor/tool, budget, accepted risk, go/no-go, or Mago handoff readiness.

Do not use this mode to author TDDs, implementation task decomposition, code changes, or decisions already made. Use Mago `technical-design` for spec-scoped architecture design docs. Use `adr-record` after the decision is accepted, rejected, deferred, deprecated, corrected, or superseded.

## Rules

- `BOARD_ROOT` is required.
- Keep `rfc-proposals.md` directly under `BOARD_ROOT`.
- Create the file with `scripts/write_artifact_scaffold.py <BOARD_ROOT>/rfc-proposals.md` when it does not exist.
- Create or update entries with `scripts/upsert_rfc_entry.py`; do not freehand shape RFC entries when the script can represent the proposal.
- RFCs may evolve during review, but preserve the proposal id and links.
- Define decision criteria before options.
- Include at least two options. Include `Do Nothing` or status quo when relevant.
- Leave `Outcome` as `pending` until approvers decide.
- When a proposal is decided, record the historical decision with `adr-record`.
- Validate with `scripts/validate_artifact.py <BOARD_ROOT>/rfc-proposals.md`.

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

When a Mago `technical-design.md` exists, link it as evidence only if the RFC needs stakeholder alignment on options, accepted risk, sequencing, ownership, or go/no-go. Do not copy its architecture contract into the RFC.
