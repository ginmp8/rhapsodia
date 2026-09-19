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

The executable contract is `references/ecosystem-handoff-contract.json`; use local `scripts/ecosystem_handoff.py` to produce or consume envelopes. Nomia produces `nomia_to_mago`, consumes `mago_to_nomia` and `magia_to_nomia`, and may retain `nomia_to_stakeholder` for its governance projection surface.

Required envelope metadata includes schema and mapping versions, producer and consumer roles, package version, timestamp, provenance, freshness, payload, evidence references, unknowns, conflicts, and deterministic `handoff_id`. State translations are explicit projections: Mago `done` maps to Nomia planning `complete`; Magia execution `done` maps to execution `complete`; Magia validation `passed` remains validation `passed`. The source skill retains authority.

Legacy envelope fields are not accepted as ecosystem handoff compatibility. Normal producers and consumers require strict handoff v3 and reject legacy, mixed-version, or unsupported envelopes before mutation. Historical governance material may be read only through `governance-adapt`; adaptation produces current Nomia-owned governance artifacts only when externally supplied current identities and provenance are available. New writers must emit the versioned schema. Stale or conflicting evidence is never silently accepted.

