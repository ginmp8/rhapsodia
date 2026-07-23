# Changelog

## [1.8.0] - 2026-07-23

- Harden strict handoff v2 consumption with closed direction payloads, bounded freshness, future-timestamp rejection, non-empty evidence references, stable reason codes, and non-actionable draft exit semantics.
- Add exact fail-closed harness assertions and a coordinated three-package release ledger bound to candidate roots, hashes, suites, archives, and ecosystem gates.
- Add an external live-routing evidence contract and immutable result schema while preserving structural-versus-measured evidence separation.
- Preserve Nomia governance ownership, closure authority, protected-file history, current identifiers, and migration-only governance adaptation.

### Compatibility

- Coordinated exact ecosystem release `1.8.0`; all three packages must move together.
- Handoff schema remains `2.0.0`; draft consumption now fails process control by default and requires explicit inspection allowance.

## [1.7.0] - 2026-07-22
- Repair protected `agents/openai.yaml` release continuity with an explicit two-step, user-authorized migration chain while keeping the immutable historical contract unchanged.
- Group correlated validation failures under deterministic root-cause identifiers while preserving every individual gate result.
- Clarify independent one-owner context loading and coordinated three-package rollback without transferring governance authority.

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
