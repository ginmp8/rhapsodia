# Usage Scenarios

These examples calibrate expected behavior. They are examples, not executed evaluation results.

## 1. Initialize a research wiki

**Prompt:** `Create an LLM wiki for this research workspace. Keep source PDFs read-only and make the wiki usable from Obsidian.`

**Mode:** `initialize`

**Expected behavior:**

- inspect the workspace before creating folders;
- create `WIKI_SCHEMA.md`, `wiki/index.md`, and `wiki/log.md` plus useful page directories;
- mark the raw-source location read-only in the schema;
- choose link conventions compatible with the existing workspace;
- avoid adding embeddings, a database, or a custom app without evidence they are needed.

## 2. Ingest one source

**Prompt:** `Ingest raw/papers/agent-memory.pdf into the wiki and update anything it changes.`

**Mode:** `ingest`

**Expected behavior:**

- read the paper without modifying it;
- inspect the index for existing related pages;
- create or update its source summary;
- revise relevant entity and concept pages;
- record contradictions or changed conclusions;
- update the index and append an ingest log entry;
- report changed paths and validation.

## 3. Cross-source query with persistence

**Prompt:** `Using the wiki, compare the two approaches to long-term agent memory. Save the comparison if it is useful later.`

**Mode:** `query`

**Expected behavior:**

- use the index to locate relevant maintained pages;
- trace decisive claims back to raw sources;
- answer with material disagreements visible;
- if the comparison adds durable cross-source knowledge, create a synthesis page and link it into the wiki;
- update index and log only if a page is persisted.

## 4. Health check

**Prompt:** `Lint the wiki for stale claims, contradictions, broken links, and orphan pages. Fix safe issues.`

**Mode:** `lint`

**Expected behavior:**

- repair broken links and index drift when unambiguous;
- surface unresolved semantic contradictions rather than choosing a winner without evidence;
- identify stale claims and missing provenance;
- append a lint log entry with checks and repairs.

## Non-activation examples

- `Summarize this PDF for me.` — one-off summarization, not persistent wiki maintenance.
- `Build a RAG chatbot over these documents.` — retrieval system design is the primary goal.
- `Create a single Obsidian note for this meeting.` — ordinary note creation.
- `Rewrite the source article to be shorter.` — mutates or transforms the source artifact rather than maintaining the wiki.
