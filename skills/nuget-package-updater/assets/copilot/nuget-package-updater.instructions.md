---
applyTo: "**/{Directory.Packages.props,NuGet.Config,*.csproj,*.fsproj,*.vbproj,*.sln,packages.lock.json}"
---

# NuGet package update workflow

When asked to update centrally managed NuGet versions, use the repository copy of `tools/nuget-updater/nuget_update.py` as the version-selection authority. Do not manually choose a version the script can decide. Do not use MCP package metadata as a substitute for NuGet/repository evidence.

Prefer an explicit repository-owned `NuGet.Config` and repository root when they exist:

```text
python tools/nuget-updater/nuget_update.py check \
  --file Directory.Packages.props \
  --repository-root . \
  --nuget-config NuGet.Config \
  --target-framework net10.0 \
  --write-decision-doc \
  --write-evidence \
  --report-format markdown
```

Omit `--nuget-config` only when the repository intentionally does not use one for this workflow.

Before writing, review baseline, source/config/mapping identity, repository model, locks/pins, `VersionOverride`, metadata snapshot, candidate provenance, stable reason codes, write preview, and decision receipt.

For the write, require the checked decision and replay the checked metadata when available:

```text
python tools/nuget-updater/nuget_update.py update \
  --file Directory.Packages.props \
  --repository-root . \
  --nuget-config NuGet.Config \
  --target-framework net10.0 \
  --write \
  --write-decision-doc \
  --write-evidence \
  --expected-decision-receipt docs/pkgs-versions/nuget-decision-receipt-<id>.json \
  --metadata-snapshot-input docs/pkgs-versions/nuget-metadata-snapshot-<id>.json \
  --validate-repository \
  --audit-repository \
  --report-format markdown
```

Rules:

- stable versions only by default;
- reject unlisted, deprecated, vulnerable, untrusted, and source-ambiguous candidates under default policy;
- never claim the first configured feed is authoritative for an exact-version tie;
- prefer Package Source Mapping to constrain eligible feeds;
- fail closed on selected conditional/duplicate `PackageVersion` declarations;
- skip a package with an active project `VersionOverride`;
- respect every lock/pin/manual/no-update marker;
- do not manually select a version after metadata/source/config/SDK/restore/audit failure;
- treat the temporary restore as package/TFM compatibility only, not transitive graph proof;
- use `--audit-repository` when transitive NuGetAudit evidence is required; `NU1905` is blocking;
- record `NU1510` pruning evidence without auto-removing references;
- treat a changed decision identity or package baseline as a blocked write;
- preserve exact last-known-good package and lock-file bytes;
- use atomic script writes, never direct editor replacement;
- if validation fails, require package-file and lock-file rollback evidence;
- never pass package-feed credentials in prompts, CLI flags, evidence files, or source control;
- summarize receipt paths, hashes, validation/audit status, and recovery state; never claim an unexecuted gate passed.
