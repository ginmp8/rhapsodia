# Report Contract

The machine-readable JSON report is authoritative for structural audit output. Markdown is a human-readable rendering of the same evidence.

## Report versions

`report_version: 3` is current. `scripts/validate_consistency_report.py` preserves validation compatibility for v1 and v2 reports; new audit output uses v3.

### Report v3 required surfaces

- target path, generation timestamp, `evidence_type`, deterministic `inventory_identity`;
- inventory summary;
- authority contract and closed resource-classification contract;
- typed `relation_contract` plus progressive-disclosure topology;
- separate `conformance.portable_core_spec`, `conformance.host_compatibility`, and supplemental reference-validator state;
- one resource-classification row per inventoried resource, including `trace` and `trace_coverage`;
- findings with evidence class;
- evidence-class summary;
- static score with explicit non-readiness meaning;
- readiness that never promotes a static audit into publish/package/runtime proof.

Validate with `scripts/validate_consistency_report.py`.

## Resource classification row

Required: path, role, provisional status, confidence, evidence, full trace dimensions, per-dimension trace coverage, semantic-review flag, and `deletion_allowed=false` for machine classification. Static tooling never grants deletion rights.

Trace coverage states are `found`, `inspected-none`, `not-inspected`, `unsupported`, and `blocked`. No zero-result detector is allowed to masquerade as proof that an external consumer does not exist.

## Finding format

Each v3 finding records: id, severity, category, subjects, evidence, evidence label, evidence class, problem, smallest repair, gate, and confidence.

## Evidence labels versus evidence classes

Labels describe the local evidence source (`measured`, `inspected`, `inferred`, `planned`, `blocked` when used by a workflow). Classes describe proof strength:

- `mechanically-proven`: deterministic parser/hash/schema/static tool evidence;
- `behaviorally-proven`: captured execution against a frozen evaluator;
- `semantically-supported`: bounded judgment with direct evidence and rubric;
- `planned`: designed but not executed evidence;
- `blocked`: required evidence unavailable or unsafe to obtain.

Do not promote one class into another.

## Conformance separation

`portable_core_spec` is a host-neutral claim. `host_compatibility` is a host/profile claim. A host-specific tolerance must not change portable-core status. External/reference validators are supplemental and never sufficient package-wide proof by themselves.

## Readiness separation

A clean static report proves only the static audit found no blocker/high inconsistency. It does not prove evaluator integrity, runtime behavior, semantic correctness, package validity, or behavioral improvement. Those require their own gates/receipts.
