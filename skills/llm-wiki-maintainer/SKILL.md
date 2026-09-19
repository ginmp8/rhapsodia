---
name: llm-wiki-maintainer
description: 'use when the user wants to build or operate a persistent llm-maintained markdown wiki that compounds knowledge across sources over time: initialize the workspace, ingest immutable source material, update entity, concept, source-summary, or synthesis pages, maintain index.md and log.md, answer cross-source questions with provenance, persist durable syntheses, lint for contradictions/stale claims/orphans/broken links, or evolve the wiki schema. do not use for one-off summarization, ordinary rag/search, generic note-taking, source-document mutation, or workflows that treat generated wiki pages as source truth.'
---

# LLM Wiki Maintainer

## Mission

Build and maintain a persistent Markdown knowledge base in which raw sources remain immutable source truth and the LLM maintains a structured, interlinked wiki derived from those sources. Make knowledge compound across ingests and queries instead of rebuilding the same synthesis from scratch.

The workflow is reproducible at the integrity/process layer while preserving bounded semantic/editorial judgment where meaning cannot be reduced safely to code.

## Scope

Use this skill to:

- initialize a new LLM-maintained wiki;
- ingest one or more immutable sources into an existing wiki;
- answer questions across accumulated wiki knowledge with traceable provenance;
- persist durable cross-source analyses when authorized;
- lint and repair wiki health;
- evolve the wiki schema when explicitly requested or required for an authorized operation;
- recover or roll back derived wiki mutations using recorded last-known-good evidence.

Do not use this skill for one-off summaries, retrieval-only Q&A, generic Obsidian editing, unrelated documentation, RAG-system implementation, or any task whose primary goal is to modify source documents.

## Core invariants

1. **Raw sources are immutable source truth.** Read/hash/snapshot them; never rewrite, normalize in place, delete, or silently replace them.
2. **The wiki is derived state.** Generated pages never become source truth merely because they exist or cite each other.
3. **Provenance terminates in source evidence.** Important factual claims must remain traceable to exact source IDs/paths/snapshots when the runtime permits it.
4. **The schema governs the wiki.** Follow the active schema first. Never silently reinterpret old pages under a new schema.
5. **Knowledge compounds.** Reuse and revise canonical pages instead of creating disconnected summaries for every source.
6. **Conflicts are lossless.** Never discard or silently reconcile disagreement without evidence supporting supersession or scope distinction.
7. **Manual derived-state edits are preserved.** Hash drift blocks overwrite until the current page is re-read and reconciled.
8. **Mutations are recovery-aware.** Stage, validate, use expected-before hashes, preserve last-known-good bytes, emit receipts, and freeze after pass.
9. **Structural evidence and semantic judgment stay separate.** Hash/schema/link checks do not prove truth; semantic/editorial conclusions require source review.
10. **Prefer simple infrastructure.** Use index/file search before adding embeddings, vector stores, or services.

## Reproducibility ceiling

Classify this skill as `research-analytic` with tool-action integrity controls.

Use mechanics for:

- exact source SHA-256 identity;
- duplicate-content detection and aliases;
- immutable source snapshots;
- stable page IDs after a semantic canonical key is chosen;
- deterministic frontmatter rendering for the default schema;
- path/precondition validation, atomic per-file replacement, recovery and rollback;
- machine-readable ingest/mutation/lint receipts;
- final candidate/package identity.

Keep model/human judgment for:

- claim extraction and importance;
- entity/concept identity and canonical keys;
- deciding which pages a source affects;
- interpreting source authority/scope;
- deciding whether claims conflict, supersede, or remain unresolved;
- cross-source synthesis and editorial wording.

Never replace those semantic decisions with arbitrary filename, keyword, recency, or hash heuristics.

## Required inputs and defaults

Resolve before writing:

- exactly one wiki root;
- requested mode;
- active `WIKI_SCHEMA.md` and schema identity when present;
- source path/set and immutable source boundary for ingest;
- writable derived-state boundary;
- whether query persistence is authorized;
- runtime capability for filesystem writes, hashing, Python 3.10+, and command execution.

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

When reproducibility helpers are available, create `.llm-wiki/` only for derived operational manifests, source snapshots, receipts, and recovery evidence. Preserve an existing coherent structure instead of forcing this default.

## Mode selection

| Mode | Use when | Primary result |
|---|---|---|
| `initialize` | no usable wiki structure/schema exists | baseline directories, schema, index, log, optional operational state |
| `ingest` | new source material must become accumulated wiki knowledge | source identity/receipt plus source summary and affected page updates |
| `query` | user asks a question against accumulated knowledge | grounded answer; optional durable synthesis when authorized |
| `lint` | health-check/reconcile/maintain the wiki | structural receipt, semantic findings, safe repairs when unambiguous |
| `evolve-schema` | user explicitly requests schema change or current schema cannot support an authorized task | versioned schema change, bounded migration, receipt and rollback point |

## Workflow

### 1. Inspect and bind identity

1. Resolve exactly one wiki root and writable boundary.
2. Read `WIKI_SCHEMA.md` when present and record its schema version/identity.
3. Read `wiki/index.md` before broad traversal.
4. Read the recent `wiki/log.md` portion when prior operations matter.
5. Inspect `.llm-wiki/` manifests/receipts when present; they are operational evidence, not semantic source truth.
6. Inspect only source/pages needed for the mode, expanding when evidence requires it.
7. Never infer unseen source content.

### 2. Initialize

1. Inspect for an existing compatible structure; never overwrite one blindly.
2. Create only missing baseline directories/files.
3. For a new default schema, write `WIKI_SCHEMA.md` with `schema_version: llm-wiki/2` and the contracts in `references/wiki-protocol.md`.
4. Create content-oriented `wiki/index.md` and append-only `wiki/log.md`.
5. If reproducibility helpers are available, initialize operational state only as needed by first source capture/mutation.
6. Validate links and source/writable boundaries before completion.

### 3. Ingest

For every source, preserve a one-source identity and receipt even during batch work.

1. Verify the source is inside the declared immutable source boundary.
2. When filesystem execution is available, capture its exact identity/snapshot before semantic reading:

```text
<PYTHON> scripts/source_identity.py capture --workspace <ROOT> --source <ROOT>/raw/<SOURCE> --json <INGEST_RECEIPT>
```

3. Handle intake classification before semantic mutation:
   - `first-ingest`: proceed;
   - `already-ingested`: do not rewrite derived pages unless some independent dependency changed;
   - `duplicate-content-alias`: preserve one source identity and add the alias; do not create a duplicate source-summary identity;
   - `source-modified`: block automatic reingestion; preserve old source ID/snapshot and require explicit authorization before registering the new bytes as a new source version.
4. Read the raw source or exact captured snapshot; extract actual claims, context, dates, scope, limitations, entities, concepts, and relationships.
5. Use index plus canonical page identity to locate existing pages. Reuse the same page when semantic identity is the same.
6. Create/update one source-summary page for the canonical source ID.
7. Update existing entity/concept/synthesis pages only when the new evidence materially affects them.
8. Preserve contradictions, superseded claims, uncertainty, and open questions explicitly.
9. Record source-to-page and page-to-source provenance with source IDs.
10. Render the complete derived mutation into staging; include index/log changes.
11. Validate staged structure/provenance and record expected-before hashes for every existing target.
12. Commit using the recovery-aware transaction helper when available:

```text
<PYTHON> scripts/wiki_transaction.py commit --workspace <ROOT> --staging <STAGE> --plan <PLAN.json> --json <MUTATION_RECEIPT>
```

13. Run strict structural validation:

```text
<PYTHON> scripts/wiki_validate.py --workspace <ROOT> --strict --json <LINT_RECEIPT>
```

14. If a post-commit hard validation fails, roll back with the committed mutation receipt when safe, preserve failure/recovery evidence, and do not claim completion.
15. Freeze the successful operation. Any later edit reopens validation.

If helpers cannot run, preserve the same invariants using available host tools and mark unexecuted hash/snapshot/transaction gates explicitly. Do not claim equivalent mechanical reproducibility without equivalent evidence.

### 4. Query

1. Read `wiki/index.md` first.
2. Read the most relevant maintained pages and follow their source IDs/locators.
3. Re-open raw source evidence for decisive, disputed, stale, high-impact, or migration-sensitive claims.
4. Answer with source-grounded synthesis and expose material disagreement/uncertainty.
5. Persist only when the synthesis is durable and mutation is authorized.
6. If persisted, use the same staged/validated/receipt-backed mutation path as ingest.

### 5. Lint

Mechanically check at least:

- source manifest/snapshot integrity when operational state exists;
- changed/missing registered raw paths;
- schema-version/frontmatter consistency;
- duplicate/missing page IDs;
- page-to-source provenance IDs;
- broken/missing internal links;
- index entries that point nowhere or maintained pages missing from the index;
- append-only log structure;
- path/boundary violations.

Semantically inspect at least:

- stale-claim candidates;
- contradictions represented as settled facts;
- source authority/scope changes;
- duplicate entities/concepts that may or may not be semantically equivalent;
- important claims with weak/missing provenance;
- missing cross-links and durable gaps.

Repair only unambiguous mechanical issues automatically. Record semantic issues as `needs-review` until source evidence supports a specific repair.

The lint receipt must keep `structural_evidence` separate from `semantic_editorial_judgment`.

### 6. Evolve schema

Use only with explicit authorization or when the requested operation cannot be represented coherently under the active schema.

1. Record current schema identity and a last-known-good wiki state.
2. Define target schema identity, compatibility statement, affected page types/fields, deterministic transforms, semantic-review requirements, rollback point, and validation gates.
3. Update `WIKI_SCHEMA.md` in staging before dependent page migration.
4. Migrate only affected derived pages; never mutate raw sources.
5. Validate staged schema/provenance/links/index/log.
6. Commit with precondition hashes and recovery evidence.
7. Append `schema-change` log entry with old/new version and mutation receipt.
8. Run strict lint and freeze the new state.

Never silently reinterpret old pages under a new version.

## Idempotency, drift, failure and rollback rules

- Same exact source + same schema + no independent dependency change => no semantic rewrite required.
- Same source bytes at another filename => one source ID, multiple aliases, one source-summary identity.
- Known source path with changed bytes => integrity event; block until explicitly versioned/replaced.
- Registered source path removed => preserve source ID/snapshot and derived knowledge; report missing raw path.
- Manual/concurrent edit to a target page => expected-before hash mismatch; preserve current page, re-read/merge, then regenerate from the new hash.
- Mid-commit failure => restore touched files when possible; preserve recovery artifacts if rollback is incomplete.
- Rerun of the exact committed mutation => classify `already-applied`; do not duplicate log/page changes.
- Rollback => allowed only from a valid receipt/recovery snapshot and only when current bytes still match the committed post-state.

## Canonical page/frontmatter rules

For the default schema, use `references/wiki-protocol.md` and `references/reproducibility-protocol.md`.

When Python helpers are available:

```text
<PYTHON> scripts/page_identity.py id --type <source|entity|concept|synthesis> --key <CANONICAL_KEY>
<PYTHON> scripts/page_identity.py render-frontmatter --metadata <META.json> --body <BODY.md> --out <STAGED_PAGE.md>
```

The helper canonicalizes mechanics only. The semantic canonical key for entity/concept/synthesis pages remains a judgment decision and must not be derived from mere spelling similarity.

## Resource loading

Load only the active branch:

- `references/wiki-protocol.md` — default structure, page contracts, canonical frontmatter, index/log, ingest/query/batch rules;
- `references/provenance-and-consistency.md` — evidence hierarchy, conflicts, staleness, source drift/removal, manual edits, privacy, scale;
- `references/reproducibility-protocol.md` — identities, snapshots, transactions, receipts, recovery, schema migration, final freeze;
- `references/origin.md` — conceptual provenance of the skill;
- `examples/usage-scenarios.md` — calibration examples;
- `evals/activation-scenarios.json` — frozen evaluator baseline for activation/non-activation scope; preserve its evaluator hash and do not treat it as executed behavioral evidence;
- `evals/reproducibility-scenarios.json` — planned lifecycle/regression scenarios; do not report pass rates without actual execution;
- `schemas/*.schema.json` — machine-readable state/receipt/plan contracts;
- `scripts/*.py` — optional stdlib helpers for objective mechanics; they are not a semantic evaluator.

Treat Agent Skills Markdown as the portable core. The package must not semantically depend on OpenAI, Claude, Copilot, Cursor, or another host-specific invocation mechanism. `agents/openai.yaml` remains an optional OpenAI adapter.

## Validation

Before reporting a mutating operation complete, verify applicable gates:

- source bytes were not modified by the skill;
- source identity/snapshot receipt corresponds to the bytes actually analyzed;
- same-content duplicates did not create duplicate source identities;
- every changed page follows the active schema/version;
- important factual claims trace to source IDs/evidence;
- generated pages are not sole evidence where raw evidence exists;
- conflicts/supersession remain explicit;
- current target hashes matched mutation preconditions or drift was reconciled before commit;
- internal links and index coverage are valid;
- `wiki/log.md` has the required append-only entry for a real mutation;
- mutation/lint receipts describe the exact committed bytes;
- receipt/output paths are canonicalized and rejected when they alias raw inputs, staged inputs, maintained wiki targets, or sibling outputs;
- no hard structural lint failure remains;
- unresolved semantic findings/partial reads remain visible;
- no post-validation edit occurred.

If version control exists, also inspect the final diff and verify `raw/**` is unchanged.

## Output contract

For mutating operations, report:

1. mode and active schema identity;
2. raw sources read plus source IDs/intake classifications;
3. derived pages created/updated/renamed/removed;
4. index/log status;
5. conflicts, stale candidates, manual drift, source drift/removal, or evidence gaps;
6. structural evidence separately from semantic/editorial judgment;
7. ingest/mutation/lint/rollback receipt paths or IDs when produced;
8. exact validation performed plus `not-run` checks;
9. remaining limitations.

For query-only operations, answer first, then concise provenance and uncertainty. If a durable synthesis was persisted, include its page path plus mutation/index/log/receipt status.

## Stop conditions

Stop or narrow the operation when:

- zero or multiple plausible wiki roots could be mutated;
- requested action would modify/delete raw source bytes;
- source bytes needed for a claim are unavailable and proceeding would require guessing;
- a known source path changed bytes and replacement/versioning is not explicitly authorized;
- an existing target page changed after it was read and semantic reconciliation has not occurred;
- the active schema conflicts with the requested mutation and migration is not authorized;
- a conflict cannot be resolved from evidence; preserve it instead of inventing resolution;
- a write escapes the selected derived-state boundary;
- the user asks to treat generated wiki prose as authoritative source truth where source evidence is required;
- required structural validation fails and safe rollback/repair cannot restore a coherent state;
- a batch is too large to preserve per-source identity, provenance, validation, and recovery evidence within available tooling/context.
