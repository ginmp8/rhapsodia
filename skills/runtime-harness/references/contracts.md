# Architecture and contracts

## Ownership

`host bootstrap -> immutable snapshot -> exact read-only resolver -> optional bounded publication -> handoff`

The runtime owns only local, mechanically verifiable observations. It does not own task
progress, plans, permissions, domain decisions, acceptance, agent topology or durable
conversation memory. Existing domain handoffs remain authoritative for those concerns.

## Snapshot model

State lives under:

```text
.rhapsodia/runtime/
  current.json
  snapshots/<SHA256>.json
  handoffs/<SHA256>.json
```

Snapshots are immutable canonical UTF-8 JSON. `current.json` is an atomic bootstrap
pointer to the latest merged snapshot. Agents never modify either directly.

A snapshot contains:

- stable workspace/host/interpreter scope;
- bootstrap creation time and last publication time;
- selected skill roots and bounded agent/skill catalogs;
- tool observations accumulated lazily;
- typed reusable resource-file observations.

Mutable `PATH`, `PATHEXT` and Git HEAD are deliberately excluded from global scope.
They change too often and would force expensive whole-registry refreshes. Missing-tool
observations instead bind to a hash of the exact PATH/PATHEXT search space used.

## Tool observations

Bootstrap eagerly records only the running Python. Other tools are added by `ensure`
or `observe-tool` when actually needed. Available records carry a file/stat identity,
observation source/time/TTL and optional search fingerprint. They are revalidated on
read and never executed by discovery.

Missing records carry observation time/TTL and search fingerprint. They are evidence
only that the exact bounded search did not find that ID at that time—not global absence.

## Resource observations

`resource://...` records describe a verified regular file relative to either:

- `workspace://current`, or
- one registered `skill://<id>` root.

The stored observed SHA supports diagnostics; every resolution/handoff hashes current
bytes again. Resource records cannot point to arbitrary home directories, private
credential paths, symlink escapes, directories, sockets or other special objects.

## Query contracts

[runtime-query-v1](../contracts/runtime-query-v1.schema.json) and
[runtime-result-v1](../contracts/runtime-result-v1.schema.json) define the read-only
query envelope. `resolve` and `context` never discover or publish. This invariant keeps
MCP genuinely read-only.

`if_none_match` returns `not_modified` only when the selected current result is unchanged.
The caller must retain the previous records; an etag is not hidden memory.

Snapshots follow [runtime-snapshot-v1](../contracts/runtime-snapshot-v1.schema.json).
Executable validation enforces additional filesystem/freshness rules that JSON Schema
alone cannot prove.

## Publication and contention

`ensure`/`observe-*` discover or validate outside the lock, then acquire the short local
writer lock and merge into the **latest** current snapshot. This avoids lost updates when
two agents learned different resources. Publication writes the immutable snapshot first
and moves `current.json` only after success.

The lock is never stolen. Writers wait only a short bounded interval and return `BUSY`
if another publication does not finish. This is cooperative single-workspace state, not
a distributed consensus system.
