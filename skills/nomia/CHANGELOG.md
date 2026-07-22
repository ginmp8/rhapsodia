# Changelog

## [1.7.0] - 2026-07-22

- Replace retired cycle-version vocabulary in current activation scenarios with canonical `cycle_id` terminology.
- Add distributed routing, lifecycle, shared provenance, negative ecosystem harness, coordinated release metadata, and declared development requirements.
- Standardize the display name as `Nomia` while preserving the technical id `nomia`.
- Preserve Nomia governance ownership and coordinated exact compatibility with Mago and Magia `1.7.0`.

### Compatibility

- Coordinated exact ecosystem release `1.7.0`; mixed versions remain rejected before mutation or closure.


## 1.6.0 - 2026-07-22

- Maintenance correction: align handoff prose with the strict breaking-no-legacy contract; legacy governance input remains isolated to `governance-adapt` and is never accepted as ecosystem handoff compatibility.
- Maintenance correction: add a contract-semantic gate to package, ledger, unit-test, and packaging assurance.

- Adopt exact ecosystem compatibility with Mago and Magia `1.6.0`.
- Upgrade ecosystem handoffs to strict schema v2 with deterministic ids, exact package versions, no unsupported aliases, and explicit state projections.
- Make `business_priority` the only governance priority field; reject generic priority aliases.
- Add a Nomia-owned closure gate that requires an explicit governance decision and external release evidence after technical completion.
- Add the integrated Nomia-to-Mago-to-Magia reconciliation and closure harness.
- Preserve fail-closed package security, atomic governance writes, canonical schema v2, documentation validation, and machine-readable assurance gates.
- Keep validation and packaging read-only with respect to source caches; reject symlinks, credential files, private-key material, and unsafe archive paths.
