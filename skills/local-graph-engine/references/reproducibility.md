# Reproducibility and portability

## At a Glance
- **Purpose:** Define controls that reduce avoidable run-to-run and cross-host variance.
- **Load when:** Comparing outputs, designing tests, packaging, or using optional analytics.
- **Decision impact:** Fixes ordering/ID/timestamp behavior and limits portability claims to executed evidence.

## Controls
- Canonical JSON uses sorted keys and compact separators for IDs/hashes.
- Query traversals sort candidates before visiting them.
- Edge/source/evidence IDs are content-derived when caller IDs are absent.
- `graph-view-v1` contains no wall-clock generation timestamp by default.
- Source `indexed_at` is persisted only when supplied or `SOURCE_DATE_EPOCH` is set.
- Python stdlib + SQLite is the required baseline; optional packages cannot silently change baseline query semantics.
- NetworkX analytics are explicit, write a run identity, and record the installed NetworkX version.
- Keep all package paths relative; resolve a Python 3.10+ launcher by capability rather than assuming its executable name.

## Evidence ceilings
A passing package/CLI test is structural/deterministic evidence, not proof that an external parser extracted a real repository correctly. Runtime behavior on ChatGPT, Codex, Claude, Copilot, Cursor, or an IDE must be reported separately unless actually executed there.
