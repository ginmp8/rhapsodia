# Delivery State, Risk Metrics, And Handoffs

Use with the canonical governance record. Nomia owns governance state; planning, execution, validation, and release states are reported only from attributed evidence.

## State Dimensions

Keep these dimensions separate:

| Dimension | Authority | Values |
|---|---|---|
| governance | Nomia | `intake`, `triage`, `planned`, `ready`, `in_progress`, `blocked`, `validating`, `releasable`, `released`, `closed`, `canceled`, `superseded`, `unknown` |
| planning | Mago evidence | `unknown`, `not_started`, `planned`, `ready`, `blocked`, `complete` |
| execution | Magia evidence | `unknown`, `not_started`, `ready`, `in_progress`, `blocked`, `complete` |
| validation | Magia evidence | `unknown`, `not_started`, `in_progress`, `blocked`, `passed`, `failed` |
| release | supplied release evidence | `unknown`, `not_released`, `releasable`, `released`, `closed`, `canceled`, `superseded` |

A governance state never upgrades a technical dimension. For example, governance `ready` does not imply planning or execution readiness; `released` requires release evidence and does not let Nomia certify technical validation.

## Permitted Governance Transitions

Normal forward flow:

```text
intake -> triage -> planned -> ready -> in_progress -> validating -> releasable -> released -> closed
```

`blocked` may be entered from any nonterminal active state and may return only to the documented prior state or a newly evidenced state. `canceled` and `superseded` may be entered from any nonterminal state with a material decision record. Terminal states are `closed`, `canceled`, and `superseded`; reopening requires a new governance decision and explicit previous/new values.

Use `scripts/evaluate_governance.py --transition <from> <to>` to validate a transition.

## Deterministic Metrics

Use `scripts/evaluate_governance.py <ops.yaml> --as-of <ISO-8601>`. The script returns a value only when the required evidence is present; otherwise it returns `null` with `missing_evidence`.

| Metric | Required evidence |
|---|---|
| intake age | `timestamps.intake_at` |
| time in current state | `timestamps.state_entered_at` |
| blocked duration | `timestamps.blocked_since` while blocked |
| target-date variance | `planning.target_date` and as-of date; actual closure/release date when terminal |
| decision latency | `timestamps.decision_requested_at`, `timestamps.decision_at` |
| planning lead time | `timestamps.planning_started_at`, `timestamps.planning_ready_at` |
| execution lead time | attributed `timestamps.execution_started_at`, `timestamps.execution_completed_at` |
| validation age | attributed validation observation timestamp |
| dependency exposure | dependency status/severity evidence |
| stakeholder-response age | request and response timestamps |
| delivery confidence | evidence completeness, blocker/risk severity, conflicts, staleness; never intuition |
| risk trend | at least two dated `risk_history` entries |

## Material Change Provenance

Every material change records:

- field path;
- previous value and new value;
- actor or `unknown`;
- change timestamp;
- evidence source;
- rationale;
- affected commitments;
- consequence for Nomia-to-Mago, Mago-to-Nomia, or Magia-to-Nomia handoffs.

Business acceptance of risk is a Nomia governance decision. Technical risk assessment remains Mago or Magia evidence.

## Typed Handoff Envelopes

All handoffs use an envelope with `direction`, `source`, `observed_at`, `provenance`, `freshness_days`, and `payload`. Acceptance is mechanical:

| Direction | Required payload | Acceptance | Rejection reasons |
|---|---|---|---|
| `nomia_to_mago` | `feature_key`, outcome, scope summary, owner/unknown, dependencies, readiness, candidate spec id/provenance when non-null | governance context current; no technical design/tasks; identity externally sourced | missing outcome/provenance, stale context, invented identity, technical content |
| `mago_to_nomia` | `spec_id`, planning state, planning evidence reference, observed time | identity/provenance valid and evidence current | missing source, stale/conflicting state, identity mismatch |
| `magia_to_nomia` | execution and/or validation state, evidence reference, observed time | technical state attributed and current | unsupported completion claim, stale/conflicting evidence, missing source |
| `nomia_to_stakeholder` | audience, summary, unknowns, decision needed, evidence references | derived from canonical facts and output profile | hidden unknowns, unsupported completion, confidential/audit data leaked to wrong audience |

Use `scripts/evaluate_governance.py --handoff <json-or-yaml>` to return `accepted`, `draft`, `stale`, `conflicting`, or `rejected` with reasons.
