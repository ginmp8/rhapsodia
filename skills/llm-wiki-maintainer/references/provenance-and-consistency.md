# Provenance and Consistency

Use this reference when claims conflict, source freshness matters, manual edits exist, the wiki is large, or a mutation could damage traceability. Load `reproducibility-protocol.md` for exact hashes, source snapshots, transactions, receipts, and rollback.

## Evidence hierarchy

Use this hierarchy by default:

1. immutable raw source bytes or an exact captured source snapshot with matching hash;
2. explicit metadata about that source, such as date, author, version, scope, or jurisdiction;
3. derived source-summary pages;
4. entity, concept, and synthesis pages;
5. conversational inference.

Derived pages accelerate navigation and accumulated reasoning. They do not outrank the evidence they summarize and never become source truth merely through repetition.

## Provenance rules

- Assign exact source IDs when the runtime permits hashing.
- Keep source IDs and useful raw path/locator details on derived pages.
- Keep enough location detail to reopen decisive evidence efficiently when the format permits it.
- For important claims, the provenance chain must terminate in source evidence, not another generated page.
- When the same bytes appear at multiple paths, treat those paths as aliases of one source identity.
- If external research becomes durable wiki evidence, capture a stable source record/bytes under the declared source boundary before treating it as long-term evidence.
- If source bytes cannot be retained or hashed, label that limitation explicitly.

## Structural evidence vs semantic/editorial judgment

Keep the two layers separate in reports and receipts.

**Structural evidence can establish:**

- exact source/page hashes;
- source identity and duplicate aliases;
- whether registered raw bytes changed or disappeared;
- whether source IDs referenced by a page exist;
- schema/frontmatter shape;
- broken links/index drift;
- expected-before hash drift;
- whether committed bytes match a mutation receipt.

**Semantic/editorial judgment decides:**

- what a source means;
- which entity/concept it refers to;
- whether claims address the same scope;
- whether a conflict exists or is resolved;
- whether one source supersedes another;
- whether a synthesis is durable/useful;
- whether a claim is substantively stale.

Never present a structural validator pass as proof of factual correctness.

## Contradictions

When new evidence conflicts with existing wiki content:

1. identify the exact proposition/frame in conflict;
2. trace every side to source IDs and reopen the decisive source evidence;
3. compare date, scope, version, authority, conditions, and applicability;
4. preserve each competing claim separately;
5. if evidence clearly supports supersession, update the current synthesis and retain the superseded claim plus reason;
6. otherwise mark the conflict unresolved or scope-different.

Do not discard conflict because one statement is newer, more plausible, more detailed, or easier to reconcile.

## Staleness

A mechanical checker may produce a **stale candidate**, not a truth conclusion. Review a claim when:

- a newer source explicitly concerns the same page/subject;
- a system/entity version changed;
- a page declares source IDs that are not all in its reviewed source set;
- a new source-to-page relationship was recorded after the page's last semantic review;
- a source was time-sensitive or later superseded.

Then reopen relevant sources and decide whether the claim is still valid, stale, scope-limited, or contradicted. Preserve uncertainty when evidence is insufficient.

## Source changes and removals

The skill never edits raw sources, but external actors may.

- If a registered raw path changes bytes, treat it as an integrity event. Preserve the prior source ID/snapshot and do not silently remap provenance.
- If explicit authorization treats the new bytes as a replacement/version, register a new source ID and preserve the previous relationship.
- If a registered path disappears, retain the source identity/snapshot and flag path availability. Do not purge pages automatically.
- If source evidence itself cannot be recovered or verified, lower confidence and mark affected claims for review.

## Manual derived-page changes

A manual edit to `wiki/**` is legitimate derived-state input, but not source truth.

Before overwrite, compare the current page hash to the hash read when the candidate mutation was prepared. On mismatch:

1. block the write;
2. preserve the current manual page;
3. inspect the diff/content;
4. merge only with semantic justification;
5. rebuild the staged page from current bytes;
6. validate and commit under a new precondition.

Do not use automatic rollback or regeneration to erase an unreviewed manual change.

## Transactional mutation

For broad updates:

1. determine the complete intended mutation set;
2. read and hash every existing target page;
3. render derived candidates in staging, never in `raw/`;
4. validate source provenance and staged structure;
5. commit with expected-before hashes and recovery copies;
6. run post-commit validation;
7. retain mutation/lint receipts and last-known-good recovery evidence;
8. freeze after pass.

If a commit fails mid-update, automatically restore already-touched targets when possible. If rollback is incomplete, preserve backups and failed candidate paths and report recovery as required; do not continue unrelated mutations.

## Mechanical vs semantic repairs

Safe mechanical repairs include:

- fixing an unambiguous broken internal path;
- adding a missing index entry for an existing page;
- removing a dead index entry when history does not require it;
- updating reciprocal paths after an authorized rename;
- normalizing deterministic frontmatter to the active schema;
- restoring exact last-known-good bytes from a validated transaction receipt when no later drift exists.

Semantic repairs require evidence and may remain findings:

- merging possibly distinct entities;
- choosing which conflicting claim is true;
- deciding a canonical concept interpretation;
- deleting a claim because it seems old;
- deciding a manual edit is wrong;
- deciding a source replacement should supersede earlier evidence.

## Privacy and external research

Do not export private source material to an external service to make retrieval easier. Keep snapshots and receipts inside the authorized workspace unless the user explicitly chooses another destination.

When lint identifies a knowledge gap, propose targeted research rather than silently mixing web content into the wiki. If external research is authorized and persisted, capture durable provenance first.

## Scale and search

Use `wiki/index.md` plus ordinary file search while effective. Embeddings/vector stores are optional accelerators, not the knowledge model.

As the wiki grows, adopt more search infrastructure only when there is evidence index-first navigation materially fails. Raw/source identities, provenance, schema, receipts, and maintenance rules remain authoritative regardless of search engine.
