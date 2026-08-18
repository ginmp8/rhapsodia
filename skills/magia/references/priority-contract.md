# Ecosystem Priority Contract v2

This package implements `nomia-mago-magia-priority-v2`. The machine-readable source is [priority-contract.json](priority-contract.json). The coordinated package release is frozen by [ecosystem-compatibility.json](ecosystem-compatibility.json).

## Authority

| Concept | Owner | Meaning | Consumers |
|---|---|---|---|
| `business_priority` | Nomia | Business urgency and importance | Mago and Magia, read-only |
| `technical_criticality` | Mago | Technical risk, blast radius, reversibility, and engineering impact | Magia and Nomia, read-only |
| `execution_sequence` | Mago | Dependency-safe technical execution order and lane | Magia executes; Nomia may project |

No skill may write another skill's concept or convert one concept into another as if the enums were equivalent.

## Normative values

- `business_priority.level`: `unknown`, `low`, `medium`, `high`, `urgent`.
- `technical_criticality.level`: `low`, `normal`, `high`, `critical`.
- `execution_sequence.lane`: `expedite`, `fixed_date`, `standard`, `deferred`.
- `execution_sequence.rank`: `null` only for `draft`/`blocked`; non-negative integer is mandatory for `ready`.

## Guidance, not automatic mapping

| Nomia business priority | Suggested Mago lane | Rule |
|---|---|---|
| `unknown` | none | Handoff cannot be declared ready when business priority is required but unresolved. |
| `low` | `deferred` | Mago may choose another lane with rationale. |
| `medium` | `standard` | Default planning suggestion only. |
| `high` | `standard` or `fixed_date` | Deadline and dependency evidence decide. |
| `urgent` | `expedite` or `fixed_date` | Urgency never bypasses dependencies, safety, validation, or rollback. |

Mago records the chosen `execution_sequence.rationale`. Dependency topology and safety constraints remain authoritative.

## Provenance and write rules

- Nomia writes `business_priority` with `owner: nomia`, source, observation time, and rationale when known.
- Mago preserves `business_priority` as read-only attributed evidence and writes `technical_criticality` plus `execution_sequence` with `owner: mago`.
- A non-`unknown` `business_priority` without Nomia source and observation time is invalid at every handoff.
- Magia consumes the three fields, reports blockers or deviations, and never rewrites governance or planning values.

## Breaking removal of generic fields

- Every package must reject the generic fields `priority` and `order_hint`; they must never be treated as aliases, migration inputs, projection keys, or accepted runtime fields.
- Every package rejects records containing either generic field, including records that also contain canonical fields.
- Migration must be explicit and external: the source owner must produce the appropriate canonical field before the record enters Nomia, Mago, or Magia validation.
- No implicit mapping is allowed because the old Mago enum mixed technical criticality and execution ordering, while Nomia priority represents business governance.
