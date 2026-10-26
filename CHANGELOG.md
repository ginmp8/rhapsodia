# Changelog

All notable changes to the RhapsodIA distribution are documented here. Individual Skills follow their own version histories and are not automatically bumped with the distribution.

## [0.14.0] - 2026-10-25

### Added
- Software Improvement Loop v0.1.0, packaged under `skills/software-improvement-loop/`, with four bounded improvement modes, frozen evaluation, isolation, regression gates, and limited iterations.
- A standard-library-only metrics comparator, unit tests, activation fixtures, and report templates.
- Pull-request-triggered full release checks and Skill tests in the Linux, Windows, and macOS portability matrix.

### Changed
- Advanced marketplace, host manifests, agent manifest, release workflows, version assertions, README, and source inventory to distribution version 0.14.0.
- Added Skill archive inventory checks while retaining independent Skill versions, internal semantic contracts, and eight native agent profiles.

### Validation
- Full release and cross-platform CI must pass before acceptance. Structural checks do not establish native-host activation or real software performance gains.

## [0.13.0] - 2026-10-20

- Added portable capability-discovery v0.1.0 and standalone installer support; retained the previous 57 Skills and eight agent profiles. See [release notes](docs/releases/0.13.0.md).

## [0.12.0]

- Added causal-flow-comprehension and selective-decision, research, and evidence-workflow improvements. See [release notes](docs/releases/0.12.0.md).

Historical releases remain in [docs/releases/](docs/releases/).
