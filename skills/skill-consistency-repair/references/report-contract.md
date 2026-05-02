# Report Contract

Use for durable reports and final responses.

## Sections

1. Target identity and inspected path.
2. Mode and evidence policy.
3. Inventory summary.
4. Decision: pass, repair recommended, blocked, or package-ready.
5. Findings by severity/category.
6. Broken local references and missing files.
7. Resource integration map.
8. Ownership and scope review.
9. Validation and packaging gates.
10. Proposed plan or applied changes.
11. Measured before/after comparison when available.
12. Remaining risks and next hypothesis.

## Finding format

```text
[id] [severity] [category] title
Evidence: file path and section or line when available
Problem: observed inconsistency
Impact: why it matters
Repair: smallest safe correction
Gate: validation that should pass after repair
Confidence: high | medium | low
```

## Evidence labels

- `measured`: command output or supplied scenario result inspected.
- `inspected`: file content read or inventoried.
- `inferred`: reviewer judgment from inspected evidence.
- `planned`: scenario, metric, or improvement not executed.
- `blocked`: evidence unavailable or unsafe to modify.

Keep labels distinct. Say `scenario coverage planned` unless executed scenario evidence supports a stronger claim.
