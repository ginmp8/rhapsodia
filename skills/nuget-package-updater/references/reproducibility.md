# Reproducibility and recovery contract

## Evidence identities

The updater keeps different evidence layers separate:

| Layer | Identity |
|---|---|
| package input | exact SHA-256 of `Directory.Packages.props` bytes |
| target framework | canonical hash of TFM plus detected `dotnet` SDK identity |
| NuGet sources | canonical hash of normalized source URLs in configured order |
| locks/pins | canonical hash of package ID, line, lock flag, and lock reason records |
| metadata snapshot | canonical hash of source list plus URL/body hashes and offline versions-file hash |
| decision | canonical hash of baseline, TFM, source/lock identities, metadata snapshot, policy, stable package decisions, and write preview |
| package update | receipt tied to decision identity plus final package-file hash and validation/recovery evidence |

Do not substitute one identity for another.

## Metadata snapshot

`--write-evidence` captures the decoded JSON bytes returned by NuGet V3 before the response is interpreted. Each record contains its URL, capture time, body hash, canonical JSON hash, transport, and exact JSON body.

`--metadata-snapshot-input` is strict replay. A URL missing from the snapshot is `metadata-snapshot-miss`; network fallback is forbidden in replay mode.

This enables two legitimate write patterns:

1. **Exact replay**: check live → write with the captured snapshot. External metadata cannot drift because the update reads the checked bytes.
2. **Fresh verification**: check live → update live again with `--expected-decision-receipt`. A changed decision identity blocks the write.

## Preconditions

Before mutation:

- package file must exist;
- `--expected-baseline-sha256`, when supplied, must match;
- `--expected-decision-receipt`, when supplied, must match the newly recomputed decision identity;
- immediately before replace, the live package-file hash must still match the analyzed baseline;
- sidecar outputs must not alias the package file or one another.

## Last-known-good and rollback

For a changed file, the exact pre-write content is preserved under `.nuget-updater/last-known-good/` using a filename that includes its SHA-256. Existing LKG content is reused only when its hash matches the expected baseline.

The package update uses same-directory staging and atomic replace. If post-write hash verification fails, rollback is immediate. If requested repository validation fails, rollback is also immediate.

A failed atomic replace leaves the original target intact. LKG evidence is retained.

## Validation evidence

Candidate compatibility evidence and repository validation evidence are distinct.

Candidate compatibility records the selected candidate's TFM restore result. Repository validation is only present for commands actually executed after a write. `--validate-repository` is shorthand for restore/build/test in that order.

Output is represented by SHA-256 in receipts rather than copied verbatim, reducing accidental secret/log exposure while still binding the result to exact observed bytes.

## Receipt interpretation

### Decision receipt

Status `planned` means the decision is computed; it does not mean a write occurred. `decisionIdentity` is the precondition key for a later write.

### Package-update receipt

Important statuses:

- `committed`: package file committed and all requested post-write validation passed;
- `no-change`: recomputation produced no package-file mutation;
- `rolled-back-validation-failure`: a package-file write was attempted but requested validation failed and the original bytes were restored.

A package-update receipt contains the final file hash. Confirm it before claiming the mutation remains applied.

## Stable reruns

Rerunning with the same package bytes, metadata snapshot, TFM, source order, policy, locks, and compatibility outcomes should produce the same semantic decision identity. Timestamps and live/replay transport mode are not part of metadata snapshot identity.

After a successful update, a rerun against the new package-file baseline should normally converge to `no-change`; that is a new decision identity because the input baseline legitimately changed.
