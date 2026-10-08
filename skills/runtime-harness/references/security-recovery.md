# Security, freshness and recovery

## Trust boundary

Runtime state is private local observation data, never authorization. Discovery does not
execute source code, package hooks, macros, URLs, network requests or candidate tools.
Agents may publish only mechanically verifiable tool/file locations through bounded
operations. Arbitrary prose, credentials, permissions, decisions, validation verdicts and
conversation history are intentionally outside the registry.

The core rejects traversal, unsupported URI schemes, secret-like paths, symlink escapes
for shared resources, special files, malformed/oversized JSON, duplicate keys, nonfinite
numbers and unsafe write hardlinks. Executable symlinks are allowed because common PATH
installations use them; their target/stat identity is checked on reuse.

This is not a sandbox against malicious same-user processes or privileged attackers.
Hashes are integrity/change identifiers, not authentication or signatures.

## Freshness

Global snapshot reuse binds stable workspace/host/interpreter identity plus selected
skill/agent root stamps and an overall expiry. Mutable PATH/PATHEXT and Git HEAD do not
invalidate the whole snapshot.

Tool freshness is narrower:

- available tool: recheck file/stat identity on resolution;
- missing tool: reuse until its TTL expires **and** search-space fingerprint is unchanged;
- changed PATH/PATHEXT: only a missing requested tool becomes eligible for rediscovery;
- explicit tool path: reuse while the file identity remains stable.

Resource files are rehashed on each resolution/handoff. A changed resource may still be
a valid location, but `changed_since_observed` is surfaced and old handoff pins fail.

## Recovery

- `NOT_INITIALIZED`: authorized `init` once.
- `EXPIRED`/catalog or stable-scope change: authorized `init`/`--refresh` once.
- Missing tool: authorized `ensure tool://<id>` once; do not start launcher/search loops.
- Negative cache: wait for TTL, provide new search-space evidence, or explicitly publish
  an already-found executable with `observe-tool`.
- `CORRUPT_STATE`: inspect and explicitly rebuild; never trust modified bootstrap argv.
- `BUSY`: wait for active publication to finish. Never steal a live lock automatically.
- Stale handoff pin: reopen current content and recompute required validation; never edit
  the old receipt to force readiness.

Local state is disposable after writers stop. Removing `.rhapsodia/runtime/` deletes
runtime observations/handoff IDs only; never delete source/domain artifacts as recovery.
Release builders exclude this private state.
