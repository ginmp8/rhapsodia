# Changelog

All notable package changes are recorded here. Versions follow semantic versioning for the distributed skill package only; cycle and spec filesystem identities never use semantic versioning.

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
