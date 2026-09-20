# Strict Multi-Candidate Execution Evidence

Use this contract when a caller needs evolution/search evidence with identity-bound repeated runs and trace-manifest provenance. It is additive to the current `skill-opt.harness-multi-candidate-evidence` v4 contract; it does not replace or reinterpret the base contract.

## Contract identity

- contract id: `skill-opt.harness-multi-candidate-evidence-strict`
- version: `2`
- template: `assets/templates/multi-candidate-manifest-strict.json.template`
- validator: `scripts/validate_multi_candidate_manifest_strict.py`

Base v1/v2/v3 and strict v1 remain legacy-readable for their original consumers. Use strict v2 when repeated executions of one candidate are required under the current canonical trace-hash representation.

## Required invariants

For every run:

- `candidate_id` identifies the logical candidate;
- `candidate_identity` identifies the exact candidate bytes or immutable artifact;
- the same `candidate_id` may appear in multiple runs only when `candidate_identity` is identical;
- different `candidate_id` values must not share one `candidate_identity`;
- `run_id`, `work_dir`, `trace_id`, `trace_manifest_id`, and `trace_manifest_sha256` are unique per run;
- strict v2 represents `trace_manifest_sha256` canonically as `sha256:<64hex>`;
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

A failing validator blocks use of the envelope as strict multi-candidate evidence. Strict v1 remains legacy-readable with its original unprefixed 64-hex representation; do not silently reinterpret it as v2.
