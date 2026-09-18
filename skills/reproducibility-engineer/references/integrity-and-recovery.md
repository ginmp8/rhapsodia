# Integrity and Recovery Contract

## Purpose

Make evidence and delivery trustworthy even when files, repositories, paths, or outputs can change underneath the workflow. Reproducibility is weakened if the bytes inspected are not the bytes evaluated, if an output aliases an input, or if a failed commit destroys the last-good artifact.

## 1. Snapshot evidence before analysis

When external files or repository content materially determine a transformation or acceptance decision, capture the exact bytes first and analyze the snapshot rather than repeatedly reopening the live source.

Preferred sequence:

`resolve source -> capture exact bytes -> hash -> record provenance -> analyze snapshot -> verify identity before acceptance`

Use `scripts/snapshot_sources.py` for filesystem evidence when available:

```text
<PYTHON> scripts/snapshot_sources.py capture \
  --root <SOURCE_ROOT> \
  --path <RELATIVE_SOURCE> \
  --snapshot-dir <WORK>/source-bytes \
  --out <WORK>/source-manifest.json
```

Before final acceptance:

```text
<PYTHON> scripts/snapshot_sources.py verify \
  --manifest <WORK>/source-manifest.json \
  --json <WORK>/source-verification.json
```

A source that changes after capture invalidates claims tied to the original live source. Re-baseline intentionally instead of silently mixing versions.

## 2. Pinned repository evidence must mean immutable repository evidence

When evidence is attributed to a VCS revision, read the immutable object identified by that revision when the host supports it. Do not assume the current working tree represents the pinned revision.

For Git-backed evidence:

- record repository identity, revision SHA, path, and relevant range;
- prefer object-database reads such as `git show <sha>:<path>` or equivalent over reading the working tree;
- do not let local replacement refs, dirty files, or branch movement silently redefine a pinned revision;
- if the runtime cannot bypass replacement/ref rewriting, record that limitation and downgrade the evidence claim;
- verify that links or citations refer to the same recorded revision.

The goal is not Git-specific behavior. The general rule is that a stable source identifier must resolve to stable source bytes.

## 3. Canonicalize output paths before mutation

Validate both the authored path and its resolved destination before writing.

Check, where applicable:

- required output type/extension before writing;
- required extension again after symbolic links are resolved;
- output does not alias any input, evaluator, protected file, or sibling receipt;
- multiple outputs do not alias one another;
- relative outputs remain inside their allowed root after canonicalization;
- symbolic-link cycles fail closed;
- existing last-good bytes remain untouched on preflight or validation failure.

Alias means more than identical strings. Treat symbolic links, canonical paths, and same-file identity as possible aliases. Case/Unicode-normalization aliases should also be considered on filesystems where they matter.

## 4. Commit multiple outputs as one recovery-aware transaction

When one action publishes an artifact plus sidecars/receipts, preflight every target before committing any of them.

Preferred sequence:

1. write all candidates privately;
2. validate every candidate;
3. compute hashes and receipts from those exact staged bytes;
4. preserve existing targets as backups;
5. commit staged outputs;
6. remove backups only after all commits succeed;
7. if commit fails, restore the previous outputs;
8. if rollback itself fails, preserve recovery files and report exact backup-to-target paths.

Do not delete recovery evidence merely to leave a clean directory.

## 5. Receipts are durable evidence, not decoration

Machine-readable receipts should remain parseable and complete under pipes, large payloads, and process termination.

A useful failure or success receipt includes:

- `receipt_version`;
- `status`;
- `stage`;
- stable diagnostic `code` when available;
- exact `subject`;
- observed `evidence`;
- `supported_fixes` when repair choices are bounded;
- hashes/identities for source and artifact when material;
- recovery paths when rollback is incomplete.

For file receipts, prefer same-directory staging, flush/fsync, and atomic replace. For stdout receipts, flush the complete serialized payload before exit. Never emit a success receipt before the artifact it describes is committed.

## 6. Keep evidence identities separate

Record separately:

- live source identity;
- captured source/snapshot identity;
- evaluator identity;
- candidate tree identity;
- delivered artifact/package identity;
- receipt identity when the receipt is persisted.

One hash must not be reused as shorthand for a different evidence layer.

## Acceptance implications

Fail or restart the experiment when:

- source bytes change after a frozen source snapshot and the comparison depends on those bytes;
- a pinned revision cannot be resolved to stable bytes but the report claims immutability;
- an output aliases an input/protected path/receipt;
- a failed delivery overwrites the last-good output;
- a receipt is truncated, unparsable, or refers to bytes different from the committed artifact;
- rollback is incomplete and recovery locations are not preserved/reported.
