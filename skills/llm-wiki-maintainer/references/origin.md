# Origin and Invariant Mapping

This skill operationalizes the LLM Wiki pattern described by Andrej Karpathy in the public gist `llm-wiki.md` created on 2026-04-04:

https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

The package is a paraphrased operational design, not a copy of the source text.

## Source ideas preserved

- maintain a persistent, interlinked Markdown wiki instead of rediscovering all synthesis at query time;
- separate immutable raw sources from LLM-maintained derived wiki pages;
- keep a schema or agent instruction file that defines structure and workflows;
- treat ingest, query, and lint as first-class operations;
- update existing entity and concept pages when new evidence arrives;
- keep a content-oriented index and chronological append-only log;
- allow durable query results to become maintained wiki knowledge;
- make advanced local search optional rather than foundational;
- keep the human focused on source curation and direction while the LLM handles maintenance bookkeeping.

## Operational safeguards added by this skill

The source pattern is intentionally implementation-agnostic. This package makes several implicit requirements explicit so the workflow remains auditable:

- derived pages cannot become sole provenance for claims backed by raw sources;
- contradictions are preserved until evidence supports a resolution;
- broad edits are validated as a coherent mutation set;
- query results are persisted only when they add durable knowledge and mutation is authorized;
- batch ingestion preserves per-source provenance and log separation.
