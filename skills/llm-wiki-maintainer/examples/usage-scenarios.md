# Usage Scenarios

These examples calibrate expected behavior. They are examples, not executed evaluation results.

## 1. Initialize a research wiki

**Prompt:** `Create an LLM wiki for this research workspace. Keep source PDFs read-only and make the wiki usable from Obsidian.`

**Mode:** `initialize`

Expected behavior:

- inspect the workspace before creating folders;
- preserve any coherent existing schema;
- for a new default wiki, create `WIKI_SCHEMA.md` with explicit schema identity, `wiki/index.md`, `wiki/log.md`, and page directories;
- keep raw sources immutable;
- avoid embeddings/databases/custom apps without evidence they are needed.

## 2. First ingest with reproducible identity

**Prompt:** `Ingest raw/papers/agent-memory.pdf into the wiki and update anything it changes.`

**Mode:** `ingest`

Expected behavior:

- hash/capture the exact source bytes when helpers are available;
- assign one content-addressed source ID and emit an ingest receipt;
- read the source without modifying it;
- reuse existing canonical pages where semantic identity matches;
- preserve conflicts or changed conclusions;
- stage index/log/page changes, commit with precondition hashes, lint, and retain receipts.

## 3. Idempotent reingestion

**Prompt:** `Ingest that same PDF again; nothing else changed.`

Expected behavior:

- same source ID;
- `already-ingested` classification;
- no duplicate source-summary page;
- no gratuitous rewrite or fake log mutation merely to refresh dates.

If the same bytes are found under another filename, record an alias instead of a second source identity.

## 4. Manual page drift

**Prompt:** `Continue the ingest, but I edited the entity page while you were working.`

Expected behavior:

- expected-before hash blocks stale overwrite;
- current manual edit stays untouched;
- re-read/merge the derived page semantically;
- regenerate staging from the new current hash, then revalidate and commit.

## 5. Conflicting sources

**Prompt:** `This new paper contradicts the older one. Update the wiki.`

Expected behavior:

- preserve both exact source IDs and claims;
- compare source scope/version/date/authority;
- mark `unresolved`, `scope-different`, or supported supersession explicitly;
- never pick a winner because one claim sounds more plausible.

## 6. Cross-source query with persistence

**Prompt:** `Using the wiki, compare the two approaches to long-term agent memory. Save the comparison if it is useful later.`

**Mode:** `query`

Expected behavior:

- use the index to locate maintained pages;
- trace decisive claims back to source IDs/raw evidence;
- expose material disagreements;
- persist only durable authorized synthesis;
- if persisted, use staged transaction, index/log updates, and receipts.

## 7. Health check

**Prompt:** `Lint the wiki for stale claims, contradictions, broken links, orphan pages, source drift, and provenance gaps. Fix only safe issues.`

**Mode:** `lint`

Expected behavior:

- structural findings are reported separately from semantic/editorial findings;
- unambiguous mechanical issues may be repaired;
- stale/conflict/entity-merge decisions remain `needs-review` until source evidence supports them;
- no source or manual page change is silently destroyed.

## Non-activation examples

- `Summarize this PDF in five bullets.` — one-off summarization, not persistent wiki maintenance.
- `Build me a vector RAG service over these documents.` — retrieval-system engineering is primary.
- `Create a single Obsidian note from this meeting.` — ordinary note creation.
- `Rewrite the source article to be shorter.` — transforms source content rather than maintaining derived wiki state.
