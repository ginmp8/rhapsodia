# Changelog

## [3.1.0] - 2026-07-22

### Added
- Add a byte-equivalent ecosystem handoff contract, local producer/consumer CLI, explicit state projections, and regression coverage for Nomia, Mago, and Magia transfers.
- Add mechanical `nomia_to_mago`, `mago_to_magia`, `magia_to_mago`, `mago_to_nomia`, and `magia_to_nomia` envelope validation without runtime imports between skills.

### Compatibility
- Existing planning artifacts remain unchanged. Legacy Nomia handoff envelopes remain readable during migration, while new Mago writers emit contract v1.
- The change is additive and preserves Mago ownership, canonical identity, priority, planning, mutation, and evidence boundaries.

## [3.0.0] - 2026-07-22

### Breaking
- Remove all runtime, projection, and migration support for generic `priority` and `order_hint`.
- Require `business_priority`, `technical_criticality`, and `execution_sequence` on every active registry record.
- Replace generated catalog `order_hint` with explicit business-priority, technical-criticality, execution-lane, and execution-rank fields.
- Reject generic priority records rather than interpreting or converting them.

## [2.6.0] - 2026-07-21

- Replace new generic registry `priority`/`order_hint` writes with explicit `business_priority`, `technical_criticality`, and `execution_sequence` contracts.
- Add a versioned ecosystem priority contract, provenance rules, migration compatibility, deterministic validators, and regression tests.
- Preserve legacy Mago registry records as read-only migration inputs while rejecting mixed canonical and legacy forms.

All notable package changes are recorded here. Versions follow semantic versioning for the distributed skill package only; cycle and spec filesystem identities never use semantic versioning.

## [2.5.0] - 2026-07-21

### Added

- Progressive getting-started guidance that routes new users through Nomia, Mago, and Magia boundaries without creating a second lifecycle.
- A non-authoritative planning compass renderer for package identity, artifact completeness, mutation state, mechanically observed gates, and the next safe Mago action.
- A deterministic execution-wave renderer that rejects unknown dependencies and cycles while preserving Magia responsibility for file, contract, environment, and runtime overlap checks.
- Clarification prioritization, brownfield discovery summaries, and a version-explicit adapter development contract.
- `scripts/validate_planning_experience.py` as an additive integration gate for the new onboarding and projection resources.

### Compatibility

- Canonical identity, registry, package, traceability, profile, mutation, adapter, Nomia, and Magia authority contracts are unchanged.
- Planning compass and execution-wave outputs are disposable external projections and never become canonical planning or runtime evidence.

## [2.4.0] - 2026-07-21

### Added

- Bounded aggregate test and evidence runners with sequential-safe defaults, whole-run deadlines, atomic progress checkpoints, signal-aware process-group termination, and truthful partial failure reports.
- A separate deterministic lifecycle evidence suite covering quick, standard, governed, handoff, concurrency, recovery, security, interoperability, release, and dependency contracts without changing the frozen activation oracle.
- `scripts/validate_distribution.py` as a single external distribution gate that composes dependencies, release metadata, activation, the complete test suite, core and lifecycle evidence, package validation, archive validation, byte-equivalent extraction, and extracted-package revalidation.
- An explicit Markdown output contract and direct progressive-loading links for activation, roadmap intake, RFC quality, handoff, validation, and release guidance.

### Changed

- Deterministic mechanism scenarios moved from `evals/` to `evidence/` so activation schema tooling cannot misclassify executable evidence as prompt-routing cases; scenario bytes remain unchanged.
- Import-only helpers now fail clearly when invoked as CLIs instead of appearing to succeed silently.

### Compatibility

- Canonical board, registry, package, requirement, task, validation, security, adapter, and ownership contracts are unchanged.
- The new distribution and lifecycle gates are additive. Existing 2.3 planning packages remain readable and require no artifact migration.

## [2.3.0] - 2026-07-21

### Added

- Clarification readiness v2 with stable assumption, blocker, and question records plus deterministic handoff blocking.

- Explicit `requirements.txt` and machine-validated runtime dependency metadata with actionable installation diagnostics.
- Executable, explicit-version Kiro requirements/design/tasks adapter with checksum round trips and external-edit disclosure.
- Isolated parallel test and evidence-harness execution with per-file/scenario timeouts, exact counts, ordered results, and duration metrics.
- Governed plan-quality contract v2 with requirement criticality, risk-calibrated acceptance paths, complete AC-to-validation coverage, evidence capture, residual-risk disposition, and rollback/reversibility fields.

### Compatibility

- Existing Mago planning artifacts and plan-quality v1 packages remain readable; new governed handoffs migrate to quality contract v2. The distributed skill now requires installation of the declared PyYAML runtime range before deterministic validators run.

## [2.1.0] - 2026-07-20

### Added

- Executable multi-artifact transactions with staging, drift detection, interruption resume, injected-failure testing, and verified rollback.
- Version 2 relational security/risk contract linking assets, boundaries, threats, abuse cases, controls, residual risks, validation evidence, and external review authority.
- Governed plan-quality validation for requirement evidence, failure/recovery behavior, acceptance-path diversity, design alternatives, measurable NFRs, and reproducible validation procedures.
- Version-explicit Spec Kit and OpenSpec file-convention adapters with metadata, checksums, loss disclosure, external-edit detection, and round-trip comparison.
- Release metadata, compatibility policy, and distribution validation.

### Compatibility

- Existing version 1 security artifacts remain readable for legacy compatibility; new governed security work requires contract version 2 before handoff.
- Existing canonical board, registry, package, requirement, task, validation, and execution-evidence ownership contracts remain unchanged.
- External adapters are bounded file-convention mappings and do not claim complete compatibility with unspecified external schema versions.
