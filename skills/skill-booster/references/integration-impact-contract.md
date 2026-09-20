# Integration Impact Contract

Use this gate when an optimization can change a machine-readable handoff, required input, output envelope, schema, CLI consumed by another skill, or any resource declared in `contracts/integration-manifest.json`.

## Contract manifest

A participating skill declares `contracts/integration-manifest.json` with:

- `exports`: contracts this package **owns**, with contract id, integer version, owner role, and exact package paths that define the public surface;
- `imports`: contracts this package produces instances of or consumes, with accepted owner versions and the workflow branches that require them.

Use exactly one owner for a contract id across the known catalog. A package that merely emits an instance of another skill's schema imports that owner contract; it does not duplicate/export a second definition. Contract ids describe interfaces, not skill names.

A manifest is required only when the skill has a peer-facing machine-readable contract. Do not add empty manifests to unrelated standalone skills merely for uniformity.

## Discovery before mutation

1. Inspect the target for an existing integration manifest.
2. Trace explicit cross-skill handoffs, schemas, receipts, versioned JSON envelopes, required CLIs, and direct peer references. Use architecture/consistency evidence when available.
3. Resolve a peer catalog from supplied roots, a sibling skill catalog, or host capability when available. Do not assume a vendor-private catalog path.
4. If an evidenced peer-facing surface exists but no manifest exists, create a **provisional integration map outside the target** before mutation. Promote it into `contracts/integration-manifest.json` only when ownership and consumers are sufficiently evidenced.
5. If no peer-facing surface is evidenced, record `not-applicable`; do not force a manifest.

## Gate

Before finalizing a candidate whose public surface may have changed:

1. preserve the baseline target and manifest when one exists;
2. freeze the peer-manifest/catalog identity used for the decision;
3. run `scripts/analyze_integration_impacts.py`;
4. treat multiple owners for one contract id as blocking;
5. treat a changed owned surface with no version bump as blocking;
6. treat an owner version rejected by a known importer as blocking;
7. treat a removed owned contract with known importers as blocking;
8. treat an unresolved required import as blocking when the peer catalog is available;
9. when no peer catalog is available, local optimization may continue, but report integration compatibility as `not-proven` and do not claim ecosystem-safe delivery.

When a breaking change is intentional, update the owner and all impacted importers in one governed change set or preserve an explicit compatibility adapter. Internal target tests are necessary but never sufficient for an ecosystem-safe contract change.

## Sequential Booster optimization

When optimizing a catalog skill-by-skill, preserve the latest validated manifests as the compatibility catalog. Before promoting each next candidate, compare it against that catalog. This makes interface impact a cumulative gate instead of relying on the model to remember earlier package details.

## Self-optimization

When Booster optimizes itself, run the active immutable Booster controller against the candidate Booster manifest and frozen peer manifests. A candidate Booster must not waive its own integration failures.
