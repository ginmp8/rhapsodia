# Changelog

## 1.1.0 - RhapsodIA 0.7.0

- Make bootstrap minimal: eagerly record only the running Python plus bounded skill/agent catalogs.
- Add lazy arbitrary-tool discovery through `ensure tool://<id>` with PATH/PATHEXT search only.
- Add negative caching bound to search-space fingerprint and TTL instead of invalidating the whole runtime on PATH changes.
- Add `observe-tool` for an already-found executable and `observe-resource` for stable reusable files inside approved roots.
- Merge new observations into the latest immutable snapshot so agents share discoveries without lost updates or direct state edits.
- Add `resource://` lookup and handoff pinning with live content hashes and changed-since-observed diagnostics.
- Keep query/MCP read-only; discovery/publication remains available only to callers that already hold execution/write authority.
- Remove mutable PATH and Git HEAD from global runtime scope to avoid unnecessary whole-registry refreshes.
- Extend graph export with Resource membership while keeping Local Graph Engine optional.
- Update all seven agent profiles and native instruction adapters for bounded autonomous discovery/sharing.

Independent skill version 1.1.0; RhapsodIA package release remains 0.7.0.

## 1.0.0 - RhapsodIA 0.7.0 development baseline

- Initial immutable local environment snapshot, exact logical URI queries, compact runtime handoffs, host adapters, optional read-only MCP and GraphPatch export.
