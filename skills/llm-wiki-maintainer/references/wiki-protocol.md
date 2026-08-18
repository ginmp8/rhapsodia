# Wiki Protocol

Use this reference for concrete structure and page-maintenance rules.

## Default Structure

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
```

The root may differ when an existing wiki already has coherent conventions. Preserve existing names and folders unless the user asks to migrate them.

## `WIKI_SCHEMA.md` Contract

For a new wiki, define:

- purpose and domain of the wiki;
- raw-source boundary and read-only rule;
- wiki writable boundary;
- page types and their directories;
- filename convention;
- link style;
- required provenance fields;
- date format;
- index organization;
- log entry format;
- ingest, query, lint, and schema-change workflows;
- rules for contradictions and superseded claims;
- any domain-specific metadata the user actually needs.

Prefer concise rules that change behavior. Do not turn the schema into a duplicate of the entire skill.

## Page Contracts

### Source summary

Store under `wiki/sources/` unless the active schema says otherwise.

Include:

- title;
- immutable source path or source identifier;
- source date when available;
- ingest date;
- concise summary;
- key claims or observations;
- limitations or uncertainty;
- related entity, concept, and synthesis links;
- open questions.

A source-summary page is derived navigation, not a replacement for the raw source.

### Entity page

Store durable knowledge about a person, organization, product, place, system, project, or other stable subject.

Include:

- concise current description;
- accumulated synthesis grouped by useful topics;
- supporting raw sources or source-summary links with raw provenance;
- conflicting or superseded claims when relevant;
- related concepts and entities;
- last material update.

Update an existing entity page when the entity already exists. Do not create spelling variants as separate entities without a real identity distinction.

### Concept page

Use for durable themes, methods, ideas, mechanisms, patterns, or recurring topics that span sources.

Include:

- definition in the wiki's domain;
- current synthesis;
- supporting and counterevidence;
- related entities and concepts;
- open questions or unresolved edges;
- provenance.

### Synthesis page

Use when a query or analysis produces durable cross-source knowledge worth retaining.

Include:

- question or decision frame;
- synthesized answer;
- supporting evidence;
- counterevidence or competing interpretations;
- unresolved uncertainty;
- raw-source provenance;
- related maintained pages;
- creation and last-update dates.

Do not persist routine chat answers, transient calculations, or restatements that add no durable knowledge.

## `wiki/index.md`

Treat the index as content-oriented navigation, not a chronological history.

For each maintained page, keep:

- link;
- one-line description;
- optional date or source count when useful.

Group entries by the wiki's domain or page types. Update the index during every ingest that creates or materially changes pages and during migrations that rename or move pages.

When querying, inspect the index before scanning broad parts of the wiki.

## `wiki/log.md`

Treat the log as append-only operational history. Never rewrite older entries merely to make the past match the current state.

Use a parseable heading pattern:

```text
## [YYYY-MM-DD] <operation> | <subject>
```

Recommended operation values:

- `initialize`
- `ingest`
- `query-persist`
- `lint`
- `schema-change`

Each entry should state the raw source or question, pages changed, major contradictions or gaps, and validation outcome.

## Ingest Update Algorithm

For each source:

1. read the raw source;
2. identify durable claims, entities, concepts, relationships, dates, and limitations;
3. inspect the index for existing pages;
4. create or update the source-summary page;
5. revise existing entity and concept pages affected by the new evidence;
6. create only genuinely missing durable pages;
7. preserve conflicts and supersession explicitly;
8. add useful reciprocal links;
9. update the index;
10. append one log entry;
11. validate schema, provenance, and links.

A single source may legitimately update many wiki pages. Do not limit the update to one summary page when the new evidence changes existing accumulated knowledge.

## Query Persistence Rule

Persist a query result only when all are true:

- the analysis is likely to be useful beyond the current turn;
- it synthesizes multiple maintained pages or raw sources, or creates a meaningful new connection;
- the conclusion is sufficiently grounded to survive outside chat context;
- wiki mutation is authorized.

Otherwise answer in chat without creating a page.

## Batch Ingest

Default to one source at a time for maximum reviewability. When batch ingest is explicitly requested:

- keep a separate source-summary page for each source;
- keep separate provenance on every derived claim;
- append one log entry per source or clearly separable per-source subentries;
- avoid collapsing conflicting sources into one statement without preserving disagreement;
- validate incrementally so a later source cannot obscure an earlier failure.
