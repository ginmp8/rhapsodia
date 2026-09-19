# Usage reference

## Local setup

Recommended repository layout:

```text
repo/
├── .github/instructions/nuget-package-updater.instructions.md
├── tools/nuget-updater/nuget_update.py
├── docs/pkgs-versions/
└── Directory.Packages.props
```

Copy the portable pieces:

```bash
mkdir -p tools/nuget-updater .github/instructions docs/pkgs-versions
cp scripts/nuget_update.py tools/nuget-updater/nuget_update.py
cp assets/copilot/nuget-package-updater.instructions.md .github/instructions/nuget-package-updater.instructions.md
```

## Non-negotiable rule

The script is the version-selection authority. Do not manually choose a package version when the script can decide, and do not bypass missing/untrusted metadata by editing `Directory.Packages.props` directly.

## Commands

### Scan

```bash
python tools/nuget-updater/nuget_update.py scan \
  --file Directory.Packages.props \
  --target-framework net10.0 \
  --report-format markdown
```

### Check with reproducibility evidence

```bash
python tools/nuget-updater/nuget_update.py check \
  --file Directory.Packages.props \
  --target-framework net10.0 \
  --report-format markdown \
  --write-decision-doc \
  --write-evidence
```

This creates under `docs/pkgs-versions/` by default:

- `nuget-package-update-decisions-<decision-id>.md`;
- `nuget-metadata-snapshot-<snapshot-id>.json`;
- `nuget-decision-receipt-<decision-id>.json`.

### Reproducible write from the checked decision

Use both the checked decision receipt and exact metadata snapshot when available:

```bash
python tools/nuget-updater/nuget_update.py update \
  --file Directory.Packages.props \
  --target-framework net10.0 \
  --write \
  --write-decision-doc \
  --write-evidence \
  --expected-decision-receipt docs/pkgs-versions/nuget-decision-receipt-<decision-id>.json \
  --metadata-snapshot-input docs/pkgs-versions/nuget-metadata-snapshot-<snapshot-id>.json \
  --validate-repository \
  --report-format markdown
```

`--metadata-snapshot-input` fails closed if the snapshot lacks a required URL. It never silently returns to live network access.

If you intentionally want fresh metadata, omit snapshot replay but keep `--expected-decision-receipt`; any decision drift blocks the write.

### Custom repository validation

```bash
python tools/nuget-updater/nuget_update.py update \
  --file Directory.Packages.props \
  --target-framework net10.0 \
  --write \
  --write-evidence \
  --validation-command "restore::dotnet restore My.sln" \
  --validation-command "build::dotnet build My.sln --no-restore" \
  --validation-command "test::dotnet test tests/My.Tests/My.Tests.csproj --no-build"
```

Validation commands run without a shell, in the `Directory.Packages.props` directory, in the exact order supplied. The first failure stops validation and rolls the package file back to its last-known-good bytes.

### Pin the expected package-file baseline

```bash
--expected-baseline-sha256 <sha256>
```

This rejects an unexpected starting file before package analysis proceeds.

### Multiple feeds

```bash
--source https://api.nuget.org/v3/index.json \
--source https://packages.example.test/v3/index.json
```

Feed order is identity-bearing. For the same exact package version, the first configured feed is authoritative for that version.

## NuGet metadata policy

The script discovers V3 resources from each service index:

- `SearchAutocompleteService`: version enumeration with `prerelease=false` and `semVerLevel=2.0.0`;
- `RegistrationsBaseUrl`: listed state, deprecation metadata, package metadata, and registration vulnerabilities;
- `VulnerabilityInfo`: vulnerability index/page ranges.

Default policy:

- stable only;
- no major upgrades;
- patch/minor upgrades allowed;
- no downgrade;
- reject unlisted;
- reject deprecated;
- reject known vulnerabilities at/above threshold;
- require trusted metadata;
- validate TFM compatibility;
- never mutate locked/pinned entries.

Diagnostic/test-only overrides remain available:

```text
--allow-deprecated
--allow-vulnerable
--allow-unlisted
--allow-untrusted-metadata
--disable-safety-validation
--disable-restore-validation
```

Do not use these flags for a normal production repository upgrade unless the user explicitly requested that altered risk policy.

## Evidence options

| Option | Meaning |
|---|---|
| `--write-evidence` | write metadata snapshot plus decision/package receipts |
| `--metadata-snapshot-output <path>` | override metadata snapshot path |
| `--metadata-snapshot-input <path>` | strict replay from captured metadata |
| `--decision-receipt <path>` | override decision receipt path |
| `--expected-decision-receipt <path>` | require current decision identity to match prior receipt |
| `--package-update-receipt <path>` | override package-update receipt path |
| `--last-known-good-dir <path>` | override LKG directory |
| `--expected-baseline-sha256 <hash>` | pin exact package-file baseline |
| `--validate-repository` | run default restore/build/test after write |
| `--validation-command label::command` | custom ordered validation |

## Write semantics

A changed update uses:

1. pre-write baseline recheck;
2. LKG preservation;
3. same-directory temp file;
4. fsync;
5. atomic replace;
6. post-write hash verification;
7. requested repository validation;
8. rollback on validation failure.

A second run after a successful update should converge to `writeStatus: no-change` when no newer safe candidate exists.

## Reason codes

Automation should inspect `reason_code`, not free-form `reason` text. Common values:

```text
package-locked
current-version-nonliteral
metadata-unavailable
candidate-metadata-missing
candidate-metadata-untrusted
candidate-unlisted
candidate-deprecated
candidate-vulnerable
no-safe-candidate
no-policy-allowed-newer-version
safe-update-selected
safe-compatible-update
already-selected
no-compatible-candidate
```

## Exit codes

- `0`: successful run, including a successful no-change rerun;
- `1`: technical/precondition failure, including metadata snapshot mismatch/miss or atomic-write failure;
- `2`: policy failure, including requested post-write validation that failed and was rolled back, or explicit `--fail-on-*` conditions.

## Offline test mode

`--versions-file` remains intentionally limited to parser/write tests. It does not prove deprecation, listed state, vulnerability status, or live feed provenance.

```json
{
  "Newtonsoft.Json": ["13.0.1", "13.0.4", "14.0.0-beta.1"]
}
```

Use with:

```bash
--allow-untrusted-versions-file --disable-restore-validation
```

Never use an offline versions file as a substitute for trusted live/snapshotted NuGet metadata in a real update decision.
