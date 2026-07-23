# Ecosystem Handoff Contract v2

Use this contract whenever Nomia, Mago, or Magia transfers governed facts, planning intent, execution instructions, implementation evidence, or delivery-impact evidence to another ecosystem skill. The machine-readable source is [ecosystem-handoff-contract.json](ecosystem-handoff-contract.json); coordinated package compatibility is defined by [ecosystem-compatibility.json](ecosystem-compatibility.json).

## Contract boundary

Each package carries its own byte-equivalent copy of `references/ecosystem-handoff-contract.json` and its own local `scripts/ecosystem_handoff.py`. No skill imports, executes, or reads another skill package at runtime. Coordinated release validation compares the local contract files and rejects drift.

A typed envelope transfers attributed evidence; it never transfers authority. The producer owns only its source facts. The consumer validates the envelope before using it and preserves the source skill, source version, provenance, observation time, freshness, unknowns, conflicts, and mapping version.

Payload properties are closed by direction: required, typed, and explicitly optional fields are allowed; undeclared fields are rejected.

## Release contract

- Ecosystem release: `1.8.0`.
- Handoff schema: `2.0.0`.
- State mapping: `2.0.0`.
- Compatibility: exact coordinated versions only.
- Legacy aliases and envelopes are rejected; adaptation must occur before a handoff is built.

## Directions

| Direction | Producer | Consumer | Meaning and boundary |
|---|---|---|---|
| `nomia_to_mago` | Nomia | Mago | Governance outcome, scope, owner, attributed business priority, dependencies, and readiness; no technical design or tasks. |
| `mago_to_magia` | Mago | Magia | Requirements, acceptance criteria, tasks, validation references, technical criticality, and execution sequence; no governance replacement or runtime completion claim. |
| `magia_to_mago` | Magia | Mago | Execution findings, deviations, validation state, and evidence requiring reconciliation; no silent planning rewrite. |
| `mago_to_nomia` | Mago | Nomia | Planning state and delivery-impact projections with explicit state mapping; no governance decision. |
| `magia_to_nomia` | Magia | Nomia | Execution and validation evidence with explicit state mapping; no closure, business-risk acceptance, or release communication decision. |

`nomia_to_stakeholder` remains a Nomia-owned projection direction and does not grant stakeholder communication authority to Mago or Magia.

## Required envelope and evidence integrity

Current writers emit `schema_version`, `ecosystem_release`, `direction`, `source_skill`, `source_version`, `target_skill`, `observed_at`, `provenance`, `freshness`, `payload`, `unknowns`, `conflicts`, and deterministic `handoff_id`. `provenance.evidence_refs` contains at least one non-empty reference. `freshness.max_age_days` cannot exceed the machine-readable contract maximum. Timestamps beyond the allowed clock skew are rejected rather than treated as fresh.

A stale, future-dated, conflicting, malformed, wrong-role, wrong-version, tampered-id, mixed-version, undeclared-payload, or authority-violating envelope fails closed. There is no runtime compatibility switch for pre-v2 envelopes. Stable `reason_codes` accompany human-readable rejection reasons.

## Draft and CLI exit semantics

A `draft` envelope may be structurally valid and transported, but it is not actionable. `build` may create a draft. `validate --operation consume` succeeds only for `accepted` by default. Use `--allow-draft` only for explicit inspection or transport; it must not authorize mutation.

| Status | Default exit code | With `--allow-draft` |
|---|---:|---:|
| `accepted` | 0 | 0 |
| `error` | 2 | 2 |
| `draft` | 3 | 0 |
| `stale` | 4 | 4 |
| `conflicting` | 5 | 5 |
| `rejected` | 6 | 6 |

## State projections

Source states remain authoritative in their source dimensions. Projections sent to Nomia use mapping version `2.0.0`: Mago planning `done` maps to planning `complete`; Magia execution `done` maps to execution `complete`; Magia validation `passed` remains validation `passed`. Mappings never let Nomia certify technical truth.

Mappings do not let Nomia certify planning, execution, or validation. A projected state without source evidence, mapping version, or current provenance is rejected.

## Commands

```text
python -B scripts/ecosystem_handoff.py contract
python -B scripts/ecosystem_handoff.py build --direction <direction> --payload <payload.json> --source <artifact-or-record> --authority <authority> --evidence-ref <ref> --freshness-days 30 --output <handoff.json>
python -B scripts/ecosystem_handoff.py validate --input <handoff.json> --operation consume --json-output <validation.json>
python -B scripts/ecosystem_handoff.py validate --input <draft.json> --operation consume --allow-draft --json-output <inspection.json>
python -B scripts/validate_ecosystem_handoff_contract.py --target <skill-root>
python -B scripts/validate_ecosystem_compatibility.py --target <skill-root> --peer-root <peer-root> --peer-root <peer-root>
```

## Release gate

A coordinated release proves byte-equivalent shared contracts, producer/consumer acceptance, exact status and reason-code negative cases, package-local validation, positive lifecycle flow, fail-closed closure, and strict ecosystem change-gate review.
