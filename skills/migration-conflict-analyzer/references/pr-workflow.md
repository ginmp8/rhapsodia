# PR Migration Review Workflow

## Evidence precedence

1. resolved Git base/head/merge-base SHAs;
2. exact changed migration bytes and SHA-256;
3. changed ModelSnapshot/Designer identities as supporting evidence;
4. base migration-history identities read from the resolved base revision;
5. generated SQL identity when supplied;
6. provider/DbContext/deployment evidence when supplied.

## Local Git workflow

```bash
python3 -S scripts/migration_conflict_analyzer.py . \
  --git-base origin/main \
  --format json \
  --output migration-conflict-report.json \
  --receipt migration-conflict-analysis-receipt.json
```

The analyzer records the requested base ref plus resolved base/head/merge-base SHAs. Base-history collision checks are made against migration identities read from the resolved base revision, not inferred from the current working tree.

A dirty working tree is recorded. The analyzed working bytes remain bound by file SHA-256; do not describe them as immutable commit bytes unless they match the recorded revision evidence.

## Connector-only PR workflow

When repository execution is unavailable:

1. fetch the PR file list/diff;
2. read every changed main migration file;
3. read changed ModelSnapshot/Designer files as supporting evidence;
4. obtain base migration identities when a base-conflict claim is required;
5. preserve exact diff/file revision identifiers supplied by the connector;
6. apply `conflict-heuristics.md` manually;
7. mark deterministic analyzer, Git-object, and package-owned validation as `not-run`.

Do not claim a base collision if base migration history was not inspected.

## Generated SQL

Generated SQL may be supplied with `--generated-sql` to bind its hash to the report. Hashing it is not the same as executing or semantically proving it.

For high-risk changes, separately generate and inspect provider-specific SQL and test both:

- clean database path;
- upgraded database path with representative existing data.

## Review comment shape

For each material finding include:

- finding/rule ID;
- exact migration/operation evidence;
- severity, confidence, evidence status, and gate;
- concrete failure/risk mechanism without overstating certainty;
- smallest safe remediation;
- validation evidence still needed;
- explicit uncertainty.

## Merge/apply interpretation

Use the machine summary vocabulary:

- `block`: at least one frozen `block` gate;
- `changes-required`: high findings without a critical/block gate;
- `review-required`: medium findings without high/critical;
- `no-static-blocker`: no critical/high/medium finding from the supplied static evidence.

`no-static-blocker` is not a production-safety guarantee.
