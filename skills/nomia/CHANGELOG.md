# Changelog

The version line was normalized with Mago and Magia. Historical Nomia releases `2.0.0` through `3.1.0` are grouped below without removing capabilities.

## 1.6.0 - 2026-07-22

- Adopt exact ecosystem compatibility with Mago and Magia `1.6.0`.
- Upgrade ecosystem handoffs to strict schema v2 with deterministic ids, exact package versions, no legacy aliases, and explicit state projections.
- Add a Nomia-owned closure gate that requires an explicit governance decision and external release evidence after technical completion.
- Add the integrated Nomia-to-Mago-to-Magia reconciliation and closure harness.

## 1.5.0 - 2026-07-22

- Make `business_priority` the only governance priority field and remove generic priority aliases.
- Add mechanically validated ecosystem handoffs with provenance, freshness, conflicts, unknowns, and mapping metadata.

## 1.4.0 - 2026-07-21

- Add guided intake, lifecycle projections, typed diagnostics, reproducible release contracts, assurance gates, and deterministic archive attestation.

## 1.3.0 - 2026-07-21

- Add fail-closed package security, atomic governance writers, canonical schema v2 records, and hardened state/evidence contracts.

## 1.2.0 - 2026-07-20

- Add JSON-safe adapters, governance profiles, lifecycle stages, technical-state projections, deterministic golden scenarios, and atomic packaging.

## 1.1.0 - 2026-07-20

- Establish governance intake, ownership, roadmap, portfolio, decisions, reporting, release communication, and roadmap-to-Mago handoffs.

## Preserved pre-normalization controls

These lines record historical behavior and safety gates. The deprecated alias described in the first line was removed by `1.6.0` and is not an active read path.

- Make `business_priority` the canonical Nomia ops field while retaining deprecated `priority` as a read-only migration alias.
- Add fail-closed release, documentation, and machine-readable assurance gates with SDD G1-G8 coverage.
- Keep validation and packaging read-only with respect to source bytecode caches.
- Fail closed when package input contains symlinks, environment/credential files, private-key containers, or private-key material; validate the completed archive before release.
