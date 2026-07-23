# Ecosystem Handoff Contract v3

Use this contract whenever Nomia, Mago, or Magia transfers governed facts, planning intent, execution instructions, implementation evidence, or delivery-impact evidence. The machine-readable source is [ecosystem-handoff-contract.json](ecosystem-handoff-contract.json).

## Boundary

Each package carries byte-equivalent local copies of the contract and builder. Packages remain runtime-independent and never import peer internals. A handoff transfers attributed evidence, not authority. Payloads are closed per direction and undeclared fields fail closed.

## Release

- Ecosystem release: `1.9.0`.
- Handoff schema: `3.0.0`.
- State mapping: `2.0.0`.
- Compatibility: exact coordinated versions only; v2 envelopes are rejected on the normal path.
- Legacy aliases and envelopes are rejected; adaptation must occur before a handoff is built. There is no runtime compatibility switch for pre-v3 envelopes.

## Envelope invariants

Current envelopes require identity, direction, producer/consumer versions, provenance, freshness, payload, unknowns, conflicts, deterministic `handoff_id`, stable `workflow_id`, and `privacy_handling`. Follow-up envelopes reuse `workflow_id` and set `causation_id` to the prior handoff.

`privacy_handling` records classification, audience, allowed destinations, purpose, retention, data categories, redactions, evidence-reference visibility, and external-share policy. Secrets are never transported. Public handoffs cannot contain personal, third-party, or confidential data. Evidence references are opaque by default and must reference evidence rather than embed raw logs or private URLs.

## Directions

| Direction | Producer | Consumer | Boundary |
|---|---|---|---|
| `nomia_to_mago` | Nomia | Mago | Governance facts and readiness; no technical design or tasks. |
| `mago_to_magia` | Mago | Magia | Validated intent and execution plan; no governance replacement or runtime completion claim. |
| `magia_to_mago` | Magia | Mago | Execution evidence and deviations; no silent planning rewrite. |
| `mago_to_nomia` | Mago | Nomia | Attributed planning projection; no governance decision. |
| `magia_to_nomia` | Magia | Nomia | Attributed execution/validation projection; no closure or risk acceptance. |

## Failure semantics

Malformed, stale, future-dated, conflicting, wrong-role, mixed-version, lineage-invalid, privacy-invalid, tampered, undeclared, or authority-violating envelopes fail closed with stable reason codes. A draft is transportable but non-actionable unless `--allow-draft` is used for inspection only.

## Commands

```text
python -B scripts/ecosystem_handoff.py workflow-id --seed <non-sensitive-seed>
python -B scripts/ecosystem_handoff.py contract
python -B scripts/ecosystem_handoff.py build --direction <direction> --payload <payload.json> --privacy <privacy.json> --workflow-id <workflow-id> --source <artifact> --authority <authority> --evidence-ref <opaque-ref> --output <handoff.json>
python -B scripts/ecosystem_handoff.py validate --input <handoff.json> --operation consume --json-output <validation.json>
```

The shared handoff ledger records lifecycle state (`created`, `accepted`, `consumed`, `superseded`, `replayed`) without changing domain authority.
