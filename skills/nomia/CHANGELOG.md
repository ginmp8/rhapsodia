# Changelog

## 3.1.0 - 2026-07-22

- Add a versioned ecosystem handoff contract with local producer and consumer validation for Nomia, Mago, and Magia.
- Make `nomia_to_mago`, `mago_to_nomia`, and `magia_to_nomia` mechanically validated with source package version, provenance, freshness, unknowns, conflicts, evidence references, target role, and state-mapping metadata.
- Preserve runtime independence by carrying byte-equivalent contract and validator files in each package rather than importing peer skills.
- Retain explicit legacy-envelope compatibility only for reads while requiring all new writers to emit contract v1.

## 3.0.0 - 2026-07-22

### Breaking
- Remove the generic `priority` alias from ops records, governance adaptation, projections, portfolio items, validators, examples, and writers.
- Require Nomia-owned `business_priority` everywhere governance priority is represented.
- Reject source records that use generic `priority`; no implicit adaptation or enum conversion is performed.
- Rename executive and portfolio projection fields to `business_priority`.
- Adopt ecosystem priority contract v2 with no legacy read surface.

## 2.4.0 - 2026-07-21

- Make `business_priority` the canonical Nomia ops field while retaining deprecated `priority` as a read-only migration alias.
- Publish the shared ecosystem priority contract and explicit handoff semantics for Mago technical criticality and execution sequence.
- Add deterministic priority-contract validation, canonical/legacy conflict rejection, projection fallback, and migration tests.

## 2.3.0 - 2026-07-21

- Add guided intake and progressive product-discovery facilitation that preserves unknowns, prioritizes blocking questions, and never writes canonical governance records.
- Add lifecycle, decision-ready, and audience-specific non-authoritative projections with explicit authority, evidence health, next action, and next responsible skill.
- Add actionable typed-handoff diagnostics while preserving rejection, freshness, conflict, provenance, and cross-skill authority gates.
- Fix atomic `--json-output` handling in `evaluate_governance.py` and add regression coverage for the new guided and projection flows.
- Preserve the exact bytes of protected `agents/openai.yaml`.

## 2.2.0 - 2026-07-21

- Preserve the immutable historical contract while adding a separate current-release contract and explicit protected-file migration records.
- Add fail-closed release, documentation, and machine-readable assurance gates with SDD G1-G8 coverage.
- Add regression tests for missing migrations, tampered protected files, version drift, root-escaping links, unsupported assurance claims, and archive metadata drift.
- Add deterministic archive attestation and prove repeated builds are byte-identical.
- Keep validation and packaging read-only with respect to source bytecode caches.
- Keep the selected `agents/openai.yaml` bytes unchanged.

## 2.1.0 - 2026-07-21

- Fail closed when package input contains symlinks, environment/credential files, private-key containers, or private-key material; validate the completed archive before release.
- Make RFC, governance-decision, structured-list, normalization, adaptation-report, and validation-report writes atomic through the shared same-directory replacement helper.
- Add adversarial package-security and writer-interruption regression tests.
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
