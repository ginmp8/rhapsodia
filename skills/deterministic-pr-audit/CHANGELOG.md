# Changelog

## [0.2.0] - 2026-11-14

### Changed

- Preserve the RhapsodIA 0.18.0 release integration, repository CLI wrapper, and portable `gh` command validation.
- Bump the independent skill version from 0.1.0 to 0.2.0 for non-comparable scoring changes.

### Fixed

- No checkout and no executed checks now yields `NOT_ASSESSED` and `null` evidence floor, never an apparent `0% implemented`.
- Incomplete check plans and partial runtime-only/static probes cannot produce a numerical progress headline.
- A mandatory `preflight` command rejects empty/incomplete verification contracts and missing exact-SHA evidence; `--allow-partial` is explicitly diagnostic only.
- Parent REQ and observable AC groups are reported separately to prevent inflated 14+40 progress denominators.
- Old unassessed/legacy reports cannot be silently compared as equally complete.
- Offline `--from-json` captures are marked completeness-unverified instead of claiming full issue coverage.
- Instructions require a bounded read-only Git acquisition attempt and a GitHub source/CI qualitative fallback if no checkout is available.
- Self-reported issue evidence ledgers, CI-green status and matrix-dispatch-only tests cannot stand in for per-requirement terminal proof.

### Compatibility

- Input and evidence schema names remain v1; algorithm identity changes to `score-v1.1.0`.
- Earlier reports must be regenerated under the new algorithm before comparisons.
- No network writes or repository test execution were added.

### Validation

- 23 offline automated tests passed, including real Git-object replay and a synthetic 14-REQ/40-AC regression.
- PR #152's sparse offline evidence was re-scored to `NOT ASSESSED` / N/A, with byte-identical replay.

## [0.1.0] - 2026-11-14

### Added
- Initial SHA-pinned GitHub PR/issue capture, scoped checks, deterministic JSON/Markdown reports, and report comparison.
- Standard-library CLI, offline regression suite and optional host discovery metadata.

### Fixed
- Portable resolution of the GitHub `gh` executable for live capture and mocked subprocess endpoint tests.

