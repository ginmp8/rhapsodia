# SDD Interoperability and Planning Reconciliation

Use this reference for Spec Kit, Kiro, or OpenSpec import/export and for read-only comparison of Mago intent with Magia execution evidence. All adapters and reconciliation outputs are generated, non-authoritative reports.

## Canonical authority

- Mago registry and canonical package artifacts remain the source of truth for intended technical planning.
- Imported public-format files are evidence inputs until validated and normalized through a Mago planning mode.
- Exported files are compatibility projections, not write targets for Mago, Nomia, or Magia.
- Magia evidence remains Magia-owned and read-only. Reconciliation never rewrites it and never turns it into runtime proof authored by Mago.

## Public format mappings

| Public format | Import into Mago | Export from Mago | Required loss checks |
|---|---|---|---|
| GitHub Spec Kit | `spec.md` -> PRD requirements and acceptance; `plan.md` -> technical design, constraints, decisions; `tasks.md` -> canonical tasks; constitution/policy -> referenced constraints only | PRD -> spec; technical design/decisions -> plan; tasks -> tasks | board/cycle/spec identity, registry state, rigor profile, evidence provenance, governed traceability, Nomia/Magia authority, conditional artifacts, validation status |
| Kiro Specs | requirements -> PRD requirements/acceptance; design -> technical design/decisions; tasks -> canonical tasks; Quick Plan -> candidate `quick` profile subject to Mago escalation | PRD -> requirements; technical design -> design; tasks -> tasks | profile escalation, registry identity, evidence labels, optional artifact triggers, explicit change history, reconciliation state |
| OpenSpec | proposal -> context/goals; design -> technical design; tasks -> tasks; ADDED/MODIFIED/REMOVED requirements -> Mago change-delta and canonical requirement updates | change delta -> proposal/spec delta; technical design -> design; tasks -> tasks | preserved behavior, compatibility, migration, rollback, board identity, governed traceability, authority boundaries, fields not representable by the selected OpenSpec schema |

C4, OpenAPI, and AsyncAPI are technical evidence/export formats, not replacement SDD package authorities. Use C4 views only at the useful abstraction levels; reference or generate OpenAPI for HTTP API contracts and AsyncAPI for message-driven contracts when triggered. Record unsupported semantics and version assumptions in the adapter loss report.


## Executable bounded adapters

`scripts/sdd_adapter.py` implements version-explicit file-convention adapters for `spec-kit` and `openspec`. It exports canonical PRD/design/tasks and optional delta files, writes checksums and a non-authoritative metadata sidecar, imports mapped files into an external Mago projection, and performs strict round-trip SHA-256 comparison. Run `scripts/validate_sdd_adapter_report.py` on every report.

The adapters are deliberately bounded: they map the documented file surfaces and do not claim compatibility with an unspecified, `latest`, or complete external tool schema. Board identity, authority, evidence provenance, profile decisions, mutation state, and reconciliation remain Mago concepts and are disclosed as sidecar-only losses. Native external edits are detected and reported on import rather than silently treated as unchanged Mago intent.

## Import contract

1. Identify source format and version from supplied evidence; never guess a volatile schema version.
2. Validate required source files and internal references before normalization.
3. Produce a mapping and loss report outside `BOARD_ROOT`.
4. Resolve or preserve unknown Mago identities, governance facts, evidence provenance, and profile triggers.
5. Normalize into canonical Mago artifacts through exactly one internal primary mode.
6. Run Mago identity, package, boundary, traceability, and triggered artifact gates.

## Export and round-trip contract

Every export includes a machine-readable report with:

- `authoritative: false`
- source Mago spec/version and target format/version
- generated files and checksums when practical
- mapped fields
- omitted fields
- lossy mappings with severity and rationale
- unsupported target concepts
- source-only Mago concepts
- round-trip comparison status
- validator commands and outcomes

A round trip passes only when every semantic difference is either lossless or explicitly reported. The adapter report validator checks disclosure completeness, not semantic equivalence by itself. Use `assets/templates/sdd-adapter-report.json.template` for the generated non-authoritative report and validate it with `scripts/validate_sdd_adapter_report.py`.

## Read-only reconciliation mode

Normalize selected Mago plan facts and supplied Magia evidence into external evidence envelopes, then classify:

- **implemented as planned**
- **implementation deviation**
- **unmet acceptance criteria**
- **obsolete planned task**
- **newly discovered work**
- **required planning revision**
- **no-change convergence**

`no-change convergence` means the supplied evidence introduces no planning deviation; it does not add runtime proof beyond the cited Magia evidence.

Reconciliation workflow:

1. Resolve the canonical Mago package and evidence provenance.
2. Read Magia implementation notes, validation evidence, technical gap notes, contract notes, and implementation ADRs without mutation.
3. Compare stable requirement, acceptance, decision, task, and validation IDs where available.
4. Report every classification with source references and evidence status (`pass`, `fail`, `blocked`, `not_run`, or `unknown`).
5. Recommend a Mago planning revision only when canonical intent must change; never perform that revision inside the read-only reconciliation step.
6. Hand governance/status consequences to Nomia and implementation follow-up to Magia.

Use `assets/templates/planning-reconciliation.md.template`; `scripts/reconcile_planning.py` can validate normalized JSON envelopes and produce a non-authoritative result outside the package.
