# Changelog

## [0.1.0] - 2026-11-14

### Added
- SHA-pinned GitHub PR and issue snapshot capture, including paginated comments and changed paths.
- Stable acceptance-criteria extraction, explicit verification plans, immutable evidence and repeatable scoring.
- Standard-library CLI commands for capture, checks, code inspection, optional targeted tests, score, verify, evidence verification and comparison.
- Offline tests covering score replay, capture drift, plan mismatch, Git object pinning and input safety.

### Limitations
- Natural-language requirements and assertion sufficiency need independent review. The CLI guarantees repeatable calculation over frozen evidence, not automatic semantic correctness.
- Live GitHub capture requires authenticated `gh`; optional test execution requires explicit authorization and an isolated checkout.
