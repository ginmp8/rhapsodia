---
name: nuget-package-updater
description: update and validate nuget central package management versions in directory.packages.props for local copilot or chatgpt-assisted dotnet work. use when asked to check, upgrade, modernize, or validate nuget package versions, especially when selecting the latest stable non-prerelease version, rejecting deprecated unlisted or vulnerable versions through nuget v3 metadata, respecting locks/pins, validating target-framework compatibility, and producing reproducible metadata snapshots, decision receipts, package-update receipts, and rollback evidence.
---

# NuGet Package Updater

## Authority

Use the bundled `scripts/nuget_update.py` as the deterministic authority for package discovery, candidate ordering, metadata policy, compatibility decisions, write previews, file mutation, and receipts.

Never manually select a version when the script can decide. Never replace unverified metadata with a guess. Never perform unrelated package upgrades.

Do not use MCP package metadata or MCP-assisted version edits for this workflow. The open NuGet V3 metadata consumed by the script and the repository files are the source evidence.

## Modes

| Mode | Purpose | Writes `Directory.Packages.props` |
|---|---|---|
| `scan` | inventory packages and lock/pin state | no |
| `check` | produce the safe update plan and evidence | no |
| `update` | recompute the plan; writes only with `--write` | only with `--write` |

A prior `check` does not authorize a later write by itself. For a reproducible check→write handoff, use the generated decision receipt as a precondition or replay the exact captured metadata snapshot.

## Required workflow

1. Resolve the exact `Directory.Packages.props` and target framework.
2. Run `scan`.
3. Run `check` with `--write-decision-doc --write-evidence`.
4. Review:
   - baseline SHA-256;
   - target-framework identity;
   - ordered NuGet source identity;
   - lock/pin identity;
   - metadata snapshot identity and timestamp;
   - selected candidate provenance;
   - stable reason codes;
   - write preview;
   - decision receipt.
5. Only when a write was requested, run `update --write` and require the prior decision receipt with `--expected-decision-receipt <receipt.json>`. Prefer `--metadata-snapshot-input <snapshot.json>` when the goal is exact replay of the checked external metadata.
6. For normal repository updates, use `--validate-repository`, or pass explicit ordered `--validation-command label::command` arguments when the repository needs custom restore/build/test commands.
7. Treat any post-write validation failure as a failed update. The script rolls the package file back to the preserved last-known-good bytes.
8. Report the decision document, metadata snapshot, decision receipt, package-update receipt, hashes, validation evidence, and rollback state.

Recommended check:

```bash
python scripts/nuget_update.py check \
  --file Directory.Packages.props \
  --target-framework net10.0 \
  --report-format markdown \
  --write-decision-doc \
  --write-evidence
```

Recommended write after that check:

```bash
python scripts/nuget_update.py update \
  --file Directory.Packages.props \
  --target-framework net10.0 \
  --write \
  --write-decision-doc \
  --write-evidence \
  --expected-decision-receipt docs/pkgs-versions/nuget-decision-receipt-<id>.json \
  --metadata-snapshot-input docs/pkgs-versions/nuget-metadata-snapshot-<id>.json \
  --validate-repository
```

If exact snapshot replay is unavailable, the update may query live metadata again, but `--expected-decision-receipt` must block the write when the resulting decision identity differs.

## Reproducibility contract

### Input identities

Every `check`/`update` report carries:

- exact `Directory.Packages.props` baseline SHA-256;
- target framework plus detected `dotnet` SDK identity;
- ordered normalized NuGet source list and source identity hash;
- lock/pin records and lock/pin identity hash;
- offline versions-file hash when test mode is used.

Before mutation, the script rechecks the package-file hash. If another process or person changed the file during metadata/restore analysis, the write fails with `input-changed-before-write`.

Use `--expected-baseline-sha256` when an external workflow already knows the required package-file baseline.

### NuGet metadata evidence

For live NuGet V3 requests the script captures the decoded JSON response body before semantic analysis and records:

- request URL;
- capture timestamp;
- exact response-body SHA-256;
- canonical JSON SHA-256;
- transport mode (`live` or `replay`).

`--write-evidence` writes a metadata snapshot under `docs/pkgs-versions/`. `--metadata-snapshot-input` replays only URLs present in that snapshot and fails closed on a missing URL; it does not silently fall back to the network.

The metadata snapshot identity excludes timestamps and transport mode, so replay of the same captured bytes retains the same snapshot identity.

### Feed precedence and candidate ordering

Configured `--source` order is part of the input contract. Candidate versions are ordered deterministically by NuGet version. When the exact same version exists in multiple feeds, the first configured feed is authoritative for that version.

Candidate provenance records the selected version, feed, feed index, and normalized metadata hash.

### Stable rejection reasons

Human-readable reasons may contain metadata details, but automation should use `reason_code`. Important codes include:

- `package-locked`;
- `current-version-nonliteral`;
- `metadata-unavailable`;
- `candidate-metadata-missing`;
- `candidate-metadata-untrusted`;
- `candidate-unlisted`;
- `candidate-deprecated`;
- `candidate-vulnerable`;
- `no-safe-candidate`;
- `no-policy-allowed-newer-version`;
- `safe-update-selected`;
- `safe-compatible-update`;
- `already-selected`;
- `no-compatible-candidate`.

Do not scrape free-form `reason` text when `reason_code` is available.

## Safety policy

Preserve these defaults unless the user explicitly requests a diagnostic/test override:

- stable versions only;
- no preview/alpha/beta/rc/dev/nightly candidates;
- no major upgrades unless `--allow-major` is explicit;
- no downgrade unless `--allow-downgrade` is explicit;
- reject unlisted versions;
- reject deprecated versions;
- reject versions with known vulnerabilities at or above the configured threshold;
- require trusted Registration metadata;
- validate compatibility with the requested TFM;
- never update MSBuild property-based versions, wildcards, ranges, or non-literal versions;
- never bypass package locks/pins unless the user explicitly requests an unlock;
- never choose a version manually after metadata, feed, SDK, or restore failure.

When `sdk-does-not-support-target-framework` is reported, do not conclude the package itself is incompatible. The local SDK cannot validate that TFM.

## Atomic write and recovery

Before changing `Directory.Packages.props`, the script produces a write preview with:

- input hash;
- expected output hash;
- exact package/version replacements.

For a real mutation it:

1. verifies the input hash still matches the analyzed baseline;
2. preserves the exact pre-write bytes in `.nuget-updater/last-known-good/` by default;
3. stages the new file in the same directory;
4. fsyncs and atomically replaces the target;
5. verifies the committed hash matches the preview;
6. runs requested repository validation;
7. rolls back to last-known-good if post-write validation fails.

Never delete last-known-good evidence merely to make a failed run look clean.

## Restore/build/test evidence

Candidate TFM compatibility captures `dotnet restore` result kind, exit code, command identity, and output SHA-256.

For repository-level evidence, prefer:

```text
--validate-repository
```

which runs, in order:

```text
restore::dotnet restore
build::dotnet build --no-restore
test::dotnet test --no-build
```

For repositories with custom validation, pass ordered commands explicitly:

```text
--validation-command "restore::dotnet restore My.sln"
--validation-command "build::dotnet build My.sln --no-restore"
--validation-command "test::dotnet test tests/My.Tests/My.Tests.csproj --no-build"
```

Commands run without a shell. Evidence records label, argv, timestamps, exit code/status, and output SHA-256. The first failure stops validation and triggers rollback after a write.

## Receipts

With `--write-evidence`, `check`/`update` produce:

- metadata snapshot: exact external JSON response bodies plus hashes;
- decision receipt: deterministic decision identity bound to input hash, TFM, sources, lock/pin state, metadata snapshot, policy, decisions, and write preview;
- package-update receipt for `update --write`: commit/rollback state, final file hash, validation evidence, and links by hash to the decision/metadata evidence.

Receipt filenames are derived from content identities, not wall-clock timestamps. Receipt payloads include a canonical payload hash.

`--expected-decision-receipt` compares decision identity before any package-file write. Metadata changing between `check` and `update`, policy changes, feed-order changes, TFM changes, lock changes, or package-file changes therefore block the write.

## Decision document

For every real `check` or `update`, pass `--write-decision-doc`. The default filename is derived from `decisionIdentity`, making same-decision reruns converge to the same path.

Use `references/decision-document.md` for the human-readable contract and `references/reproducibility.md` for evidence/receipt semantics.

## Stop conditions

Do not write when any of these holds:

- required metadata cannot be trusted;
- a replay snapshot is incomplete or fails its hash check;
- the expected decision receipt does not match;
- the package-file baseline changed before write;
- a lock/pin blocks the package;
- no safe policy-allowed candidate exists;
- target-framework compatibility cannot be established under the requested policy;
- output paths alias the package file or one another;
- atomic commit or post-write hash verification fails;
- requested restore/build/test validation fails (rollback is required).

Do not reinterpret these failures as permission for a manual version selection.

## Output contract

Summaries should separate:

- **decision evidence**: selected/unchanged/locked/skipped/error packages with stable reason codes;
- **external evidence**: metadata snapshot hash/timestamp/source identity;
- **write evidence**: baseline/output/final hashes and last-known-good path;
- **validation evidence**: restore/build/test statuses and output hashes;
- **recovery evidence**: rollback status when applicable;
- **artifact paths**: decision document, metadata snapshot, decision receipt, package-update receipt.

Never claim validation passed when a command was not executed.

## References

- `references/usage.md`: complete command reference.
- `references/decision-document.md`: decision document fields and interpretation.
- `references/reproducibility.md`: identities, snapshots, receipts, recovery, and rerun rules.
- `references/local-copilot-setup.md`: local Copilot setup.
- `evals/reproducibility-scenarios.json`: frozen regression/edge scenario catalog.
- `scripts/test_nuget_update.py`: preserved baseline smoke evaluator.
- `scripts/test_reproducibility.py`: reproducibility regression evaluator.
- `scripts/validate_evidence.py`: validates snapshot/receipt hashes without external dependencies.
- `schemas/*.schema.json`: machine-readable snapshot and receipt contracts.
- `assets/copilot/nuget-package-updater.instructions.md`: ready-to-copy Copilot instructions.
