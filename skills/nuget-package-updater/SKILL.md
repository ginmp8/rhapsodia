---
name: nuget-package-updater
description: update, audit, and validate NuGet Central Package Management versions in Directory.Packages.props with reproducible evidence. use for safe .NET package upgrades, NuGet.Config and Package Source Mapping, stable non-prerelease selection, deprecated/unlisted/vulnerable package rejection, CPM locks and VersionOverride guards, TFM compatibility, transitive NuGetAudit, packages.lock.json recovery, decision receipts, metadata snapshots, and atomic rollback. portable across agent hosts because the core depends only on repository files, Python 3 stdlib, NuGet V3 HTTP metadata, and the dotnet CLI when runtime validation is requested.
---

# NuGet Package Updater

## Authority and scope

Use `scripts/nuget_update.py` as the deterministic authority for package discovery, candidate ordering, metadata policy, compatibility probes, write previews, mutation, receipts, and recovery.

Never manually select a version when the script can decide. Never turn missing metadata, ambiguous source provenance, unsupported CPM semantics, or failed restore/audit evidence into permission to edit a package version manually. Never perform unrelated upgrades.

The portable core must not depend on ChatGPT, Codex, Claude, Copilot, Cursor, MCP, or another vendor-private runtime. `agents/openai.yaml` and `assets/copilot/` are optional host adapters only. Resolve the available Python 3 launcher (`python`, `python3`, `py -3`, or equivalent) instead of assuming one spelling.

## Modes

| Mode | Purpose | Writes `Directory.Packages.props` |
|---|---|---|
| `scan` | inventory selected declarations, locks, repository model, and overrides | no |
| `check` | compute the safe update plan and evidence | no |
| `update` | recompute the plan; mutate only with `--write` | only with `--write` |

A prior `check` never authorizes a later write by itself. Bind check→write with `--expected-decision-receipt`; use `--metadata-snapshot-input` when exact replay of checked NuGet metadata is required.

## Required workflow

1. Resolve the exact `Directory.Packages.props`, target framework, and repository root.
2. If the repository uses a repo-local `NuGet.Config`, pass it explicitly with `--nuget-config`. Prefer Package Source Mapping when multiple feeds exist.
3. Run `scan`.
4. Run `check --write-decision-doc --write-evidence`.
5. Review:
   - package-file baseline SHA-256;
   - target-framework and detected SDK identity;
   - NuGet source identity;
   - explicit `NuGet.Config` SHA-256 and Package Source Mapping identity when supplied;
   - repository-model identity, `VersionOverride` evidence, locks/pins, and lock-file identity;
   - metadata snapshot identity;
   - candidate provenance and source ambiguity;
   - stable reason codes and write preview;
   - decision receipt.
6. Only when a write was requested, run `update --write` and require the checked decision receipt. Prefer exact metadata replay.
7. For normal repository updates, use `--validate-repository --audit-repository`. Use custom `--validation-command label::command` only when repository-specific commands are necessary; `--audit-repository` intentionally requires the built-in validation sequence.
8. Treat any post-write validation failure as a failed update. The script restores the exact package-file bytes and pre-validation `packages.lock.json` state, including removing lock files created by the failed validation run.
9. Report decision, metadata, write, validation/audit, recovery, and receipt evidence separately.

Recommended check:

```text
<PYTHON> scripts/nuget_update.py check \
  --file Directory.Packages.props \
  --repository-root . \
  --nuget-config NuGet.Config \
  --target-framework net10.0 \
  --report-format markdown \
  --write-decision-doc \
  --write-evidence
```

Omit `--nuget-config` when the repository intentionally uses only the default nuget.org source or explicit `--source` arguments.

Recommended write after the check:

```text
<PYTHON> scripts/nuget_update.py update \
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
  --audit-repository
```

If live metadata is intentionally re-queried, keep `--expected-decision-receipt`; any decision drift must block the write.

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
