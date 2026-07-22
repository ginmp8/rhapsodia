# Ecosystem Versioning

Nomia, Mago, and Magia use one coordinated package release: `1.6.0`.

## Compatibility rule

- All three package versions must equal `ecosystem_release` in `references/ecosystem-compatibility.json`.
- Mixed versions are rejected before mutation or handoff consumption.
- Shared priority, handoff, and compatibility JSON files must be byte-equivalent across the three packages.
- Package-local releases remain individually distributable, but a coordinated ecosystem readiness claim requires all three validators and the integrated flow harness.

## Normalized history

The changelogs were normalized to a shared `1.1.0` through `1.6.0` line. Earlier independent package numbers remain historical provenance only and are not accepted runtime compatibility versions.

| Package | Former independent line | Normalized coordinated line |
|---|---|---|
| Mago | `2.1.0` through `3.0.0` | `1.1.0` through `1.5.0` |
| Magia | `1.1.0` through `1.5.0` | retained |
| Nomia | `2.0.0` through `3.1.0` | `1.1.0` through `1.5.0` |

`1.6.0` is the first release requiring exact three-package compatibility, strict v2 handoffs, and the integrated lifecycle harness.
