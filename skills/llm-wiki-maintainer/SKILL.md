---
name: llm-wiki-maintainer
description: 'use when the user wants to build or operate a persistent llm-maintained markdown wiki that compounds knowledge across sources over time: initialize the workspace, ingest immutable source material, update entity, concept, source-summary, or synthesis pages, maintain index.md and log.md, answer cross-source questions with provenance, persist durable syntheses, or lint the wiki for contradictions, stale claims, orphans, gaps, and broken cross-links. do not use for one-off document summarization, ordinary rag or search, generic note-taking, or workflows that mutate raw sources or treat generated wiki pages as source truth.'
---

# LLM Wiki Maintainer

## Mission

Build and maintain a persistent Markdown knowledge base in which raw sources remain immutable source truth and the LLM incrementally maintains a structured, interlinked wiki derived from those sources. Make knowledge compound across ingests and queries instead of reconstructing the same synthesis from scratch each time.

## Scope

Use this skill to:

- initialize a new LLM-maintained wiki;
- ingest one or more sources into an existing wiki;
- answer questions across accumulated wiki knowledge with traceable provenance;
- persist durable cross-source analyses back into the wiki when authorized;
- lint and repair wiki health;
- evolve the wiki schema when the user explicitly asks to change conventions or structure.

Do not use this skill for one-off summaries, ordinary retrieval-only Q&A, generic Obsidian editing, unrelated documentation work, or any task whose primary goal is to modify source documents.

## Core Invariants

1. **Raw sources are immutable.** Read them; never rewrite, normalize in place, delete, or silently replace them.
2. **The wiki is derived state.** The LLM may create and update wiki pages, but generated pages do not become source truth merely because they exist.
3. **The schema governs the wiki.** Follow the existing schema first. For a new wiki, create WIKI_SCHEMA.md and make its conventions explicit.
4. **Knowledge must compound.** Reuse and revise existing pages, links, and syntheses rather than generating disconnected summaries for every source.
5. **Preserve provenance.** Important claims must remain traceable to raw source paths, source identifiers, or externally captured source records.
6. **Do not hide disagreement.** When sources conflict, record the conflict and evidence. Resolve it only when source precedence or newer evidence makes the resolution supportable.
7. **Keep navigation and history current.** Update wiki/index.md after material wiki changes and append to wiki/log.md for ingest, query-persist, lint, or schema-change operations.
8. **Prefer simple infrastructure.** Use the index and ordinary file search before introducing embeddings, vector databases, or extra services.

## Required Inputs and Defaults

Resolve from the active workspace before writing:

- wiki root;
- requested mode;
- source path or source set when ingesting;
- existing schema and link conventions;
- writable wiki boundary;
- whether the user authorized persistence for query results.

For a new wiki, default to:

```text
WIKI_SCHEMA.md
raw/
wiki/
  index.md
  log.md
  sources/
  entities/
  concepts/
  syntheses/
```

Create `raw/assets/` only when local attachments are part of the source workflow. Preserve an existing coherent structure instead of forcing this default onto it.

## Mode Selection

| Mode | Use when | Primary result |
|---|---|---|
| `initialize` | no usable wiki structure or schema exists | baseline directories, schema, index, and log |
| `ingest` | new raw source material must become accumulated wiki knowledge | source summary plus updates to relevant wiki pages, index, and log |
| `query` | the user asks a question against the accumulated knowledge | grounded answer; optional durable synthesis page when authorized |
| `lint` | the user asks to health-check, reconcile, or maintain the wiki | findings plus safe repairs and a logged lint result |
| `evolve-schema` | the user explicitly asks to change page types, metadata, conventions, or workflow rules | minimal schema change plus any required migration and log entry |

## Workflow

### 1. Inspect before acting

1. Resolve the wiki root and writable boundary.
2. Read WIKI_SCHEMA.md when present.
3. Read wiki/index.md before broad wiki traversal when it exists.
4. Read the recent portion of wiki/log.md when recent operations may affect the task.
5. Inspect only the pages and raw sources needed for the active mode; expand when evidence requires it.
6. Never infer unseen source content.

### 2. Initialize

1. Inspect for an existing compatible structure; do not overwrite it.
2. Create missing baseline directories and files.
3. Write WIKI_SCHEMA.md using the contracts in `references/wiki-protocol.md`.
4. Create a content-oriented wiki/index.md grouped by page type or domain.
5. Create an append-only wiki/log.md with the initialization entry.
6. Validate links and writable/read-only boundaries.

### 3. Ingest

1. Verify the source is inside `raw/` or another explicitly read-only source location.
2. Read enough of the source to capture its actual claims, context, date, and limitations.
3. Use wiki/index.md to identify existing entities, concepts, source summaries, and syntheses that may be affected.
4. Create or update one source-summary page for the source.
5. Update existing entity and concept pages instead of creating duplicates when the subject already exists.
6. Add new pages only when the information is durable enough to deserve its own maintained page.
7. Record contradictions, superseded claims, uncertainty, and open questions rather than flattening them into one confident statement.
8. Update cross-links in both directions where useful.
9. Update wiki/index.md for every created, renamed, or materially changed page.
10. Append one ingest entry per source to wiki/log.md, even during batch ingest.
11. Validate the mutation set against the schema and provenance rules before reporting completion.

Default to one-source-at-a-time ingestion when the user has not requested a batch. For batch work, keep source provenance and log entries separable so one source cannot silently inherit claims from another.

### 4. Query

1. Read wiki/index.md first to locate candidate pages.
2. Read the most relevant wiki pages and follow their source references.
3. Re-open raw sources for decisive, disputed, stale, or high-impact claims instead of trusting a derived page alone.
4. Answer with source-grounded synthesis and expose material uncertainty or disagreement.
5. Persist the answer under `wiki/syntheses/` only when it adds durable cross-source knowledge and the user has authorized wiki mutation.
6. If persisted, link the synthesis from relevant pages, update wiki/index.md, and append a `query-persist` entry to wiki/log.md.

### 5. Lint

Check at least:

- broken or missing internal links;
- index entries that point nowhere or pages missing from the index;
- orphan pages with no useful inbound relationship;
- duplicate entity or concept pages;
- stale claims superseded by newer raw sources;
- contradictions represented as settled facts;
- important claims with weak or missing provenance;
- missing cross-links between clearly related maintained pages;
- repeatedly mentioned durable concepts that lack a maintained page;
- unanswered gaps that deserve a new source or targeted research.

Repair mechanical issues automatically when write authority exists and the fix is unambiguous. For semantic contradictions or uncertain merges, record a finding instead of inventing a resolution. Append a lint entry to wiki/log.md describing checks and repairs.

### 6. Evolve the schema

Use only on explicit request or when the current task cannot be completed coherently under the existing schema.

1. Identify the recurring problem the schema change solves.
2. Prefer the smallest backward-compatible change.
3. Update WIKI_SCHEMA.md before migrating affected wiki pages.
4. Migrate only pages that require the new rule.
5. Validate links, provenance, index coverage, and log consistency.
6. Append a `schema-change` entry to wiki/log.md with the reason and affected page types.

## Resource Loading

Load only what the active branch needs:

- `references/wiki-protocol.md` for default structure, page contracts, naming, index, log, and operation details;
- `references/provenance-and-consistency.md` for evidence hierarchy, contradiction handling, stale claims, transactional edits, privacy, and scale rules;
- `references/origin.md` when provenance of the skill design or conceptual invariants matters;
- `examples/usage-scenarios.md` for calibration examples;
- `evals/activation-scenarios.json` for planned activation, non-activation, ambiguous, and edge coverage. Treat these scenarios as planned unless they were actually executed.

## Validation

Before reporting a mutating operation as complete, verify:

- no raw source file was modified;
- every changed page follows the active schema;
- important new factual claims have traceable provenance;
- generated wiki pages are not the sole evidence for claims that should trace to raw sources;
- internal links added or changed resolve;
- wiki/index.md reflects created, renamed, or materially changed pages;
- wiki/log.md contains the required append-only operation entry;
- unresolved contradictions, missing evidence, and partial reads are reported rather than hidden.

If the workspace is version-controlled, inspect the final diff when available and confirm source files are unchanged.

## Output Contract

For mutating operations, report:

1. mode used;
2. raw sources read;
3. wiki pages created, updated, renamed, or removed;
4. index and log status;
5. contradictions, stale claims, or gaps surfaced;
6. validation performed and any checks not run;
7. remaining limitations or follow-up work.

For query-only operations, provide the grounded answer first, then concise provenance and uncertainty. If a durable synthesis was persisted, include its wiki path and the index/log updates.

## Stop Conditions

Stop or narrow the task when:

- the wiki root is ambiguous and multiple candidates could be mutated;
- the requested action would modify or delete raw sources;
- the source content needed for a claim is unavailable, incomplete, or unreadable and proceeding would require guessing;
- the existing schema conflicts with the requested mutation and the user did not authorize schema evolution;
- a contradiction cannot be resolved from source precedence or evidence;
- the requested write would escape the selected wiki boundary;
- the user asks to treat an LLM-generated page as authoritative source truth when raw evidence is required;
- a batch is too large to preserve per-source provenance and validation within the available context or tooling. In that case, process a bounded subset and report the remaining scope without fabricating completion.
