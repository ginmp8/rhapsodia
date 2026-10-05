---
name: nuget-package-updater
description: safely update, audit, and validate NuGet Central Package Management versions in Directory.Packages.props with deterministic NuGet V3 evidence, CPM/source guards, compatibility checks, NuGetAudit, receipts, and rollback. use when a repository centrally manages NuGet versions and package updates must be reproducible and fail-closed. do not use for generic PackageReference/csproj edits, package-install advice, or repositories whose effective versions require unsupported MSBuild evaluation. portable core uses repository files, Python 3 stdlib, NuGet V3 HTTP metadata, and dotnet only for runtime validation.
---

# NuGet Package Updater

## Selection and authority

Use this skill for safe NuGet **Central Package Management** updates in `Directory.Packages.props`: discovery, candidate selection, source/config policy, TFM compatibility, repository audit, atomic mutation, receipts, and recovery.

Do not use it to edit ordinary `<PackageReference Version=...>` values, migrate package-management models, choose packages by taste, bypass an unsupported CPM graph, or perform unrelated upgrades.

`scripts/nuget_update.py` is the deterministic authority for the supported static CPM surface. Never manually choose a version to bypass missing/untrusted metadata, source ambiguity, unsupported CPM semantics, active `VersionOverride`, lock/pin policy, failed compatibility, or failed repository validation/audit.

## Modes

| Mode | Use when | Mutation |
|---|---|---|
| `scan` | inventory declarations, locks, overrides, configs, and repository model | none |
| `check` | compute the safe update plan plus evidence | none |
| `update --write` | recompute and commit an authorized plan | `Directory.Packages.props` only, transactionally |

A previous `check` is evidence, not write authority. Bind check -> write with `--expected-decision-receipt`; add `--metadata-snapshot-input` for exact metadata replay. Any decision drift blocks mutation.

## Core rules and invariants

- Default candidate policy is stable-only: no prerelease, major upgrade, downgrade, unlisted, deprecated, vulnerable-at-threshold, untrusted metadata, or ambiguous exact-version source unless the matching diagnostic/test override was explicitly requested.
- Fail closed on selected conditional or duplicate `PackageVersion`, non-literal version expressions, unsupported source mapping/source type, or other static CPM semantics the script cannot prove. An active project `VersionOverride` skips that package.
- With `--nuget-config`, bind the exact config bytes and Package Source Mapping identity. Prefer mapping when multiple feeds are eligible. Never treat configured source order as authoritative for an ID/version present in multiple feeds.
- The metadata client supports HTTP(S) NuGet V3 and does not store credentials. Surface 401/403 as an authentication requirement; never place PATs, tokens, passwords, or credential values in arguments, reports, snapshots, receipts, or skill files.
- Package/TFM compatibility probing is not repository graph proof. For normal writes, use `--validate-repository --audit-repository`; repository validation is `restore -> build --no-restore -> test --no-build` and audit policy is evaluated separately.
- A write is atomic and recoverable: recheck the baseline, preserve exact last-known-good package bytes and existing `packages.lock.json` bytes, commit, validate, and restore/remove lock-file changes if validation fails.
- Keep identities separate: package baseline, TFM+SDK, source/config/mapping, repository model, locks/pins, metadata snapshot, decision, and final update receipt. Timestamps are provenance, not decision identity.
- Treat `reason_code` as the automation contract; free-form `reason` is explanatory only.
- Never claim compatibility, restore/build/test, NuGetAudit, signature trust, graph safety, rollback, or package success unless the corresponding evidence was executed or supplied.
- Portable core must not depend on ChatGPT, Codex, Claude, Copilot, Cursor, MCP, or another vendor-private runtime. Resolve the available Python 3 launcher instead of assuming `python`.
- Stop without writing when required metadata/trust/authentication is unresolved, replay/receipt/baseline identity mismatches, source mapping or source ambiguity is unresolved, CPM semantics are unsupported, a lock/pin or override blocks the package, no safe compatible candidate exists, output paths alias protected inputs, or commit/validation/audit fails.

## Required workflow

1. Resolve the exact `Directory.Packages.props`, repository root, target framework, and available Python 3 launcher; identify any repo-local `NuGet.Config`.
2. Run `scan` to capture declarations, locks/pins, overrides, central props, and lock-file state.
3. Run `check --write-decision-doc --write-evidence`; pass `--nuget-config` when repository-owned config matters.
4. Review baseline/config/repository/metadata identities, source ambiguity, stable reason codes, candidate policy, write preview, and decision receipt.
5. If no write was requested, stop after reporting the check evidence. Never mutate implicitly.
6. If a write was requested, run `update --write` with `--expected-decision-receipt`; prefer `--metadata-snapshot-input` for exact replay.
7. For normal repository changes require `--validate-repository --audit-repository`. Custom `--validation-command label::command` is only for repository-specific validation and is incompatible with the built-in audit contract.
8. If post-write validation fails, treat the update as failed and preserve/report rollback evidence for both package and lock files.
9. Report decision, external metadata, repository model, write, validation/audit, recovery, and artifact evidence as separate layers.

## Quick start

```text
<PYTHON> scripts/nuget_update.py scan --file Directory.Packages.props --repository-root . --target-framework net10.0
<PYTHON> scripts/nuget_update.py check --file Directory.Packages.props --repository-root . --target-framework net10.0 --write-decision-doc --write-evidence
<PYTHON> scripts/nuget_update.py update --file Directory.Packages.props --repository-root . --target-framework net10.0 --write --write-decision-doc --write-evidence --expected-decision-receipt <receipt.json> --metadata-snapshot-input <snapshot.json> --validate-repository --audit-repository
```

Add `--nuget-config NuGet.Config` whenever that explicit repository config is part of the decision. If live metadata is intentionally re-queried during write, keep `--expected-decision-receipt`; drift must still block mutation.

## Direct resource map

- [`references/usage.md`](references/usage.md): command/flag reference, source mapping, CPM guards, candidate policy, validation/audit, credentials, reason codes, and offline test mode.
- [`references/reproducibility.md`](references/reproducibility.md): evidence identities, exact replay, cache isolation, alias safety, last-known-good state, lock-file transaction, audit evidence, and stable reruns.
- [`references/decision-document.md`](references/decision-document.md): human-readable decision-document contract and evidence boundaries.
- [`references/local-copilot-setup.md`](references/local-copilot-setup.md): optional Copilot adapter setup; never required by the portable core.
- `scripts/nuget_update.py`: executable authority; `scripts/test_nuget_update.py`, `scripts/test_reproducibility.py`, `scripts/test_research_improvements.py`, and `scripts/validate_evidence.py`: deterministic regression/evidence validators.
- `schemas/metadata-snapshot.schema.json`, `schemas/decision-receipt.schema.json`, and `schemas/package-update-receipt.schema.json`: machine-readable evidence contracts; `evals/reproducibility-scenarios.json`: planned reproducibility scenarios.

## NuGet source and configuration semantics

### Package Source Mapping

When `--nuget-config` is supplied, bind the exact config bytes into the decision identity and read its `packageSources` plus `packageSourceMapping` sections.

Resolve mapping specificity deterministically:

1. exact package ID;
2. longest matching prefix pattern ending in `*`;
3. `*` fallback.

If mapping resolves no eligible configured source, fail with `source-mapping-no-match`. Unsupported wildcard shapes fail with `source-mapping-pattern-unsupported`.

The metadata client supports HTTP(S) NuGet V3 sources only. Fail with `unsupported-nuget-source` rather than silently reinterpret a local-folder source.

### Source ambiguity

NuGet `PackageReference` restore does not make source order authoritative for an ID/version that exists in multiple eligible feeds. Therefore:

- preserve every observed source for the candidate version in `sourceCandidates`;
- reject multi-source exact-version candidates by default with `candidate-source-ambiguous`;
- prefer Package Source Mapping to remove ambiguity;
- use `--allow-source-ambiguity` only as an explicit diagnostic/risk override, never as the normal production policy.

Do not describe the first configured feed as the authoritative restore source.

### Explicit-config boundary

`--nuget-config` binds and interprets one explicit config file. The Python metadata phase does not recreate NuGet's entire machine/user/repository config hierarchy. When inherited config materially affects sources, mappings, credentials, audit sources, or trust policy, prefer a repository-local consolidated config or treat effective-config identity as not fully proven.

Never emit credential values. The config is represented by hashes and non-secret source/mapping metadata only.

## Central Package Management guards

The updater edits literal `<PackageVersion ... Version="...">` values only. Fail closed rather than guess effective MSBuild behavior:

- selected conditional `PackageVersion` declarations → `conditional-package-version-unsupported`;
- duplicate selected `PackageVersion` declarations for the same package → `duplicate-package-version-declarations`;
- project-level `VersionOverride` for a selected package → skip that package with `version-override-active`;
- non-literal property/range/wildcard version → `current-version-nonliteral`.

The repository model records discovered `Directory.Packages.props` files, relevant `VersionOverride` declarations, and lock files. Multiple central props files are evidence, not permission to rewrite them automatically.

When a repository requires full conditional/import evaluation beyond these guards, use MSBuild/NuGet evaluation outside this script and do not claim the static model proves the effective graph.

## Candidate policy

Preserve these defaults unless the user explicitly requests a diagnostic/test override:

- stable versions only;
- no preview/alpha/beta/rc/dev/nightly candidates;
- no major upgrade unless `--allow-major` is explicit;
- no downgrade unless `--allow-downgrade` is explicit;
- reject unlisted versions;
- reject deprecated versions;
- reject known vulnerabilities at or above `--vulnerability-severity-threshold`;
- require trusted Registration metadata;
- respect lock/pin/manual/no-update markers;
- reject source ambiguity;
- validate TFM compatibility unless explicitly disabled.

The bundled NuGet-version comparator must provide total SemVer-compatible ordering for mixed numeric/alphanumeric prerelease identifiers. Keep regression coverage for numeric-vs-string and prerelease-vs-stable ordering.

## Package compatibility versus repository graph proof

Keep these evidence layers distinct.

### Package-level compatibility probe

Candidate TFM compatibility uses a temporary project and `dotnet restore` with:

- the exact candidate version;
- isolated `NUGET_PACKAGES` and `NUGET_HTTP_CACHE_PATH` directories;
- the explicit `--configfile` when `--nuget-config` is supplied;
- otherwise explicit `--source` values;
- `NuGetAudit=false` because this probe answers package/TFM compatibility, not repository graph security.

Do not treat this probe as proof that the repository's resolved transitive graph is safe.

### Repository validation and audit

`--validate-repository` runs, in order:

```text
restore::dotnet restore
build::dotnet build --no-restore
test::dotnet test --no-build
```

`--audit-repository` implies repository validation and augments restore with `NuGetAudit=true`, `NuGetAuditMode=all`, and the configured severity threshold.

Audit interpretation:

- `NU1901` low, `NU1902` moderate, `NU1903` high, `NU1904` critical;
- a vulnerability warning at/above the configured threshold fails validation;
- `NU1905` fails audit because configured audit evidence is unavailable;
- `NU1510` is recorded as pruning evidence but is non-blocking by itself.

Custom validation commands run without a shell. They are compatible with transactional rollback, but not with `--audit-repository` because the script cannot prove that a custom restore command preserved the required audit contract.

## Authentication and trust

The Python NuGet V3 metadata client does not implement or store credentials. HTTP 401/403 is surfaced as `authenticated-source-credentials-required` and must not be converted to a generic safe-update decision.

`dotnet restore` may use the host's normal NuGet credential-provider/configuration flow. Do not add tokens, passwords, or PATs to CLI arguments, reports, snapshots, or skill files.

Do not implement an ad-hoc package-signature verifier. When signed-package or `trustedSigners` policy is required, configure it in NuGet and use repository restore/validation as the authority. A passing metadata check alone does not prove signature trust.

## Atomic write, lock files, and recovery

Before a real mutation:

1. recheck the analyzed `Directory.Packages.props` hash;
2. validate command syntax and all declared output paths before mutation;
3. preserve exact package-file bytes under `.nuget-updater/last-known-good/`;
4. snapshot existing `packages.lock.json` files with byte SHA-256 and resolved/content-hash identity;
5. persist exact lock-file backup bytes under the last-known-good area;
6. stage and atomically replace the package file;
7. verify the committed file hash;
8. run requested repository validation;
9. capture post-validation lock-file identity;
10. on failure, restore exact package-file and lock-file bytes and remove validation-created lock files.

Output/report/receipt paths must not alias the package file, explicit config, metadata replay input, expected receipt, versions file, lock files, or one another. Decision-document names must be simple `.md` filenames.

Never delete last-known-good or incomplete recovery evidence merely to make a failed run look clean.

## Reproducibility identities

Keep identities separate:

- `Directory.Packages.props` baseline SHA-256;
- target framework + detected SDK identity;
- normalized source/config/mapping identity;
- repository-model identity based on relative repository structure, overrides, and lock identities rather than the absolute machine path;
- lock/pin identity;
- metadata snapshot identity;
- decision identity;
- package-update receipt/final file identity.

`--expected-baseline-sha256` pins the initial package file. `--expected-decision-receipt` pins the recomputed decision before mutation. `--metadata-snapshot-input` is strict replay and never silently falls back to live metadata for a missing URL.

## Evidence and receipts

With `--write-evidence`, emit:

- metadata snapshot: exact decoded NuGet JSON bodies plus hashes;
- decision receipt: input/config/repository/metadata/policy/decision/write-preview identity;
- package-update receipt for `update --write`: commit/no-change/rollback status, final file hash, lock-file before/after evidence, repository validation/audit evidence, and rollback evidence.

Receipt filenames derive from content identities rather than wall-clock time. Receipt payloads include a canonical payload hash.

Human-readable timestamps are provenance, not decision identity.

## Stable reason codes

Automation must inspect `reason_code`, not free-form `reason`. Important codes include:

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

## Optional independent oracles

On SDKs that provide them, `dotnet package list` and `dotnet package update` can be useful independent cross-checks of resolved/outdated/vulnerable package information. Treat them as differential/oracle evidence only; they do not replace this skill's frozen metadata, policy, receipts, or rollback contract.

If the independent oracle materially disagrees with this updater, investigate the mismatch instead of choosing whichever answer is more convenient.

## Stop conditions

Do not write when any required condition is unresolved, including:

- metadata unavailable/untrusted or private-feed authentication unavailable to the metadata phase;
- replay snapshot miss/hash failure;
- expected decision receipt mismatch;
- baseline changes before mutation;
- source mapping failure or unresolved multi-source ambiguity under default policy;
- conditional/duplicate CPM declaration whose effective semantics cannot be proven;
- active `VersionOverride` for that package;
- lock/pin block;
- no safe policy-allowed candidate;
- required TFM compatibility cannot be established;
- output aliases an input/protected file or sibling output;
- atomic commit/hash verification fails;
- repository validation/audit fails, including `NU1905` or a vulnerability at/above threshold.

Do not reinterpret a stop condition as permission for manual package selection.

## Output contract

Summaries must keep evidence layers separate:

- **decision evidence**: update/unchanged/locked/skipped/error with stable codes;
- **external metadata evidence**: snapshot/source/config/mapping identities;
- **repository-model evidence**: central props, overrides, lock-file identities;
- **write evidence**: baseline/preview/final hashes and last-known-good path;
- **validation evidence**: compatibility probe versus repository restore/build/test/audit;
- **recovery evidence**: package and lock-file rollback state;
- **artifact evidence**: decision document, metadata snapshot, decision receipt, package-update receipt.

Never claim a command, audit, graph check, signature policy, or runtime validation passed when it was not executed.

## References

- `references/usage.md`: command reference and examples.
- `references/reproducibility.md`: identity, cache isolation, receipts, lock files, and recovery semantics.
- `references/decision-document.md`: human decision-document contract.
- `references/local-copilot-setup.md`: optional local Copilot adapter setup.
- `evals/reproducibility-scenarios.json`: planned scenario catalog.
- `scripts/test_nuget_update.py`: baseline smoke evaluator.
- `scripts/test_reproducibility.py`: core reproducibility regression evaluator.
- `scripts/test_research_improvements.py`: research-backed regression evaluator for source/config/CPM/audit/recovery controls.
- `scripts/validate_evidence.py`: snapshot/receipt integrity validator.
- `schemas/*.schema.json`: machine-readable evidence contracts.
- `assets/copilot/nuget-package-updater.instructions.md`: optional Copilot instructions.
