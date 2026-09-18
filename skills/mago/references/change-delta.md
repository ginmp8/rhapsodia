# Change-Delta Contract

Use this contract when an existing spec version changes. The delta is a generated, non-authoritative comparison and never a second source of truth. Canonical intended state remains in the Mago registry and package artifacts.

## Required classes

Every delta reports these sections, using stable requirement or behavior identifiers:

- **Added behavior:** behavior present in the target version and absent from the base version.
- **Modified behavior:** behavior whose obligation, condition, response, acceptance, or constraint changes.
- **Removed behavior:** behavior intentionally absent from the target version; preserve its identifier and removal rationale.
- **Preserved behavior:** material behavior explicitly confirmed unchanged, especially compatibility-sensitive behavior.
- **Compatibility impact:** consumers, producers, schemas, protocols, files, data, or user behavior affected.
- **Migration impact:** data, schema, configuration, rollout, coexistence, backfill, or consumer transition work.
- **Rollback assumptions:** conditions under which the change can be reverted and any irreversible effects.

Use `none - <evidence-backed reason>` only when a class truly has no entries. An empty heading is invalid.

## Deterministic semantics

1. Compare two resolved canonical Mago package versions or a canonical package plus an imported proposal.
2. Generate the delta outside `BOARD_ROOT` or in a caller-owned report directory.
3. Validate all referenced IDs against the base and target packages.
4. Apply accepted intent by editing canonical PRD/design/tasks/validation through the appropriate Mago mode.
5. Re-render the delta to confirm the canonical target expresses the accepted change.
6. Retain the delta only as an audit/report attachment when policy requires; otherwise archive or delete it after merge. Never read it as the current spec source.

Generated adapters may project an OpenSpec-style ADDED/MODIFIED/REMOVED view from this contract. `Preserved behavior`, compatibility, migration, and rollback fields remain Mago extensions and must be reported as losses when the target format cannot represent them.

Use `assets/templates/change-delta.md.template` and validate with:

```bash
python scripts/validate_change_delta.py <external-change-delta.md>
```
