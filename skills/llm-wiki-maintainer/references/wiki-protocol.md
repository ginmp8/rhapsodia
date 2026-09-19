# Wiki Protocol

Use this reference for concrete structure, page contracts, naming, index/log behavior, and operation sequencing. Load `reproducibility-protocol.md` whenever ingestion or mutation needs stable identities, receipts, recovery, migration, or rerun guarantees.

## Default Structure

For a new wiki:

```text
WIKI_SCHEMA.md
raw/
  assets/              # optional; source attachments only
wiki/
  index.md
  log.md
  sources/
  entities/
  concepts/
  syntheses/
.llm-wiki/             # derived operational state; created only when needed
```

The root may differ when an existing wiki already has coherent conventions. Preserve existing names and folders unless the user authorizes migration.

`raw/` is immutable source truth. `wiki/` and `WIKI_SCHEMA.md` are derived maintained state. `.llm-wiki/` is operational evidence/state and never source truth.

## `WIKI_SCHEMA.md` Contract

For a new wiki, define at least:

- `schema_version: llm-wiki/2`;
- purpose and domain of the wiki;
- raw-source boundary and read-only rule;
- wiki writable boundary;
- page types and their directories;
- filename convention and canonical page-ID rule;
- link style;
- required provenance fields;
- date format when dates are used;
- index organization;
- log entry format;
- ingest, query, lint, rollback, and schema-change workflows;
- rules for contradictions, superseded claims, and stale-review candidates;
- any domain-specific metadata that materially changes behavior.

Do not duplicate the full skill inside the schema. Preserve an existing coherent schema unless migration is explicit.

## Canonical frontmatter for the default schema

For new default-schema pages, use deterministic frontmatter ordering from `scripts/page_identity.py`. Core fields are:

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

List fields are sorted and deduplicated mechanically. The semantic `canonical_key`, title, source relevance, conflict meaning, and prose remain judgment-bearing.

A page filename is a navigation choice, not its identity. Preserve `page_id` across display-title or filename changes when semantic identity is unchanged.

## Page Contracts

### Source summary

Store under `wiki/sources/` unless the active schema says otherwise.

Require:

- one `page_id` derived from the exact `source_id`;
- exactly one canonical `source_id` plus any observed source-path aliases;
- title;
- source date when available;
- ingest context/date when useful, without making it part of identity;
- concise summary;
- key claims or observations;
- limitations or uncertainty;
- related entity, concept, and synthesis links;
- open questions.

A source-summary page is derived navigation. It never replaces the raw source or its immutable captured snapshot.

### Entity page

Store durable knowledge about a person, organization, product, place, system, project, or other stable subject.

Include:

- stable `page_id` derived from a chosen canonical entity key;
- concise current description;
- accumulated synthesis grouped by useful topics;
- supporting source IDs and raw provenance;
- `reviewed_source_ids` representing the source set included in the latest semantic review;
- conflicting or superseded claims when relevant;
- related concepts and entities;
- last material update when useful.

Update an existing entity page when semantic identity is the same. Do not create spelling variants as separate entities without a real identity distinction.

### Concept page

Use for durable themes, methods, ideas, mechanisms, patterns, or recurring topics that span sources.

Include:

- stable `page_id` from a canonical concept key;
- definition in the wiki's domain;
- current synthesis;
- supporting and counterevidence with source IDs;
- reviewed source set;
- related entities and concepts;
- open questions or unresolved edges.

### Synthesis page

Use when a query or analysis produces durable cross-source knowledge worth retaining.

Include:

- stable `page_id` from a canonical synthesis/decision-frame key;
- question or decision frame;
- synthesized answer;
- supporting evidence;
- counterevidence or competing interpretations;
- unresolved uncertainty;
- raw-source IDs/provenance;
- reviewed source set;
- related maintained pages;
- creation/update dates only when the schema uses them.

Do not persist routine chat answers, transient calculations, or restatements that add no durable knowledge.

## Conflict representation

Do not flatten conflicting evidence into one smooth paragraph.

A maintained conflict should preserve:

- the proposition/frame in dispute;
- each competing claim separately;
- source IDs supporting each claim;
- status: `unresolved`, `superseded`, or `scope-different` only after evidence review;
- rationale for supersession when used;
- a stable conflict identifier once the semantic conflict key is fixed.

## `wiki/index.md`

Treat the index as content-oriented navigation, not chronological history.

For each maintained page, keep a link and one-line description; optional source count/date is allowed when useful. Update the index during every operation that creates, renames, removes, or materially changes a maintained page.

When querying, inspect the index before broad traversal.

## `wiki/log.md`

Treat the log as append-only operational history. Never rewrite older entries merely to make past operations match the current state.

Use:

```text
## [YYYY-MM-DD] <operation> | <subject>
```

Operation values:

- `initialize`
- `ingest`
- `query-persist`
- `lint`
- `schema-change`

Each entry states the source/question, pages changed, material conflicts/gaps, validation outcome, and receipt/transaction ID when one exists. The log is human-readable history; machine receipts under `.llm-wiki/receipts/` carry exact hashes.

## Ingest Update Algorithm

For each source:

1. capture/verify exact source identity and immutable snapshot when the runtime supports it;
2. detect same-source reingestion, duplicate-content aliases, source-path mutation, and missing prior source state before semantic work;
3. read the raw source/snapshot and identify durable claims, entities, concepts, relationships, dates, and limitations;
4. inspect the index and canonical page identities for existing maintained subjects;
5. create/update the source-summary page;
6. revise existing entity/concept/synthesis pages only when the new evidence materially affects them;
7. create only genuinely missing durable pages;
8. preserve conflicts and supersession explicitly;
9. record source-to-page and page-to-source provenance;
10. stage the full derived mutation, including index and log changes;
11. validate staged structure/provenance;
12. commit with hash preconditions and recovery-aware transaction semantics;
13. run strict structural validation/lint and retain the receipts;
14. freeze the completed operation.

A single source may update many pages. Do not limit an ingest to one summary when accumulated knowledge materially changes.

### Idempotent reingestion

If the exact source ID and schema were already ingested and no semantic dependency changed, do not rewrite pages or log a fictitious update. Return the prior identity plus a new or reused receipt classification such as `already-ingested` and report that no derived mutation was needed.

If the same source bytes appear under a second filename, add the path as an alias without duplicating the source-summary identity.

## Query Persistence Rule

Persist a query result only when all are true:

- likely reusable beyond the current turn;
- combines multiple maintained pages/raw sources or creates a durable new connection;
- sufficiently grounded to survive outside chat context;
- mutation is authorized.

Persist through the same staged/validated/receipt-backed mutation path. Otherwise answer in chat without changing the wiki.

## Batch Ingest

Default to one source at a time for reviewability. For an explicit batch:

- identify/snapshot every source independently;
- keep one source-summary identity per unique source ID;
- preserve duplicate aliases without duplicate source pages;
- keep per-source provenance and ingest receipts separable;
- append one log entry per source or clearly separable subentries;
- validate incrementally;
- if one source fails, retain last-known-good state and exact failure/recovery evidence rather than claiming the whole batch succeeded.
