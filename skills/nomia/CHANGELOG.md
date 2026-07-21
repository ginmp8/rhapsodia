# Changelog

## 2.3.0 - 2026-07-21

- Add guided intake and progressive product-discovery facilitation that preserves unknowns, prioritizes blocking questions, and never writes canonical governance records.
- Add lifecycle, decision-ready, and audience-specific non-authoritative projections with explicit authority, evidence health, next action, and next responsible skill.
- Add actionable typed-handoff diagnostics while preserving rejection, freshness, conflict, provenance, and cross-skill authority gates.
- Fix atomic `--json-output` handling in `evaluate_governance.py` and add regression coverage for the new guided and projection flows.
- Preserve the exact bytes of protected `agents/openai.yaml` and `assets/icon.svg`.

## 2.2.0 - 2026-07-21

- Preserve the immutable historical contract while adding a separate current-release contract and an explicit protected-icon hash migration record.
- Add fail-closed release, documentation, and machine-readable assurance gates with SDD G1-G8 coverage.
- Add regression tests for missing migrations, tampered protected files, version drift, root-escaping links, unsupported assurance claims, and archive metadata drift.
- Add deterministic archive attestation and prove repeated builds are byte-identical.
- Keep validation and packaging read-only with respect to source bytecode caches.
- Keep the selected `assets/icon.svg` and `agents/openai.yaml` bytes unchanged.

## 2.1.0 - 2026-07-21

- Fail closed when package input contains symlinks, environment/credential files, private-key containers, or private-key material; validate the completed archive before release.
- Make RFC, governance-decision, structured-list, normalization, adaptation-report, and validation-report writes atomic through the shared same-directory replacement helper.
- Add adversarial package-security and writer-interruption regression tests.
- Reconcile the protected Nomia icon contract with the installed 2.0.1 baseline while retaining exact-byte preservation.
- Clarify canonical schema-version-2 authoring versus schema-version-1 legacy validation/adaptation.

## 2.0.1 - 2026-07-20

- Ensure all direct adapter results are JSON-safe when YAML parsing produces `date` or `datetime` values.
- Add regression coverage for all eight public adapter mappings.

## 2.0.0 - 2026-07-20

- Integrated governance profiles, lifecycle stages, canonical schema-version-2 records, typed technical states, and deterministic projection metadata into the primary workflow.
- Hardened handoff identity, provenance, freshness, and authority validation.
- Added read-only legacy governance adaptation with current externally supplied identities.
- Added a reproducible validation ledger, governance-scenario package gate, deterministic golden dates, warning allowlists, atomic writes, and atomic packaging.
- Preserved original artifact families, public script surface, protected assets, and Nomia/Mago/Magia authority boundaries.
