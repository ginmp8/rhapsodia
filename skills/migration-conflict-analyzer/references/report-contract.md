# Migration Conflict Report Contract

Use this structure for final answers and generated markdown reports.

## 1. Scope

- mode: file, directory, PR, diff, or manual review;
- files analyzed;
- base branch or base files inspected, if any;
- excluded files such as designer/snapshot files;
- provider and DbContext if known.

## 2. Executive summary

Include:

- total findings;
- count by severity;
- merge/apply recommendation: block, request changes, approve with reservations, or no blockers found;
- one sentence explaining the dominant risk.

## 3. Findings

For each finding:

```markdown
### [Severity] [Title]

- Evidence: file, migration, operation, table/column/object.
- Why it matters: execution failure, data loss, ordering conflict, runtime deployment risk, or snapshot divergence.
- Smallest fix: concrete code or workflow change.
- Validation: command or check.
```

## 4. Safe deployment notes

Mention when applicable:

- prefer generated SQL scripts or migration bundles for production;
- avoid applying migrations from every application instance at startup;
- use expand-contract for rolling deployments;
- test against a database copy with representative data.

## 5. Validation and limits

State exactly what was executed and what was not:

- analyzer command;
- parser limitations;
- generated SQL not inspected unless it was actually inspected;
- provider-specific behavior unknown unless provider was supplied.
