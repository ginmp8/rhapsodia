# Package version decision document standard

Every real `check` or `update` should pass:

```text
--write-decision-doc --write-evidence
```

The default decision document lives under `docs/pkgs-versions/` and uses the stable decision identity:

```text
nuget-package-update-decisions-<decision-id>.md
```

## Required evidence context

The machine-readable report/receipts are authoritative for hashes and automation. The Markdown decision document is the human review surface and should be interpreted together with:

- `Directory.Packages.props` baseline SHA-256;
- target framework;
- ordered NuGet sources;
- metadata snapshot SHA-256;
- decision identity;
- write preview;
- package decisions and stable `reason_code` values;
- final package-file hash when a write occurred;
- repository validation status when commands were executed;
- rollback status when applicable.

## Package decision meanings

- `update`: the deterministic script selected a newer policy-allowed candidate.
- `unchanged`: current version already converged or no newer policy-allowed candidate exists.
- `locked`: lock/pin intent forbids mutation.
- `skipped`: a candidate path existed but safety/compatibility policy prevented selection.
- `error`: trusted decision evidence could not be established; do not update manually.

Free-form `reason` exists for human context. Prefer `reason_code` for repeatable automation/comparison.

## Evidence files

`--write-evidence` produces content-addressed sidecars under the same default directory:

```text
nuget-metadata-snapshot-<snapshot-id>.json
nuget-decision-receipt-<decision-id>.json
nuget-package-update-receipt-<decision-id>.json   # update --write only
```

The package-update receipt status, final file hash, validation evidence, and rollback evidence determine whether a write remains applied. A planned decision receipt alone does not prove mutation.
