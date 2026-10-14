# Changelog

## [0.1.0] - 2026-10-14

- First explicitly tracked package version; historical releases, if any, were not identified in this source snapshot.
- Added a root `VERSION` / `CHANGELOG.md` requirement for skill creation and optimization, with standalone portable validation and immutable-baseline bump checks.
- Migration: previously unversioned skill packages must add a root `VERSION` and matching current `CHANGELOG.md` entry before validating/repackaging. Release notes document the change.
- Updated the portability dependency scan to distinguish bundled local Python modules from external dependencies.
- Preserved the existing activation, orchestration, safety, portability, and evidence rules.
