# Changelog

## [3.2.0] - 2026-11-07

- Updated from locally installed 2.17.0-dev.1 to the complete 3.2.0 binary/runtime payload from the successful CI artifact for `ginmp8/archify` commit `a4065941f12be7967436261d9934784e381d423c`.
- Includes all ten native diagram modes, one-page Explainer, `finalize` validation/delivery, updated schemas, renderer, Viewer and localized text.
- Added portable Agent Skills metadata, an explicit release identity, and context-loading previews without changing diagrams' authoring/validation semantics.
- Revised examples to avoid false broken-local-link classification in a generic skill package validator.
- Preserved upstream licenses and the source `skill-release.json` version/channel.

### Compatibility

The 3.2.0 CLI and Viewer are the upstream 3.2.0 behavior; 2.x-specific defaults and commands may differ. The historical pinned source archive is retained outside this distributed package. Node.js 18 or later is required; browser gates require a compatible real browser.
