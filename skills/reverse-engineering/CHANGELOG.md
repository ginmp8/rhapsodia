# Changelog

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
