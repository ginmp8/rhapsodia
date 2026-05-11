# Usage reference

## Local setup

Recommended repository layout when using this with GitHub Copilot locally:

```text
repo/
├── .github/
│   └── instructions/
│       └── nuget-package-updater.instructions.md
├── tools/
│   └── nuget-updater/
│       └── nuget_update.py
├── docs/
│   └── pkgs-versions/
└── Directory.Packages.props
```

Copy files from the skill:

```bash
mkdir -p tools/nuget-updater .github/instructions docs/pkgs-versions
cp scripts/nuget_update.py tools/nuget-updater/nuget_update.py
cp assets/copilot/nuget-package-updater.instructions.md .github/instructions/nuget-package-updater.instructions.md
```

## Non-negotiable execution rule

Never use MCP for NuGet package updates. The script is the only source of truth for selecting, validating, and writing versions. Copilot should call the script, read the report, and summarize the result.

## Common commands

Scan package declarations and lock status:

```bash
python tools/nuget-updater/nuget_update.py scan \
  --file Directory.Packages.props \
  --report-format markdown
```

Check safe update plan for .NET 10 without writing, and generate a decision document:

```bash
python tools/nuget-updater/nuget_update.py check \
  --file Directory.Packages.props \
  --target-framework net10.0 \
  --report-format markdown \
  --write-decision-doc
```

Apply latest stable compatible patch or minor updates and generate a decision document:

```bash
python tools/nuget-updater/nuget_update.py update \
  --file Directory.Packages.props \
  --target-framework net10.0 \
  --write \
  --report-format markdown \
  --report nuget-update-report.md \
  --write-decision-doc
```

Allow major upgrades explicitly:

```bash
python tools/nuget-updater/nuget_update.py update \
  --file Directory.Packages.props \
  --target-framework net10.0 \
  --allow-major \
  --write \
  --write-decision-doc
```

Only update one package:

```bash
python tools/nuget-updater/nuget_update.py update \
  --file Directory.Packages.props \
  --target-framework net10.0 \
  --package Newtonsoft.Json \
  --write \
  --write-decision-doc
```

Use a private or custom source in addition to nuget.org:

```bash
python tools/nuget-updater/nuget_update.py check \
  --file Directory.Packages.props \
  --target-framework net10.0 \
  --source https://api.nuget.org/v3/index.json \
  --source https://example.test/nuget/v3/index.json \
  --write-decision-doc
```

## NuGet API checks

The script uses NuGet V3 resources discovered from the service index:

- `SearchAutocompleteService`: stable listed version discovery with `prerelease=false` and `semVerLevel=2.0.0`.
- `RegistrationsBaseUrl`: package metadata, listed state, deprecation metadata, and registration vulnerabilities.
- `VulnerabilityInfo`: vulnerability index/pages used to cross-check vulnerable version ranges locally.

A candidate version is rejected when any trusted NuGet metadata indicates it is unlisted, deprecated, or vulnerable at or above the configured severity threshold.

## Safety policy

Default policy:

- stable versions only;
- no prerelease labels;
- no major upgrades;
- patch and minor upgrades allowed;
- no downgrades;
- reject unlisted versions;
- reject deprecated versions;
- reject versions with known vulnerabilities from Registration metadata or VulnerabilityInfo ranges;
- require trusted NuGet registration metadata;
- restore validation enabled;
- locked packages are never changed.

Use these override flags only for explicit troubleshooting or tests:

```bash
--allow-deprecated
--allow-vulnerable
--allow-unlisted
--allow-untrusted-metadata
--disable-safety-validation
--disable-restore-validation
```

Do not use those override flags for normal local update work.

## Decision document

For real checks and updates, always pass:

```bash
--write-decision-doc
```

The default output directory is:

```text
docs/pkgs-versions/
```

The generated file name is timestamped by default:

```text
nuget-package-update-decisions-YYYYMMDD-HHMMSSZ.md
```

Use a deterministic name when needed:

```bash
--decision-doc-name nuget-package-update-decisions.md
```

See `references/decision-document.md` for the required structure.

## Locking packages in Directory.Packages.props

The updater skips entries with explicit lock metadata:

```xml
<PackageVersion Include="Example.Package" Version="1.2.3" Locked="true" />
<PackageVersion Include="Example.Package" Version="1.2.3" Pin="true" />
<PackageVersion Include="Example.Package" Version="1.2.3" Pinned="true" />
<PackageVersion Include="Example.Package" Version="1.2.3" NoUpdate="true" />
<PackageVersion Include="Example.Package" Version="1.2.3" UpdatePolicy="manual" />
<PackageVersion Include="Example.Package" Version="1.2.3" UpdatePolicy="locked" />
```

It also skips entries with adjacent lock comments:

```xml
<!-- nuget-updater: lock -->
<PackageVersion Include="Example.Package" Version="1.2.3" />
```

Supported comment intent includes `nuget-updater: lock`, `nuget-updater: ignore`, `pinned`, `locked`, `travado`, `fixado`, and `no-update`.

## Exit codes

- `0`: script completed successfully.
- `1`: technical failure, such as missing file, feed access error, malformed version data, or restore execution problem.
- `2`: policy failure when `--fail-on-incompatible` or `--fail-on-outdated` is enabled.

## Offline smoke test mode

Offline tests are intentionally explicit because they cannot validate NuGet deprecation or vulnerability metadata.

```json
{
  "Newtonsoft.Json": ["13.0.1", "13.0.4", "14.0.0-beta.1"],
  "Serilog": ["2.12.0", "2.12.1"]
}
```

Run:

```bash
python tools/nuget-updater/nuget_update.py update \
  --file Directory.Packages.props \
  --versions-file versions.json \
  --allow-untrusted-versions-file \
  --disable-restore-validation \
  --write \
  --write-decision-doc
```

Use this only for testing parser and write behavior. Do not use offline version files for real update decisions.
