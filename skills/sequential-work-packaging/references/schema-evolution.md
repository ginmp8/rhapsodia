# Schema evolution contract

The canonical artifact schema is versioned independently from planning identities. `schema_version` describes the wire/document contract, not the feature being planned.

## Current version

The current canonical catalog and manifest schema is `1`. Writers emit only version `1` unless a future migration explicitly changes this contract.

Readers must fail closed on an unsupported major schema. In particular, a manifest whose `schema_version` is not `1` is not interpreted as compatible merely because its other fields look familiar.

## Compatibility policy

Use these rules for future schema evolution:

- **same major, additive change**: new optional fields or new diagnostics may be introduced only when older readers can safely ignore them and meaning of existing fields does not change;
- **breaking semantic change**: removing or renaming a required field, changing field meaning, changing canonical identity syntax, or changing an invariant requires a new schema major plus an explicit migration path;
- **reader behavior**: unknown schema majors block with a stable diagnostic rather than being guessed;
- **writer behavior**: one run emits one declared canonical schema; it must not mix incompatible versions in the same artifact;
- **migration behavior**: migrations are explicit, deterministic, non-destructive by default, preserve source bytes, and emit old -> new identity/evidence in the change receipt.

A format change from the current `feature_version` token (`vMAJOR.MINOR.PATCH`) to strict SemVer text (`MAJOR.MINOR.PATCH`) is a schema-breaking serialization change and must not be performed silently inside schema version 1.

## Version semantics

`cycle_version` and `feature_version` are separate concepts:

- `cycle_version` is a fixed-width SWP planning-cycle identifier in `NN.NN.NN` form. It is intentionally **not** a SemVer token because leading zeros are part of its canonical format.
- `feature_version` in schema version 1 is an SWP version token: `vMAJOR.MINOR.PATCH`. Its numeric triple follows the project's SemVer-derived bump policy after the change is semantically classified, but the leading `v` means the serialized token itself is not strict SemVer 2.0.0 text.

Do not claim that either identifier is strict Semantic Versioning unless its serialization and semantics actually satisfy the SemVer specification.

## Machine-readable surfaces

Version public machine-readable contracts independently when they can evolve separately:

- catalog / manifest `schema_version`;
- operation `plan_version`;
- validation `report_version`;
- receipt `receipt_version`;
- semantic transaction identity `transaction_identity_version`.

A consumer must use the version of the surface it is interpreting rather than inferring compatibility from nearby fields.
