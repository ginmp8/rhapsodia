# Changelog

## [0.2.2] - 2026-10-18

### Fixed
- Shortened the portable `SKILL.md` frontmatter `description` from 690 to 491 characters to satisfy hosts with a 500-character discovery-description limit.
- Preserved the existing activation scope, six workflow modes, safety boundaries, references, scripts, tests, fixtures and host adapters.
- No implementation or public CLI/data contract changes; this is a compatible metadata-only correction.

## [0.2.1] - 2026-10-18

### Fixed / merged
- Rebased the LeanREA-inspired instruction optimization on the complete, supplied `0.2.0` reference instead of the older installed/catalog snapshot. No upstream reference files, scripts, tests, fixtures or optional browser capabilities were removed.
- Added `references/fast-static-triage.md` as a conditional cheap-first, bounded static discovery guide and connected it from `SKILL.md`, `README.md`, `references/discover.md`, `references/capability-matrix.md` and the source-aware research notes.
- Kept `web_investigator.py` as the sole supported browser entrypoint (including offline fixture mode, audits and route correlation); did **not** reintroduce the retired `browser_capture.py` entrypoint.
- Preserved the six mode router, 13 MCP tools, authorization boundaries, observation contracts, all original `0.2.0` source/test/fixture bytes, and the original release history.

### Compatibility and validation
- Compatible documentation/routing repair; no Python/C# runtime implementation, test, fixture or browser data format changed. `0.2.0` commands, APIs and migration guidance remain authoritative.
- The LeanREA benchmark is third-party evidence about LeanREA versus REA, **not** performance validation of this skill. No throughput, time, cost or token improvement is claimed without a paired test.

## [0.2.0] - 2026-10-16

### Consolidated
- Removed `scripts/browser_capture.py` after migrating package-local consumers to `web_investigator.py`. The latter is now the sole supported Playwright browser entrypoint; remaining static analysis, HTTP replay, six modes and 13 MCP tools are unchanged.
- Preserved the former tool's navigations, clicks, fills, keypresses, complete selected-element SHA-256, explicit text capture (up to 4096 characters), screenshot capture, same-origin request/response metadata and event overflow accounting; additional advanced interactions, offline reviewed fixtures, exploration and audit integration remain available.
- Updated capability matrix, usage guide, trust/replay references and acceptance tests without deleting any original test scenario.

### Migration / compatibility
- **Breaking CLI and Python import change:** replace `scripts/browser_capture.py --origin ...` with `scripts/web_investigator.py capture --origin ...`, add `--mutations-approved` for click/fill/press/etc.; import `checked_actions` / `inspect_browser` from `web_investigator` rather than importing `browser_capture`.
- **Trace schema change:** outputs now use `mode: web-investigation` with `steps`/`events`, not `mode: authorized-browser-capture` with `observations`. External consumers must migrate their field mappings; no legacy alias is included.
- Existing V1/V2 `behavior_lab` observational contracts, MCP tool names, original parser CLI commands and recorded corpora are untouched.
- Tests cover the migrated permission and path guards, full selected-text hash, optional screenshot and blocked-overwrite behavior. Live HTTP/browser access across hosts is not asserted unless independently tested.

## [0.1.0] - 2026-10-16

First tracked release of the existing unversioned Reverse Engineering + Behavioral Reconstruction package. Previous unpublished or historical versions were not independently established.

### Added
- Optional portable Playwright browser investigation with bounded interactions, passive link exploration, DOM/network/console metadata, local performance indicators and responsive-overflow observations.
- Trusted offline HTML fixture execution when the host prevents HTTP navigation; reports clearly distinguish fixture evidence from actual requests.
- Frozen-policy evaluator for recorded functional, security-header and performance expectations with explicit fail/incomplete outcomes.
- Read-only, bounded source credential-marker scanner with redacted findings and no validity checks.
- Bounded route-shape correlation and dynamic evidence ingestion into the existing SQLite graph; inferred relationships remain labeled inferred.
- Portable usage guidance, sandbox capability detection, runnable example fixtures, and regression tests.

### Compatibility and limits
- Existing six skill modes, legacy CLI tools, data contracts and the 13 MCP tools are preserved.
- New browser capabilities are optional and require separately approved trusted targets, installed Playwright and Chromium; no automatic downloads.
- Browser route interception does not constitute network isolation. Security audits are partial observations, not evidence of complete security. Browser HTTP testing could not be validated in the restricted ChatGPT sandbox.
- Root SemVer version tracking begins at 0.1.0; no prior tracked release version was present in the baseline.
