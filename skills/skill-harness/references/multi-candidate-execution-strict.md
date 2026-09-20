# Strict Multi-Candidate Execution Evidence

Use this contract when a caller needs evolution/search evidence with identity-bound repeated runs and trace-manifest provenance. It is additive to the existing `skill-opt.harness-multi-candidate-evidence` v2 contract; it does not replace or reinterpret v2.

## Contract identity

- contract id: `skill-opt.harness-multi-candidate-evidence-strict`
- version: `1`
- template: `assets/templates/multi-candidate-manifest-strict.json.template`
- validator: `scripts/validate_multi_candidate_manifest_strict.py`

The legacy v2 surface remains unchanged for existing consumers. Use this strict contract only when the caller explicitly accepts it or when a coordinated ecosystem change set migrates consumers.

## Required invariants

For every run:

- `candidate_id` identifies the logical candidate;
- `candidate_identity` identifies the exact candidate bytes or immutable artifact;
- the same `candidate_id` may appear in multiple runs only when `candidate_identity` is identical;
- different `candidate_id` values must not share one `candidate_identity`;
- `run_id`, `work_dir`, `trace_id`, `trace_manifest_id`, and `trace_manifest_sha256` are unique per run;
- `trace_manifest_sha256` is a 64-character SHA-256 hex digest;
- comparable runs use the same `evaluator_id`, `scenario_set_id`, and `evaluation_policy_id`;
- holdout/blind claims fail when evaluator-only assets were candidate-visible.

Repeated runs of one candidate are allowed so noise can be estimated without inventing a new candidate identity. Survivor selection, statistical aggregation, promotion, and final packaging remain outside Harness ownership.

## Trace-manifest provenance

`trace_manifest_id` and `trace_manifest_sha256` bind each row to one immutable trace-manifest artifact. The portable validator checks identity shape and cross-run uniqueness. Dereferencing the artifact bytes is capability-dependent and remains a separate evidence step; do not claim physical trace availability solely because the envelope validates.

Do not embed secrets or evaluator-only payloads in this envelope. Use identifiers and hashes.

## Validation

```text
<PYTHON> <skill-root>/scripts/validate_multi_candidate_manifest_strict.py <manifest.json>
```

A failing validator blocks use of the envelope as strict multi-candidate evidence. The existing v2 validator remains the compatibility path for existing consumers and must not be silently upgraded to strict semantics without a versioned, coordinated consumer migration.
