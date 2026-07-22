# Changelog

## 1.6.0 - 2026-07-22

- Adopt exact ecosystem compatibility with Mago and Magia `1.6.0`.
- Upgrade ecosystem handoffs to strict schema v2 with deterministic ids, exact package versions, no unsupported aliases, and explicit state projections.
- Make `business_priority` the only governance priority field; reject generic priority aliases.
- Add a Nomia-owned closure gate that requires an explicit governance decision and external release evidence after technical completion.
- Add the integrated Nomia-to-Mago-to-Magia reconciliation and closure harness.
- Preserve fail-closed package security, atomic governance writes, canonical schema v2, documentation validation, and machine-readable assurance gates.
- Keep validation and packaging read-only with respect to source caches; reject symlinks, credential files, private-key material, and unsafe archive paths.
