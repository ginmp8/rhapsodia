# Long-context evidence coverage

**Purpose:** Lower the risk of missing material evidence when synthesizing long or numerous
sources; retain source boundaries and bounded work. **Load when:** claims depend on long
texts, multiple documents, dispersed exceptions, or semantically indirect evidence.
**Decision impact:** Adds a coverage/locator check before promoting conclusions; does not
change result schemas, grant retrieval permissions, or assert universal model behavior.

## Bounded selection before synthesis

1. Translate required fields and material hypotheses into an obligation list. Mark
   decisive claims, caveats, conflicts and cross-document dependencies. Set a time,
   search and context budget proportional to risk; do not treat total length as a goal.
2. For long sources, inspect section/chapter headings, metadata, indexes or symbols
   where available. Retrieve **question-relevant** passages with precise page/heading/
   line locators; examine potentially decisive material across the document (including
   middle regions), rather than assuming the opening summary or end covers the issue.
3. Vary retrieval terms: exact language, synonyms, mechanism descriptions, related
   entities and forward/backward references. Check paraphrased evidence; a failed
   literal search alone is not evidence that a fact is absent.
4. Before synthesizing, compare supporting and opposing passages; resolve version,
   date, jurisdiction, scope and conditional exceptions. Do not silently drop middle
   evidence or a source that disagrees with the emerging conclusion.
5. Maintain a temporary coverage map: `obligation -> source ID -> exact locator ->
   support/contradiction/unknown -> cited claim`. Preserve original source identities;
   use existing `_sources` and `_claims` in saved item JSON. Missing required evidence
   stays `[uncertain]`; do not invent a quote or use a summary as original evidence.
6. If the budget is exhausted before a material span can be verified, narrow the
   question, read additional authorized portions or report incomplete coverage.
   Never claim full-document verification from a partial read. The map is a workflow
   aid, not a mandatory new schema field.

## Evidence and evaluation boundary

Evaluate position sensitivity only when it affects the target: frozen, comparable cases
with relevant facts near beginning/middle/end, indirect semantic links, distractors,
conflicting sources, and truly missing evidence. Verify source locators and output claims
independently; a perfect simple needle lookup cannot prove reasoning robustness. Separate
`scenario planned`, `structural pass` and actual model-behavior results.

Do **not** prescribe a universal source order, duplicate critical data at prompt edges,
or truncate authoritative exceptions merely to improve a benchmark. Placement depends on
model, host, task, and measured evidence. Relevance and provenance take priority.

## Research grounding (primary publication pages)

- [Liu et al., TACL 2024](https://aclanthology.org/2024.tacl-1.9/): position-dependent multi-document QA and retrieval.
- [Hsieh et al., RULER 2024](https://arxiv.org/abs/2404.06654): context capacity differs from effective task capability.
- [Modarressi et al., ICML 2025](https://proceedings.mlr.press/v267/modarressi25a.html): long-context retrieval beyond literal matches.
- [Wan et al., NAACL 2025](https://aclanthology.org/2025.naacl-long.442/): source-position effects on long-form summary faithfulness.
- [Cuconasu et al., EMNLP 2025](https://aclanthology.org/2025.emnlp-main.1422/): no universal passage-reordering remedy in tested RAG systems.
