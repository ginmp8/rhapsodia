# Usage reference

## At a Glance

- **Purpose:** Provide the complete command/flag and policy reference for operating `nuget_update.py` without weakening source, CPM, candidate, validation, credential, or recovery rules.
- **Load when:** You need exact CLI syntax, local setup, source mapping behavior, candidate policy, compatibility/audit options, reason codes, exit codes, or offline test mode beyond the Top-100 quick start.
- **Decision impact:** Determines which command/flags are valid, which overrides are diagnostic-only, how NuGet sources and CPM declarations are interpreted, and what validation/evidence is required before a write can be accepted.

## Contents

- Runtime and portability
- Local setup
- Non-negotiable rule
- Commands
- NuGet.Config and source mapping
- Central Package Management guards
- Candidate metadata policy
- Package compatibility probe
- Repository validation and audit
- Private feeds and credentials
- Evidence options
- Write and recovery semantics
- Reason codes
- Optional differential oracles
- Exit codes
- Offline test mode

## Runtime and portability

The core updater is a Python 3 standard-library script. Resolve the host's available Python 3 launcher rather than requiring a particular executable name. Runtime validation additionally requires the `dotnet` CLI.

Optional host adapters may copy this script into a repository, but the decision contract does not depend on a specific agent product.

## Local setup

Recommended repository layout:

```text
repo/
├── .github/instructions/nuget-package-updater.instructions.md   # optional Copilot adapter
├── tools/nuget-updater/nuget_update.py
├── docs/pkgs-versions/
├── NuGet.Config                                                  # when repository-owned
└── Directory.Packages.props
```

Copy the portable script and optional Copilot instructions as needed.

## Non-negotiable rule

The script is the version-selection authority for the supported static CPM surface. Do not manually choose a package version to bypass missing metadata, source ambiguity, unsupported conditional CPM semantics, an active `VersionOverride`, failed audit, or failed restore evidence.

## Commands

### Scan

```text
<PYTHON> tools/nuget-updater/nuget_update.py scan \
  --file Directory.Packages.props \
  --repository-root . \
  --nuget-config NuGet.Config \
  --target-framework net10.0 \
  --report-format markdown
```

`--nuget-config` is optional. When omitted and no `--source` is supplied, nuget.org is used.

### Check with reproducibility evidence

```text
<PYTHON> tools/nuget-updater/nuget_update.py check \
  --file Directory.Packages.props \
  --repository-root . \
  --nuget-config NuGet.Config \
  --target-framework net10.0 \
  --report-format markdown \
  --write-decision-doc \
  --write-evidence
```

Default evidence outputs under `docs/pkgs-versions/`:

- `nuget-package-update-decisions-<decision-id>.md`;
- `nuget-metadata-snapshot-<snapshot-id>.json`;
- `nuget-decision-receipt-<decision-id>.json`.

### Reproducible write from the checked decision

```text
<PYTHON> tools/nuget-updater/nuget_update.py update \
  --file Directory.Packages.props \
  --repository-root . \
  --nuget-config NuGet.Config \
  --target-framework net10.0 \
  --write \
  --write-decision-doc \
  --write-evidence \
  --expected-decision-receipt docs/pkgs-versions/nuget-decision-receipt-<decision-id>.json \
  --metadata-snapshot-input docs/pkgs-versions/nuget-metadata-snapshot-<snapshot-id>.json \
  --validate-repository \
  --audit-repository \
  --report-format markdown
```

`--metadata-snapshot-input` is strict replay. A missing URL fails closed; no network fallback occurs.

If fresh metadata is intentional, omit replay but keep `--expected-decision-receipt`; decision drift blocks the write.

## NuGet.Config and source mapping

Use a repo-owned config when source identity matters:

```text
--nuget-config NuGet.Config
```

The updater binds the exact config SHA-256, reads `packageSources`, and applies `packageSourceMapping` specificity:

1. exact ID;
2. longest matching prefix ending in `*`;
3. `*` fallback.

The updater does not merge the complete NuGet machine/user/repository config hierarchy. If inherited configs materially affect sources, mappings, credentials, audit sources, or trust policy, use a repository-local consolidated config or treat effective-config identity as incomplete.

### Multiple feeds

Without Package Source Mapping:

```text
--source https://api.nuget.org/v3/index.json \
--source https://packages.example.test/v3/index.json
```

Source order remains part of input identity, but it is **not** an authority rule for restore. If the same exact candidate version is observed from multiple eligible sources, default policy rejects it as `candidate-source-ambiguous`.

Prefer Package Source Mapping. `--allow-source-ambiguity` is a diagnostic/risk override only.

The metadata phase supports HTTP(S) NuGet V3 sources. Unsupported local-folder metadata sources fail explicitly rather than being rewritten as URLs.

## Central Package Management guards

The updater intentionally supports literal central versions only.

It fails closed for:

- selected conditional `PackageVersion` declarations;
- duplicate selected `PackageVersion` declarations for one package ID.

It discovers project `VersionOverride` declarations under `--repository-root`; affected packages are skipped with `version-override-active`.

Multiple `Directory.Packages.props` files are recorded in the repository model. The script does not automatically mutate sibling central props files or claim to fully evaluate MSBuild import/condition semantics.

## Candidate metadata policy

NuGet V3 resources used:

- `SearchAutocompleteService`: stable version enumeration;
- `RegistrationsBaseUrl`: listed/deprecation/registration vulnerability metadata;
- `VulnerabilityInfo`: vulnerability ranges where exposed.

Defaults:

- stable only;
- no major upgrade;
- patch/minor allowed;
- no downgrade;
- reject unlisted/deprecated/vulnerable/untrusted candidates;
- reject source ambiguity;
- respect locks/pins;
- validate candidate TFM compatibility.

Diagnostic/test-only risk overrides include:

```text
--allow-deprecated
--allow-vulnerable
--allow-unlisted
--allow-untrusted-metadata
--allow-source-ambiguity
--disable-safety-validation
--disable-restore-validation
```

Do not use them for a normal production update unless the user explicitly requests the altered risk policy.

## Package compatibility probe

The temporary candidate restore is a **package/TFM compatibility probe**, not graph-security proof.

It uses isolated `NUGET_PACKAGES` and `NUGET_HTTP_CACHE_PATH` directories. If `--nuget-config` is present it uses `dotnet restore --configfile <config>` and does not replace config sources with `--source`. Otherwise explicit/default sources are passed with `--source`.

`NuGetAudit` is disabled in this temporary probe deliberately; graph audit belongs to repository validation.

## Repository validation and audit

### Built-in sequence

```text
--validate-repository
```

runs:

```text
restore::dotnet restore
build::dotnet build --no-restore
test::dotnet test --no-build
```

Commands run without a shell from `--repository-root` (or the central props directory when no root is supplied).

### Transitive audit

```text
--validate-repository --audit-repository
```

The audit flag implies validation and configures restore with:

```text
-p:NuGetAudit=true
-p:NuGetAuditMode=all
-p:NuGetAuditLevel=<configured threshold>
```

Interpretation:

- `NU1901` low;
- `NU1902` moderate;
- `NU1903` high;
- `NU1904` critical;
- a warning at/above threshold fails validation;
- `NU1905` fails because audit-source evidence is unavailable;
- `NU1510` is recorded as package-pruning evidence but is non-blocking by itself.

`--audit-repository` cannot be combined with custom validation commands because the updater cannot prove a custom restore preserved the audit contract.

### Custom repository validation

```text
<PYTHON> tools/nuget-updater/nuget_update.py update \
  --file Directory.Packages.props \
  --repository-root . \
  --write \
  --validation-command "restore::dotnet restore My.sln" \
  --validation-command "build::dotnet build My.sln --no-restore" \
  --validation-command "test::dotnet test tests/My.Tests/My.Tests.csproj --no-build"
```

The first failing/timeout/unlaunchable command stops validation and triggers rollback.

## Private feeds and credentials

The Python V3 metadata client does not store or implement credentials. HTTP 401/403 returns `authenticated-source-credentials-required`.

Do not place PATs/passwords/tokens in CLI flags, reports, evidence snapshots, or the skill package. `dotnet restore` may use the machine's standard NuGet credential-provider flow, but metadata discovery must still be established before the updater can select a version.

If signed-package or `trustedSigners` policy matters, configure it in NuGet and require repository restore validation. This script does not implement a second signature-verification stack.

## Evidence options

| Option | Meaning |
|---|---|
| `--write-evidence` | write metadata snapshot plus decision/package receipts |
| `--metadata-snapshot-output <path>` | override metadata snapshot path |
| `--metadata-snapshot-input <path>` | strict replay from captured metadata |
| `--decision-receipt <path>` | override decision receipt path |
| `--expected-decision-receipt <path>` | require current decision identity to match prior receipt |
| `--package-update-receipt <path>` | override package-update receipt path |
| `--last-known-good-dir <path>` | override last-known-good root |
| `--expected-baseline-sha256 <hash>` | pin exact package-file baseline |
| `--repository-root <path>` | root for project/lock-file repository model and validation working directory |
| `--nuget-config <path>` | explicit config identity and Package Source Mapping source |
| `--validate-repository` | built-in restore/build/test after write |
| `--audit-repository` | transitive NuGetAudit gate on the built-in restore |
| `--validation-command label::command` | custom ordered validation; not compatible with audit mode |

## Write and recovery semantics

A changed write uses:

1. baseline hash recheck;
2. output/input alias preflight and validation-command preflight;
3. exact package-file LKG preservation;
4. exact existing `packages.lock.json` snapshot and durable backup;
5. same-directory staged write + fsync + atomic replace;
6. post-write package-file hash verification;
7. requested repository validation/audit;
8. post-validation lock-file identity capture;
9. exact package-file/lock-file rollback on failure;
10. removal of lock files created by the failed validation run.

A second successful run should converge to `writeStatus: no-change` when no newer safe candidate remains.

## Reason codes

Automation should inspect `reason_code`, not free-form `reason`.

```text
package-locked
current-version-nonliteral
metadata-unavailable
authenticated-source-credentials-required
unsupported-nuget-source
source-mapping-no-match
source-mapping-pattern-unsupported
candidate-source-ambiguous
candidate-metadata-missing
candidate-metadata-untrusted
candidate-unlisted
candidate-deprecated
candidate-vulnerable
conditional-package-version-unsupported
duplicate-package-version-declarations
version-override-active
no-safe-candidate
no-policy-allowed-newer-version
safe-update-selected
safe-compatible-update
already-selected
no-compatible-candidate
audit-custom-validation-unsupported
output-aliases-input
output-alias-collision
```

## Optional differential oracles

Where the installed SDK supports them, `dotnet package list` and `dotnet package update` may be used as independent cross-checks. They do not replace the updater's frozen metadata, policy, receipts, or rollback contract. Investigate disagreement instead of choosing whichever result is preferred.

## Exit codes

- `0`: successful run, including no-change;
- `1`: technical/precondition failure;
- `2`: policy failure such as post-write validation/audit failure followed by rollback, or explicit `--fail-on-*` conditions.

## Offline test mode

`--versions-file` exists for deterministic parser/write tests. It does not prove listed/deprecation/vulnerability state, feed provenance, signatures, or the resolved repository graph.

Use only with an explicit test policy such as:

```text
--allow-untrusted-versions-file --disable-restore-validation
```
