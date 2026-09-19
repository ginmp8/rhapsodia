---
applyTo: "**/{Directory.Packages.props,*.csproj,*.sln}"
---

# NuGet package update workflow

When asked to update centrally managed NuGet versions, use the repository copy of `tools/nuget-updater/nuget_update.py` as the only version-selection authority. Do not manually choose or edit a version that the script can decide. Do not use MCP package metadata for the decision.

First run:

```bash
python tools/nuget-updater/nuget_update.py check \
  --file Directory.Packages.props \
  --target-framework net10.0 \
  --write-decision-doc \
  --write-evidence \
  --report-format markdown
```

Before writing, review the baseline hash, source identity, lock/pin identity, metadata snapshot, candidate provenance, stable reason codes, write preview, and decision receipt.

For the write, require the prior decision and replay the checked metadata when available:

```bash
python tools/nuget-updater/nuget_update.py update \
  --file Directory.Packages.props \
  --target-framework net10.0 \
  --write \
  --write-decision-doc \
  --write-evidence \
  --expected-decision-receipt docs/pkgs-versions/nuget-decision-receipt-<id>.json \
  --metadata-snapshot-input docs/pkgs-versions/nuget-metadata-snapshot-<id>.json \
  --validate-repository \
  --report-format markdown
```

Rules:

- stable versions only by default;
- never select preview/alpha/beta/rc/dev/nightly versions;
- validate Registration metadata and VulnerabilityInfo through the script;
- reject unlisted, deprecated, vulnerable, or untrusted candidates under default policy;
- preserve configured feed order; first feed wins exact-version ties;
- respect every lock/pin/manual/no-update marker;
- do not bypass a lock unless explicitly requested by the user;
- do not manually select a version after metadata/feed/SDK/restore failure;
- do not perform unrelated upgrades;
- treat a changed decision identity as a blocked write;
- treat changed `Directory.Packages.props` bytes between analysis and write as a blocked write;
- preserve last-known-good evidence;
- use atomic script writes, never a direct editor replacement;
- after write, require repository validation evidence; default `--validate-repository` runs restore/build/test;
- if validation fails, the script must roll the package file back;
- summarize receipt paths, hashes, validation status, and rollback state; never claim unexecuted validation passed.
