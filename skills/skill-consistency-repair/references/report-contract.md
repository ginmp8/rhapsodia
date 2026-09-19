# Report Contract

The machine-readable JSON report is authoritative for structural audit output. Markdown is a human-readable rendering of the same evidence.

## Report v2 required fields

- `report_version: 2`;
- target path and generation timestamp;
- `evidence_type`;
- deterministic `inventory_identity` (SHA-256 fingerprint);
- inventory summary;
- authority contract reference;
- closed resource-classification contract;
- one resource-classification row per inventoried resource;
- findings;
- static score with an explicit non-readiness meaning;
- readiness field that does not claim publish/package readiness from static audit alone.

Validate with `scripts/validate_consistency_report.py`.

## Resource classification row

Required: path, role, provisional status, confidence, evidence, full trace dimensions, semantic-review flag, and `deletion_allowed=false` for machine classification. Static tooling never grants deletion rights; semantic review must satisfy the deletion gate separately.

## Finding format

Each finding records: id, severity, category, subjects, evidence, evidence label, problem, smallest repair, gate, confidence.

## Evidence labels

- `measured`: command output or supplied executed result;
- `inspected`: file/package content directly read or inventoried;
- `inferred`: bounded semantic judgment from inspected evidence;
- `planned`: scenario or improvement not executed;
- `blocked`: required evidence unavailable or unsafe to mutate.

## Readiness separation

A clean static report proves only the static audit found no blocker/high inconsistency. It does not prove evaluator integrity, runtime behavior, semantic correctness, package validity, or behavioral improvement. Those require their own gates/receipts.
