# Source-owned artifact orchestration

## Ownership

The Supervisor answers who acts next. Each domain agent applies its own skill's artifact decision rules and writes only owner-approved sources. Workspace answers what exists and how sources relate. The UI presents a snapshot. No component uses a view as source truth.

| Owner | Canonical artifacts | Default root |
|---|---|---|
| Nomia | governance, roadmap, reporting and business decisions | `docs/product/<work_item_id>` |
| Mago | planning identity, PRD, design, tasks and validation plan | `docs/specs/<work_item_id>` |
| Magia | execution state, implementation notes and real evidence | `docs/implementation/<work_item_id>` |
| Workspace | derived catalog and offline views only | `.rhapsodia/catalog`, `.rhapsodia/views` |

`work_item_id` is correlation, not shared state. A Mago spec ID remains meaningful even when its documents are not stored inside a Board. Artifact IDs use producer namespaces, each file has a source-owned sidecar, and typed handoff v3 remains the domain evidence transfer contract.

## Actions and validation

Workers return `artifact_actions` using the versioned closed receipt schema. Each entry preserves type, created/updated/unchanged/deprecated/removed action, paths, before/after hashes and reason. The source owner validates live source/sidecar hashes before returning. Empty action arrays are correct for read-only phases. The Supervisor does not demand files only to populate a UI.

Metadata publication validation is separate from planning checks, runtime proof and governance closure. Workspace cannot convert one into another. Missing dependencies remain diagnostics, conflicts remain conflicts, and imported JSON remains a snapshot.

## Native operation

Use Mago's `native_planning.py` for identity and semantic planning gates, the owner-local `native_artifacts.py` for publication, and Magia's `native_execution.py` for actual command receipts and source-bound closure. Nomia keeps schema-v2 governance semantics and closure authority with optional evidenced spec identity. All helpers load only their own package code.

Invoke `rhapsodia-workspace/scripts/workspace.py render --repo-root <REPO>` for a local HTML view. The runtime has no network/backend/database dependency and no writeback function. New producers integrate through data envelopes, not runtime imports. The repository's existing host adapters remain canonical; the installer now includes the seventh agent.

## Legacy support and rollback

Board is retained as an explicit compatibility profile, not restored as core architecture. Producer migration plans enumerate recognized owned files and exclusions, preserve source bytes, reject collisions/drift and copy into independent roots with unknown states pending semantic review. A journal and committed receipt support deterministic recovery. Migration is implemented now; no later Board-removal project is required to use native operation.

Restore the original exact-version package set for code rollback. Original Board files are retained unchanged for artifact rollback; copied native artifacts can be retained separately. Never blend state from both profiles. Empty/recreated derived directories have no canonical meaning.

## Portability and verification

Portable core: Python 3.11+, standard-library artifact/Workspace runtime, optional pre-existing Mags content-validation dependencies. No Orca or other orchestration runtime is required. VS Code/Copilot adapters remain thin. Native invocation on each external host requires that host's real capability/permission model and is not inferred from local structural tests.

Repository tests cover publishers in isolation, read-only catalog behavior, actual command evidence, legacy copy migration, stale inputs, atomic last-good preservation, packaging isolation and browser interactions. Reports state exactly which commands/browsers ran; no planned scenario is counted as measured host behavior.
