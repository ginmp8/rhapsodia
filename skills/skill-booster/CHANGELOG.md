# Changelog

## [0.1.0] - 2026-10-14

- First explicitly tracked package version; historical releases, if any, were not identified in this source snapshot.
- Added a root `VERSION` / `CHANGELOG.md` requirement for skill creation and optimization, with standalone portable validation and immutable-baseline bump checks.
- Migration: previously unversioned skill packages must add a root `VERSION` and matching current `CHANGELOG.md` entry before validating/repackaging. Release notes document the change.
- Updated the portability dependency scan to distinguish bundled local Python modules from external dependencies.
- Preserved the existing activation, orchestration, safety, portability, and evidence rules.

## [0.2.0] - 2026-10-14

- Removed legacy OpenAI-only `policy.products` metadata while retaining the optional adapter and implicit invocation policy.
- Added optional v1 import of the token-efficiency Golden Source for format advice, isolated candidate optimization, and final comparisons.
- Clarified capability discovery, provider-unavailable reporting, single mutation owner, and independent Booster acceptance gates without copying format policy.
- Existing orchestration, mandatory version checks, evaluation, security and portability contracts are retained. No migration required for workflows that do not delegate token efficiency.
