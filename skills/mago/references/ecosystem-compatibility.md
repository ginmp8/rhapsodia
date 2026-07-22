# Ecosystem Compatibility

Nomia, Mago, and Magia currently participate in ecosystem release `1.6.0`.

## Compatibility rule

- The current `VERSION` of each package must equal its entry in `references/ecosystem-compatibility.json`.
- Mixed package versions are rejected before mutation or handoff consumption.
- Shared priority, handoff, and compatibility JSON files must be byte-equivalent across the three packages.
- Package-local archives remain individually distributable, but an ecosystem readiness claim requires all three package validators and the integrated flow harness.
- Compatibility is determined only from current package metadata and the current ecosystem contract. Changelog entries are documentation and are not compatibility aliases or migration inputs.
