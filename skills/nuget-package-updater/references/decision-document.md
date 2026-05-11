# Package version decision document standard

Every real package update check or write operation must create a Markdown decision document under:

```text
docs/pkgs-versions/
```

Use the script flag:

```bash
--write-decision-doc
```

Optional overrides:

```bash
--decision-doc-dir docs/pkgs-versions
--decision-doc-name nuget-package-update-decisions-YYYYMMDD.md
```

## Required sections

The generated document must follow this structure:

```markdown
# NuGet package version decisions

- Generated at: `<UTC timestamp>`
- Source file: `<Directory.Packages.props path>`
- Target framework: `<TFM>`
- Wrote package file: `<true|false>`
- Restore validation: `<true|false>`
- Safety validation: `<true|false>`

## Decision policy

- Use only stable NuGet versions.
- Reject prerelease, unlisted, deprecated, and vulnerable candidate versions.
- Validate candidate package metadata through NuGet Registration API.
- Cross-check vulnerability ranges through NuGet VulnerabilityInfo API when the source exposes it.
- Respect locks and pins declared in Directory.Packages.props.
- Do not use MCP or manual version selection for this package update workflow.

## Summary

- Package declarations analyzed: `<count>`
- Updated: `<count>`
- Unchanged: `<count>`
- Locked: `<count>`
- Skipped: `<count>`
- Errors: `<count>`

## Package decisions

| Package | Current | Current safety | Latest stable | Selected | Decision | Compatibility | Reason |
|---|---:|---|---:|---:|---|---|---|

## Details

### `<PackageId>`

- Line: `<line>`
- Current version: `<version>`
- Latest stable version considered: `<version>`
- Selected version: `<version>`
- Action: `<update|unchanged|locked|skipped|error>`
- Reason: `<reason>`
- Candidate count: `<count>`
- Safe candidate count: `<count>`
- Validated candidate count: `<count>`
- Source: `<NuGet source>`
```

## Interpretation rules

- `update`: the script found a safe compatible version and write mode may update it.
- `unchanged`: the current version is already the selected safe version, or no policy-allowed newer version exists.
- `locked`: the package is pinned or locked in `Directory.Packages.props`; do not change it.
- `skipped`: a newer candidate exists but was rejected by policy, metadata, vulnerability, deprecation, or compatibility rules.
- `error`: the script could not make a trusted decision; do not update manually.
