# Workspace Contract

## Canonical file

Use one canonical `traceability.json` as the source of truth. Generate reports from it; do not maintain a second editable matrix by hand.

The schema is [../assets/schemas/traceability.schema.json](../assets/schemas/traceability.schema.json).

## Workspace placement

Keep transient traceability state outside the target skill directory by default:

```text
<work>/
  traceability.json
  evidence/
  baseline/
  evaluators/
  reports/
```

Do not package this workspace into the target skill unless the user explicitly wants durable provenance inside the skill package.

## Identity separation

Keep these identities distinct:

- research baseline identity;
- target baseline identity;
- evaluator identity;
- candidate target identity;
- final package identity;
- receipt identity.

Do not reuse one hash or version label as proof for a different artifact.

## Schema lifecycle

Current `schema_version` is `1.0`.

Reject unknown major versions. If a future schema changes relation semantics or required fields incompatibly, add an explicit migration instead of silently reinterpreting old workspaces.

## Corpus boundary

Set `scope.completeness_boundary` to `corpus-bounded`. This is a semantic invariant: the traceability workflow proves accounting relative to the frozen corpus and extracted findings, not universal research completeness.

## Resumption

When resuming:

1. validate the workspace before mutation;
2. verify frozen source/evaluator manifests when available;
3. preserve stable IDs for unchanged entities;
4. append new IDs monotonically rather than renumbering old records;
5. invalidate only affected downstream records when an upstream entity changes.

## ID allocation

Use zero-padded IDs with stable prefixes:

- `S-001` source;
- `F-001` finding;
- `R-001` requirement;
- `C-001` change;
- `E-001` evaluation;
- `K-001` conflict.

Do not encode source titles, file paths, or mutable sequence meaning into IDs.
