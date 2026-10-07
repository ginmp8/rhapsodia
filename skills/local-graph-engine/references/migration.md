# Version 2 migration and storage safety

## Compatibility
Public GraphPatch/GraphView v1 and all nine original Engine/Explorer regression tests remain supported. SQLite user_version stays 1 with extension_version 2 for additive revision/claim/memory tables. This is package version 2.0.0 because default evidence access, offline rendering and broader workflows materially change the experience, not because v1 payloads are invalid.

## Before upgrading a real graph
1. Stop active writers. Keep the previous package and a consistent `backup` snapshot.
2. Run `doctor` and inspect SQLite version/journal mode.
3. On a WAL database with an unpatched runtime, stop every other connection and run `journal --mode delete`, or upgrade the runtime's SQLite to a documented patched version. The command does not install software.
4. Apply the new package to the working copy, validate-db, and compare representative queries and a source-backed GraphView.
5. Keep old snapshots. Do not run an old writer against a graph upgraded with v2 claim/revision extensions; use the v2 reader or restore the earlier snapshot for rollback.

## WAL policy
New DBs remain in default rollback journal DELETE, which avoids a mandatory WAL portability/concurrency assumption. Explicit `journal --mode wal` requires SQLite >=3.51.3, 3.50.7+ within the 3.50 branch, or 3.44.6+ within the 3.44 branch. These ranges correspond to documented upstream WAL-reset fixes checked 2026-10-07; they are not a comprehensive vulnerability audit. Unknown earlier backports fail closed.
Writers detect WAL on an unestablished runtime and stop with a migration instruction. No automatic journal conversion during ordinary ingestion. WAL remains unsuitable for a network-shared database, and raw live DB copies may omit committed WAL transactions. Use the backup API.

## Behavioral deltas
New typed queries select accepted evidence by default; legacy commands retain accepted/ambiguous/stale scope. Source assertions and full observations are now preserved separately from canonical display. History cannot restore information already lost before the upgrade. Derived hashes cover logical knowledge, not storage page order or browser view state.
The Explorer now uses its bundled offline renderer by default. A local reviewed G6 file can still be supplied; the previous CDN attempt is intentionally removed. Browser layout/theme state remains presentation-only.
