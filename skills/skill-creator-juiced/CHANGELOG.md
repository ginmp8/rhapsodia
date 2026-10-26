# Changelog

## [0.2.1] - 2026-10-26

- Enforced a maximum of 500 Unicode characters for YAML frontmatter descriptions to satisfy ChatGPT discovery compatibility.
- Preserved existing skill ownership, runtime behavior and independent validation contracts.

## [0.1.0] - 2026-10-14

- First explicitly tracked package version; historical releases, if any, were not identified in this source snapshot.
- Added a root `VERSION` / `CHANGELOG.md` requirement for skill creation and optimization, with standalone portable validation and immutable-baseline bump checks.
- Migration: previously unversioned skill packages must add a root `VERSION` and matching current `CHANGELOG.md` entry before validating/repackaging. Release notes document the change.
- Preserved the existing activation, orchestration, safety, portability, and evidence rules.

## [0.2.0] - 2026-10-14

- Removed legacy OpenAI-only `policy.products` metadata while retaining the optional adapter and implicit invocation policy.
- Added a versioned optional consumer import of `skill-opt.token-efficiency` v1 for read-only advice on staged skill drafts.
- Explicitly preserved Creator Juiced creation/redesign authority, Markdown skill entrypoints, deterministic quality/version gates, and absent-provider behavior.
- No token-format heuristics copied and no provider-side write authorization granted. Existing creation flows remain supported.
