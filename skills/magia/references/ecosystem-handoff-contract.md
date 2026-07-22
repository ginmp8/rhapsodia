# Ecosystem Handoff Contract

Use this contract whenever Nomia, Mago, or Magia transfers governed facts, planning intent, execution instructions, implementation evidence, or delivery-impact evidence to another ecosystem skill.

## Contract boundary

Each package carries its own byte-equivalent copy of `references/ecosystem-handoff-contract.json` and its own local `scripts/ecosystem_handoff.py`. No skill imports, executes, or reads another skill package at runtime. Coordinated release validation compares the local contract files and rejects drift.

A typed envelope transfers attributed evidence; it never transfers authority. The producer owns only its source facts. The consumer validates the envelope before using it and preserves the source skill, source version, provenance, observation time, freshness, unknowns, conflicts, and mapping version.

## Directions

| Direction | Producer | Consumer | Meaning |
|---|---|---|---|
| `nomia_to_mago` | Nomia | Mago | Governance outcome, scope, owner, business priority, dependencies, and readiness. |
| `mago_to_magia` | Mago | Magia | Requirements, acceptance criteria, tasks, validation references, technical criticality, and execution sequence. |
| `magia_to_mago` | Magia | Mago | Execution findings, deviations, validation state, and evidence requiring reconciliation. |
| `mago_to_nomia` | Mago | Nomia | Planning state and delivery-impact projections with explicit state mapping. |
| `magia_to_nomia` | Magia | Nomia | Execution and validation evidence with explicit state mapping. |

`nomia_to_stakeholder` remains a Nomia-owned projection direction and does not grant stakeholder communication authority to Mago or Magia.

## Required envelope

New writers emit:

```json
{
  "schema_version": "1.0.0",
  "direction": "mago_to_magia",
  "source_skill": "mago",
  "source_version": "3.1.0",
  "target_skill": "magia",
  "observed_at": "2026-07-22T12:00:00+00:00",
  "provenance": {
    "source": "docs/boards/example/2026/cycles/cycle-2026-07-22-demo/specs/spec-2026-07-22-demo/manifest.yaml",
    "authority": "mago",
    "evidence_refs": ["tasks.md", "validation.md"]
  },
  "freshness": {"max_age_days": 30},
  "payload": {},
  "unknowns": [],
  "conflicts": []
}
```

Legacy Nomia envelopes may be read during migration, but new producers must emit contract v1. Legacy acceptance is compatibility evidence, not permission to keep producing the old shape.

## State projections

Source states remain authoritative in their source dimensions. Projections sent to Nomia use mapping version `1.0.0`:

- Mago planning `done` projects to Nomia planning `complete`.
- Magia execution `done` projects to Nomia execution `complete`.
- Magia validation `passed` projects to Nomia validation `passed`.

Mappings do not let Nomia certify planning, execution, or validation. A projected state without source evidence, mapping version, or current provenance is rejected.

## Commands

Build an envelope with the current package as producer:

```text
python scripts/ecosystem_handoff.py build --direction <direction> --payload <payload.json> --source <artifact-or-record> --authority <authority> --evidence-ref <ref> --freshness-days 30 --output <handoff.json>
```

Validate an envelope as the current package consumer:

```text
python scripts/ecosystem_handoff.py validate --input <handoff.json> --operation consume --json-output <validation.json>
```

Validate the local contract and role declaration:

```text
python scripts/validate_ecosystem_handoff_contract.py --target <skill-root>
```

## Release gate

A coordinated Mago/Magia/Nomia release must prove:

1. the three local JSON contracts are byte-equivalent;
2. every producer output is accepted by the declared consumer;
3. positive, missing-field, stale, conflict, forbidden-content, wrong-producer, and state-mapping scenarios pass;
4. package-local validators pass;
5. the SDD Ecosystem Change Gate accepts every changed package under strict policy.
