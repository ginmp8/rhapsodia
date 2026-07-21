# Changelog

## 2.0.1 - 2026-07-20

- Ensure all direct adapter results are JSON-safe when YAML parsing produces `date` or `datetime` values.
- Add regression coverage for all eight public adapter mappings.

## 2.0.0 - 2026-07-20

- Integrated governance profiles, lifecycle stages, canonical schema-version-2 records, typed technical states, and deterministic projection metadata into the primary workflow.
- Hardened handoff identity, provenance, freshness, and authority validation.
- Added read-only legacy governance adaptation with current externally supplied identities.
- Added a reproducible validation ledger, governance-scenario package gate, deterministic golden dates, warning allowlists, atomic writes, and atomic packaging.
- Preserved original artifact families, public script surface, protected assets, and Nomia/Mago/Magia authority boundaries.
