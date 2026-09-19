# Migration Conflict Report Contract v2

## Machine-readable report

JSON is the canonical report for reproducible comparison. The semantic schema is documented in `../schemas/analysis-report.schema.json`.

Required identity fields:

- `schema_version`;
- `analysis_version`;
- stable `analysis_id`;
- `heuristic_set.name/version/sha256`;
- `input_identity.digest` plus file/support/runtime/generated-SQL identities;
- `git_identity` when Git mode is used;
- provider/DbContext/deployment context when supplied.

Required evidence fields:

- canonical migration metadata;
- deterministic operation records with stable operation IDs;
- findings with stable finding/rule IDs, severity, confidence, evidence status, gate, hazard type, remediation, validation, and uncertainty;
- expand/contract pattern signals when detected;
- gate list;
- summary;
- explicit limitations;
- inline `analysis_receipt`.

## Decision vocabulary

- `block`
- `changes-required`
- `review-required`
- `no-static-blocker`

The decision is a deterministic projection of the frozen heuristic set over supplied evidence. It must not be described as a guarantee of runtime migration safety.

## Finding contract

Every finding must preserve:

```json
{
  "id": "mca:<rule-id>:<stable-hash>",
  "rule_id": "...",
  "severity": "critical|high|medium|low|info",
  "confidence": "high|medium|low",
  "evidence_status": "observed|derived|inferred|supplied|blocked",
  "gate": "block|review-required|manual-review|none",
  "hazard_type": "...",
  "files": [],
  "operation_ids": [],
  "evidence": "...",
  "why": "...",
  "recommendation": "...",
  "validation": "...",
  "uncertainty": "..."
}
```

Do not omit uncertainty from heuristic findings.

## Analysis receipt

The inline receipt binds:

- analysis ID;
- canonical analysis-core hash;
- input digest;
- heuristic-set hash;
- emitted finding IDs;
- severity counts.

When `--receipt` is requested, a standalone delivery receipt additionally records the exact serialized report artifact SHA-256 and destination.

## Markdown report

Markdown is a presentation of the same analysis contract. It must show identity, summary, finding IDs/rules, confidence/evidence, uncertainty, and limitations. JSON remains preferred for regression comparison.

## Claims and limits

State exactly what was executed. Never imply:

- generated SQL was executed when it was only hashed/read;
- production data was inspected when it was not;
- provider-specific runtime behavior is proven from static C# parsing;
- a runtime failure is guaranteed from a heuristic signal;
- a lack of findings proves migration safety.
