# Governance Adapt Mode

Use `governance-adapt` only to extract governance-owned facts from read-only legacy material into a new canonical `schema_version: 2` Nomia artifact.

## Required inputs

- legacy source path and observation timestamp;
- externally supplied current `spec_id` and its evidence reference;
- selected governance profile, lifecycle stage, and governance status;
- separate output path.

The mode never derives a current identity from a legacy ULID, renames a legacy identity, or overwrites the source. Legacy identity remains provenance only.

## Deterministic procedure

1. Read the legacy artifact without mutation.
2. Copy only governance-owned fields that exist in the canonical scaffold.
3. Require current profile, lifecycle, governance status, canonical identity, and identity provenance.
4. Reset planning, execution, validation, release, decision, and handoff states to `unknown` unless current attributed evidence is supplied through their owning contracts.
5. Record source, observation time, copied/ignored sections, previous identity, current identity, rationale, and affected commitments.
6. Validate the output with `validate_ops.py --require-canonical`.
7. For repository-facing output, also run `validate_board_paths.py`.

```bash
python scripts/adapt_governance.py legacy-ops.yaml canonical-ops.yaml \
  --spec-id spec-2026-07-20-feature-key \
  --spec-id-provenance registry/spec-2026-07-20-feature-key.yaml \
  --profile governed \
  --lifecycle triage \
  --governance-status triage \
  --observed-at 2026-07-20T12:00:00Z \
  --report adaptation-report.json
```

## Stop conditions

Stop without writing when the current identity or provenance is absent or invalid, input and output paths are equal, a legacy ULID is supplied as the new identity, technical truth would need to be inferred, or canonical validation fails.
