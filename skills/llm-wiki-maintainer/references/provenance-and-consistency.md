# Provenance and Consistency

Use this reference when claims conflict, source freshness matters, the wiki is large, or a mutation could damage traceability.

## Evidence Hierarchy

Use this hierarchy by default:

1. immutable raw source content;
2. explicit metadata about that source, such as date, author, or version;
3. derived source-summary pages;
4. entity, concept, and synthesis pages;
5. conversational inference.

Derived pages are useful navigation and accumulated reasoning, but they do not outrank the raw evidence they summarize.

## Provenance Rules

- Keep raw source paths or stable source identifiers on derived pages.
- For important claims, preserve enough location detail to re-open the evidence efficiently when the file format permits it.
- Never use a generated wiki page as the sole provenance for a claim when an underlying raw source exists.
- If external web research becomes part of the persistent wiki, capture a stable source record or file under the source boundary before treating it as long-term evidence.
- If a source cannot be retained, label the limitation clearly instead of implying durable local provenance.

## Contradictions

When new evidence conflicts with existing wiki content:

1. identify the exact claims in conflict;
2. trace both claims to raw sources;
3. compare source date, scope, version, authority, and whether they actually address the same condition;
4. if newer or more authoritative evidence clearly supersedes the old claim, update the current synthesis and retain a supersession note;
5. otherwise keep both claims and mark the conflict as unresolved.

Do not let the model silently invent a reconciliation just to keep pages internally smooth.

## Staleness

Treat a claim as potentially stale when:

- a newer source addresses the same fact;
- an entity or system version changed;
- a page has not incorporated later source summaries that reference the same subject;
- the source itself was time-sensitive.

Prefer explicit `last material update`, source dates, or schema-specific freshness fields when they help the domain. Do not add metadata that no workflow uses.

## Transactional Mutation

For broad updates:

1. determine the complete intended mutation set;
2. apply edits only inside the wiki boundary;
3. validate links, index coverage, provenance, and log entry;
4. inspect a diff when version control is available;
5. confirm no raw source changed before declaring success.

If a failure occurs mid-update, repair the wiki to a coherent state before starting unrelated work. Do not leave the index or log claiming changes that were not completed.

## Mechanical vs Semantic Repairs

Safe mechanical repairs include:

- fixing a broken internal link when the intended target is unambiguous;
- adding a missing index entry for an existing maintained page;
- removing a dead index entry for a page that no longer exists, when history does not require it;
- updating reciprocal links after a rename;
- normalizing a page to an already established schema rule.

Semantic repairs require evidence and may need to remain findings:

- merging two pages that might represent different entities;
- choosing which conflicting claim is true;
- deciding that a concept deserves a new canonical interpretation;
- deleting a claim because it feels outdated without newer evidence.

## Privacy and External Research

Do not export private raw material to an external service merely to make retrieval easier. Prefer local or connected-file tooling already authorized for the workspace.

When lint identifies a knowledge gap, suggest web research as a gap-filling option rather than silently mixing external information into the wiki. If the user authorizes external research and persistence, capture provenance under the source boundary.

## Scale and Search

Use `wiki/index.md` plus ordinary file search while that remains effective. The wiki pattern does not require embedding-based retrieval.

As the page count grows and index-first navigation becomes inefficient, use the best available local or workspace search capability. Add hybrid or vector search only when there is evidence that simpler navigation is materially failing.

Search infrastructure is an accelerator, not the knowledge model. The persistent wiki, source boundary, provenance, and maintenance rules remain authoritative even when a search engine is added.
