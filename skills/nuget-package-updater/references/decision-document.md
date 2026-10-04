# Package version decision document standard

For a real `check` or `update`, prefer:

```text
--write-decision-doc --write-evidence
```

The default Markdown decision document is content-addressed by the stable decision identity:

```text
docs/pkgs-versions/nuget-package-update-decisions-<decision-id>.md
```

`--decision-doc-name` accepts a simple `.md` filename only. This prevents path traversal or accidental aliasing with inputs/receipts.

## Required evidence context

The machine-readable report/receipts remain authoritative for hashes and automation. The human document should be read together with:

- `Directory.Packages.props` baseline SHA-256;
- target framework and SDK identity;
- NuGet source identity;
- explicit `NuGet.Config` SHA-256 when supplied;
- Package Source Mapping identity when supplied;
- repository-model identity;
- lock/pin identity;
- metadata snapshot SHA-256;
- decision identity;
- package decisions and stable `reason_code` values;
- candidate provenance, including all eligible sources observed for the exact version;
- write preview and final package-file hash;
- repository restore/build/test/audit evidence when executed;
- lock-file before/after and rollback evidence when applicable.

Do not interpret source order as proof of the restore source. An exact version present in multiple eligible sources is normally rejected as ambiguous.

## Package decision meanings

- `update`: a newer policy-allowed candidate was selected.
- `unchanged`: current version already converged or no newer policy-allowed candidate exists.
- `locked`: central lock/pin intent forbids mutation.
- `skipped`: a supported path was intentionally blocked by a policy/CPM/compatibility guard such as `VersionOverride` or source ambiguity.
- `error`: decision evidence could not be established; do not update manually.

Free-form `reason` is for humans. Automations should use `reason_code`.

## Evidence files

`--write-evidence` emits:

```text
nuget-metadata-snapshot-<snapshot-id>.json
nuget-decision-receipt-<decision-id>.json
nuget-package-update-receipt-<decision-id>.json   # update --write only
```

The package-update receipt status, final hash, lock-file evidence, validation/audit evidence, and rollback evidence determine whether a write remains applied. A planned decision receipt alone never proves mutation.

## Review prompts

Before approving a write, check:

1. Is the config/source/mapping identity the intended one?
2. Is any candidate source-ambiguous?
3. Did static CPM guards find conditional/duplicate declarations or `VersionOverride`?
4. Is package-level compatibility being confused with repository-level graph audit?
5. If lock files changed, is that expected and recorded?
6. If validation failed, do recovery identities match the pre-write state?
