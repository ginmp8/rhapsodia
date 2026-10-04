# Reproducibility and recovery contract

## Evidence identities

Keep evidence layers separate:

| Layer | Identity |
|---|---|
| package input | SHA-256 of exact `Directory.Packages.props` bytes |
| target framework | canonical hash of TFM plus detected `dotnet` SDK identity |
| NuGet source/config | normalized sources plus explicit `NuGet.Config` SHA-256 and Package Source Mapping identity |
| repository model | relative central-props paths, relevant `VersionOverride` records, and lock-file identities; absolute repository path excluded from the identity |
| locks/pins | canonical package ID/line/lock/reason records |
| metadata snapshot | canonical source list plus URL/body hashes and optional offline versions-file identity |
| decision | baseline + TFM + source/config/repository/lock identities + metadata snapshot + policy + stable decisions + write preview |
| package update | decision identity plus final package-file, lock-file, validation/audit, and recovery evidence |

Do not reuse one hash as shorthand for a different evidence layer.

## Explicit NuGet.Config boundary

When `--nuget-config` is supplied, its exact bytes are hashed and Package Source Mapping is represented independently. Credential values are never emitted.

This updater does not reconstruct the complete NuGet machine/user/repository config hierarchy. If inherited configuration materially affects semantics, provide a repo-local consolidated config or state that effective-config identity is not fully proven.

## Source ambiguity

Source order remains input evidence but is not restore authority. Exact candidate versions observed from multiple eligible sources are ambiguous and rejected by default.

Package Source Mapping is the preferred control. `--allow-source-ambiguity` is an explicit diagnostic/risk override.

## Metadata snapshot

`--write-evidence` captures decoded NuGet V3 JSON before semantic interpretation. Each record contains URL, capture time, body hash, canonical JSON hash, transport, and exact JSON body.

`--metadata-snapshot-input` is strict replay: missing URLs fail with `metadata-snapshot-miss`; no network fallback is allowed.

Two legitimate check→write patterns are supported:

1. **exact replay** — check live, then write from captured bytes;
2. **fresh verification** — check live, query again during update, but require `--expected-decision-receipt` so decision drift blocks mutation.

Metadata snapshot identity excludes timestamps and live/replay transport mode.

## Compatibility cache isolation

The temporary package/TFM compatibility project uses per-run `NUGET_PACKAGES` and `NUGET_HTTP_CACHE_PATH` paths. This prevents a previously populated global cache from silently changing source-observation and restore behavior during the probe.

When an explicit config is supplied, compatibility restore uses `--configfile`; it does not replace configured sources with `--source`.

This probe has `NuGetAudit=false` intentionally and cannot prove repository transitive security.

## Repository model and CPM safety

Before deciding/writing, capture a repository model containing:

- discovered `Directory.Packages.props` paths relative to `--repository-root`;
- relevant project `VersionOverride` declarations;
- `packages.lock.json` byte/content identities.

Selected conditional or duplicate central version declarations fail closed. Active `VersionOverride` skips the affected package. This removes unsafe text-replacement variance without pretending the script fully evaluates arbitrary MSBuild conditions/imports.

## Preconditions and alias safety

Before mutation:

- input package file must exist;
- expected baseline/decision identities must match when supplied;
- validation-command syntax must be accepted before write;
- immediately before replace, the live package-file hash must still match the analyzed baseline;
- output/report/receipt paths must not alias the package file, explicit config, versions file, metadata replay input, expected receipt, lock files, or one another;
- decision-document names must be simple `.md` filenames.

Canonical/resolved paths are used for alias checks.

## Last-known-good package bytes

The exact package-file bytes are preserved under `.nuget-updater/last-known-good/`, keyed by baseline SHA-256. Preservation and rollback use bytes, not decoded/re-encoded text, so BOM and newline form are retained.

The package mutation itself uses same-directory staging, fsync, and atomic replace. A post-write hash mismatch triggers immediate rollback.

## Lock-file transaction

Before the package-file replace, snapshot each existing `packages.lock.json` under the repository root:

- relative path;
- exact byte SHA-256;
- canonical identity of resolved package/content-hash records where parseable;
- exact backup bytes stored under the last-known-good area.

After repository validation, capture the new lock-file identity. If validation fails:

1. restore exact package-file bytes;
2. restore every pre-existing lock file from its backup;
3. remove `packages.lock.json` files created by the failed validation run;
4. verify the pre-validation lock-file identity was recovered.

If rollback itself cannot be verified, report the rollback failure and preserve recovery files.

## Repository validation and audit evidence

Candidate compatibility evidence and repository evidence are distinct.

Repository validation records command argv, timestamps, exit/status, and output SHA-256. It does not copy raw logs into receipts.

With `--audit-repository`, restore is interpreted for:

- `NU1901`..`NU1904` vulnerability warnings, evaluated against the configured threshold;
- `NU1905`, which is blocking because audit-source evidence is unavailable;
- `NU1510`, recorded as non-blocking pruning evidence.

A zero process exit code does not override a blocking audit diagnostic.

## Authentication/trust boundary

The Python V3 client never stores credentials. HTTP 401/403 is a stable `authenticated-source-credentials-required` diagnostic.

Repository `dotnet restore` may use the host's NuGet credential provider and signed-package/trusted-signer policy. The updater does not duplicate those trust mechanisms; a metadata-policy pass is not signature proof.

## Receipt interpretation

### Decision receipt

`status: planned` means the decision was computed; no mutation is implied. The receipt binds source/config/repository/metadata/policy and write-preview identity.

### Package-update receipt

Important statuses:

- `committed`: mutation remains applied and all requested validation passed;
- `no-change`: recomputation produced no package-file mutation;
- `rolled-back-validation-failure`: write occurred, validation/audit failed, and recovery was attempted.

Inspect `writeEvidence.lockFilesBefore`, `writeEvidence.lockFilesAfterValidation`, and `rollbackEvidence` when lock files are material.

## Stable reruns

For equivalent package bytes, explicit config bytes, relative repository model, metadata snapshot, TFM/SDK, policy, locks, and compatibility outcomes, the semantic decision identity should be stable. Absolute repository location and timestamps are not decision material.

After a successful update, a rerun against the new baseline should normally converge to `no-change`; it legitimately has a different decision identity because the input baseline changed.

## Evidence-layer claim rules

- static/report validation proves structure, not runtime restore success;
- package compatibility does not prove resolved graph safety;
- repository audit does not prove package signature policy unless NuGet actually enforced that configured policy;
- a package receipt proves only the commands/evidence it records;
- unexecuted optional oracles (`dotnet package list/update`) are not validation evidence.
