# RhapsodIA distribution changelog — 0.18.0

## Added
- New first-party `deterministic-pr-audit` v0.1.0 Skill and executable Python standard-library CLI for SHA-pinned PR-to-issue scoring.
- Frozen requirements/check plans, explicit evidence receipts, reproducible JSON/Markdown scoring, candidate comparability checks, and offline regression tests.

## Fixed
- Branch Reconciliation v0.1.1 uses explicit `git diff --check` whitespace settings that accept CRLF resolution files while continuing to reject trailing spaces.
- Offline GitHub capture tests mock the subprocess boundary across operating systems and verify GitHub endpoint pagination without invoking a Windows `.cmd` launcher.

## Changed
- Canonical Skill inventory from 76 to 77; package/plugin release metadata, agent manifest, license catalog and release documentation aligned to 0.18.0.

## Validation boundary
- Fifteen local Skill tests were run independently; RhapsodIA CI and host installations require separate verification.
- Frozen-score replay does not make the initial acceptance-criteria interpretation deterministic or prove unobserved behavior.
