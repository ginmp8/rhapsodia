# Provenance

New RhapsodIA capability adapted from a verified integration workflow on 2026-11-08, involving `ginmp8/pandacode-extended` PRs #119 and #120. The source was a source-tree reconciliation, not a Git rebase. Generic Git mechanics are implemented independently for reuse across repositories and do not embed or copy application code from PandaCode.

The first tracked release is `0.1.0`. The package requires local Git 2.38+ and Python 3.10+ for its deterministic helper. Execution tests use generated temporary repositories with no real credentials or network access.
