# Changelog

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
