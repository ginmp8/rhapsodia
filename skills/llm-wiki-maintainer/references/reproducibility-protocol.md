# Reproducibility Protocol

Use this reference for source identity, operational state, idempotency, transactions, recovery, receipts, schema identity, and final freeze. It governs objective mechanics only. It does not replace semantic reading or editorial judgment.

## Reproducibility ceiling

This skill is a **research-analytic workflow with tool-action integrity controls**.

Mechanically reproducible:

- exact source bytes and SHA-256 identity;
- duplicate detection and source aliases;
- immutable captured source snapshots;
- canonical page IDs once a semantic canonical key is chosen;
- frontmatter ordering and normalization for the default schema;
- expected-before hashes, path boundaries, per-file atomic replacement, rollback, and receipts;
- structural provenance/link/schema checks;
- package and final-candidate identity.

Intentionally judgment-bearing:

- which claims are durable;
- entity/concept equivalence;
- which existing pages a source materially affects;
- whether two statements truly conflict;
- authority and scope comparison between sources;
- whether a conflict is superseded or unresolved;
- what a cross-source synthesis should conclude or emphasize.

Never convert those semantic decisions into filename heuristics, keyword counts, or hash rules merely to make output look deterministic.

## Operational state

For a wiki using the reproducibility controls, reserve this derived operational state:

```text
.llm-wiki/
  source-manifest.json
  source-snapshots/
    <sha256>/content
  receipts/
    ingest/
    mutation/
    lint/
  recovery/
    <transaction-id>/before/
```

`.llm-wiki/` is derived operational metadata/evidence. It is not source truth and must never be used as a substitute for semantic source reading. Captured `source-snapshots/` are exact source-evidence bytes and become immutable after capture.

Do not put generated wiki prose into `source-snapshots/`.

## Source identity and ingest manifest

Canonical source identity is content-addressed:

```text
source_id = sha256:<64 lowercase hex digits of exact source bytes>
```

Consequences:

- the same bytes at the same filename produce the same `source_id`;
- the same bytes at a different filename are a duplicate-content alias, not a new source;
- different bytes at a previously registered path are an external source mutation, never a silent update;
- timestamps, filenames, absolute paths, and host identity never participate in `source_id`.

Before semantic ingestion, run the source-identity helper when filesystem execution is available:

```text
<PYTHON> scripts/source_identity.py capture --workspace <ROOT> --source <ROOT>/raw/<FILE> --json <INGEST_RECEIPT>
```

The helper:

1. verifies the source is inside the declared workspace source boundary;
2. hashes the exact bytes;
3. captures an immutable local snapshot under `.llm-wiki/source-snapshots/`;
4. detects reingestion and duplicate-content aliases;
5. blocks a known path whose bytes changed unless the user explicitly authorizes treating that external replacement as a new source version;
6. atomically updates `source-manifest.json`;
7. emits a machine-readable ingest receipt.

The helper never edits the raw source.

If a host cannot execute the helper, preserve the same semantic contract with the strongest available source-byte identity. Mark hash/snapshot gates `not-run`; do not claim strong reproducibility without equivalent evidence.

### Externally changed or removed sources

A source changed outside the skill is not proof the old source was wrong. Preserve the old snapshot and `source_id`.

- **Changed bytes at known path:** classify `source-modified`; block automatic reingest. With explicit authorization, register the new bytes as a new `source_id` and preserve `previous_source_id`/supersession context.
- **Missing raw path:** retain the source record and immutable snapshot; mark raw-path availability as missing. Do not delete derived knowledge automatically.
- **Missing/corrupt snapshot:** hard integrity failure for claims relying on that captured snapshot until repaired from an independently verified copy.

Use:

```text
<PYTHON> scripts/source_identity.py verify --workspace <ROOT> --json <SOURCE_VERIFY_RECEIPT>
```

## Canonical page identity

Page identity has two layers:

1. **semantic canonical key** — chosen with model/human judgment, such as the actual entity identity or concept meaning;
2. **mechanical page ID** — deterministically derived from that key.

Use:

```text
<PYTHON> scripts/page_identity.py id --type entity --key <CANONICAL_KEY>
```

For source summaries, the key is the exact `source_id`, so source-summary page identity is fully mechanical. For entity/concept/synthesis pages, the helper does not decide whether two meanings are equivalent; it only makes the chosen key stable.

A rename for display reasons does not require a new `page_id`. A true semantic identity change does; represent it as migration/supersession rather than silently reusing the old ID.

## Deterministic frontmatter

The default schema uses canonical key order and sorted/deduplicated list fields. Prefer the helper:

```text
<PYTHON> scripts/page_identity.py render-frontmatter --metadata <META.json> --body <BODY.md> --out <STAGED_PAGE.md>
```

Identity/provenance fields for the default schema:

```text
wiki_schema_version
page_id
page_type
title
canonical_key
source_ids
source_paths
reviewed_source_ids
conflict_ids
status
supersedes_page_ids
```

Date fields may follow these fields when the active schema requires them. Dates are operation metadata, not identity inputs. Idempotent reingestion must not rewrite a page merely to change an ingest/update date.

## Source-to-page and page-to-source provenance

Every maintained factual page must expose `source_ids`. Source-summary pages have exactly one canonical source ID. Entity, concept, and synthesis pages list the source IDs materially supporting their maintained content.

During ingest, record both directions:

- from the ingest result: which `page_id` values were created or materially updated because of the source;
- on each changed page: the source IDs the page currently relies on and the source IDs included in its last semantic review.

A generated page can point to another generated page for navigation, but its evidence chain must terminate in source IDs. Generated pages never become source truth merely through repeated citation.

## Conflicts

Conflict representation must be explicit and lossless.

For each material conflict:

- identify the conflicting proposition or decision frame;
- retain each competing claim separately;
- list the supporting `source_id` values for each side;
- distinguish `unresolved`, `superseded`, or `scope-different` only after source review;
- keep the reason for any supersession visible.

A deterministic `conflict_id` may be derived after the semantic conflict subject/key and participating source IDs are fixed. The helper does not decide the conflict subject or winner.

Never discard one side merely because another statement is newer, smoother, or more plausible.

## Stale-claim detection

Separate mechanical candidates from semantic conclusions.

Mechanical checks may flag:

- a referenced source ID missing from the manifest;
- source-path hash drift;
- a page whose declared `source_ids` are not all present in `reviewed_source_ids`;
- a page linked from a newly ingested source but not yet semantically reviewed, when that relationship was explicitly recorded;
- broken provenance/link/index structure.

A `semantic/stale-candidate` finding means **review needed**, not "claim is false". Determining whether the claim is stale requires reopening the relevant source evidence and comparing version, date, scope, authority, and applicability.

## Recovery-aware wiki mutation

Do not write a broad multi-page mutation directly into the live wiki.

1. Read current target bytes and record SHA-256 preconditions.
2. Render the complete candidate mutation into a private staging directory that mirrors workspace-relative paths.
3. Validate the staged content and source identity.
4. Create a versioned mutation plan using `schemas/mutation-plan.schema.json`.
5. Commit with:

```text
<PYTHON> scripts/wiki_transaction.py commit --workspace <ROOT> --staging <STAGE> --plan <PLAN.json> --json <MUTATION_RECEIPT>
```

The transaction helper:

- accepts writes only to `WIKI_SCHEMA.md` and `wiki/**`;
- rejects raw-source and path-escape writes;
- blocks overwrite when current bytes differ from the recorded precondition hash;
- uses atomic replacement for each file;
- preserves last-known-good bytes under `.llm-wiki/recovery/`;
- automatically rolls back already-touched files when a commit fails;
- detects a rerun whose exact outputs are already applied;
- emits a machine-readable mutation receipt tied to exact before/after hashes.

A portable filesystem cannot guarantee one atomic rename for an arbitrary multi-file tree across all hosts. The contract is therefore **atomic per file plus recovery-aware transaction semantics** for the mutation set. Never describe it as a database-style atomic transaction.

### Manual wiki edits

Human/manual changes to derived wiki pages are allowed. They are not source truth, but they must not be overwritten silently.

If an expected-before hash no longer matches:

- classify the page as manual/concurrent drift;
- preserve the current page untouched;
- re-read the manual edit;
- merge semantically when appropriate;
- regenerate the staged candidate from the new current hash;
- rerun validation and commit.

Do not use `--force`-style overwrite as a default escape hatch.

### Rollback

For a successful transaction whose recovery snapshot is still present:

```text
<PYTHON> scripts/wiki_transaction.py rollback --workspace <ROOT> --receipt <MUTATION_RECEIPT> --json <ROLLBACK_RECEIPT>
```

Rollback itself is preconditioned on the committed bytes still being current. If later edits exist, rollback blocks rather than deleting them.

## Structural validation and lint receipt

Run:

```text
<PYTHON> scripts/wiki_validate.py --workspace <ROOT> --strict --json <LINT_RECEIPT>
```

The receipt separates:

- `structural_evidence`: source/snapshot integrity, schema identity, page metadata, provenance IDs, links, index/log structure;
- `semantic_editorial_judgment`: stale candidates, conflict-review candidates, or other findings that require source interpretation.

A structural pass does not prove factual correctness or editorial quality.

## Schema version and migration contract

For new wikis using the default protocol, set:

```text
schema_version: llm-wiki/2
```

Do not force that version onto an existing coherent wiki merely because this skill was upgraded. Existing wikis retain their schema until migration is explicitly authorized or required for a requested operation.

Every incompatible schema change must define:

- current schema identity;
- target schema identity;
- compatibility statement;
- affected page types/fields;
- deterministic mechanical transforms, if any;
- semantic review required, if any;
- rollback point/last-known-good identity;
- validation commands and success criteria.

Migration order:

`freeze current -> update WIKI_SCHEMA.md in staging -> migrate only affected derived pages -> validate staged candidate -> commit transaction -> lint -> freeze new state`

Never reinterpret old pages under a new schema without an explicit migration.

## Final freeze

A wiki operation is complete only when:

1. source identity/snapshot checks are satisfied or honestly marked unavailable;
2. semantic edits were based on raw evidence rather than generated prose alone;
3. mutation receipt describes the exact committed bytes;
4. structural validation has no hard failure;
5. unresolved semantic findings remain visible;
6. no post-validation edit occurred.

Any edit after the final pass reopens validation for the affected operation.
