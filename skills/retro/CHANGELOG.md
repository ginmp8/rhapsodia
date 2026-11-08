# Changelog

## [0.1.1] - 2026-11-08

### Fixed
- Added a portable self-contained SVG icon and complete ChatGPT/Codex discovery metadata (`icon_small`, `icon_large`, `brand_color` and a default prompt).
- Added host-independent structural compatibility gates and documented required capability fallbacks for the 0.17.0 distribution.

### Compatibility
- The OpenAI adapter is optional; canonical Agent Skills instructions remain usable by other compatible hosts.
- This patch does not transfer responsibility to or from Nomia, Mago, Magia or other established RhapsodIA capabilities.

## [0.1.0] - 2026-11-08

### Added
- Introduced the RhapsodIA-adapted Retro capability, grounded in Matt Pocock's MIT-licensed workflow.
- Clarified the portable invocation and the RhapsodIA Nomia/Mago/Magia ownership boundaries.
- Added immutable upstream provenance, MIT license notice and discoverable host metadata.

### Compatibility
- Initial independently versioned RhapsodIA package. Does not change existing skill or internal-contract versions.
- Execution, subagent delegation and persistent writes depend on host capabilities and authorization; no unperformed validation is claimed.
