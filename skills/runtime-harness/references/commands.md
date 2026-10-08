# Commands and bounded behavior

All examples use an argv array equivalent to:

```text
<PYTHON> -I -S -B <RUNTIME_SCRIPT> --workspace <ROOT> <COMMAND> ...
```

The core requires Python 3.10+ and standard library only. Never concatenate untrusted
values into a shell string.

## Bootstrap and status

`init [--skills-root ROOT ...] [--refresh] [--max-age-seconds N]`

Creates a minimal immutable snapshot. Eager discovery includes only the already-running
Python plus bounded skill and agent catalogs. Tool/resource knowledge is added lazily.
`--refresh` rebuilds the bootstrap snapshot and drops old incremental observations from
the new current view; old immutable snapshots remain as recovery/history objects.

`session-start [--skills-root ROOT ...] [--format generic|vscode-local]`

Returns a small bootstrap card. Hosts may inject it once before agent work.

`status`

Returns counts and current snapshot identity without discovery.

## Read-only lookup

`resolve REF [REF ...] [--budget-bytes N]`

`context REF [REF ...] [--budget-bytes N]`

Supported logical schemes:

- `tool://<id>` — previously observed executable;
- `skill://<id>[/path]` — registered skill entry/file;
- `agent://<id>` — registered agent profile;
- `resource://<namespace>/<id>` — previously published reusable file location;
- `repo://<relative-file>` — exact workspace file;
- `workspace://current` — current workspace identity.

Neither command performs tool discovery, recursive search, execution or writes.

`query [--input FILE]` accepts `runtime-query-v1` JSON on a file/stdin and exposes only
`status|resolve|context`. It is the same read-only surface used by MCP.

## Incremental tool discovery

`ensure tool://<id> [tool://<id> ...] [--negative-ttl-seconds N]`

For each exact tool ID:

1. reuse a still-valid available observation;
2. reuse a missing observation while its TTL and PATH/PATHEXT search fingerprint match;
3. otherwise search only absolute directories from current PATH (and PATHEXT on Windows);
4. never execute the candidate;
5. atomically merge observations into the latest immutable snapshot.

At most 32 refs are accepted. Discovery is local bounded observation, not permission or
version compatibility proof.

`observe-tool tool://<id> --path <EXECUTABLE> [--ttl-seconds N]`

Publishes an executable already discovered by authorized native work. POSIX paths must
be executable; Windows requires an existing file. Symlinked executables are allowed
because common tool installations use them; file/stat identity is rechecked on read.

## Shared resource observations

`observe-resource resource://<id/path> --path <FILE> [--ttl-seconds N]`

Publishes a stable regular file inside the workspace or a registered skill root. The
stored record is a typed location plus observed hash, never arbitrary agent prose. Live
resolution rehashes the file and reports whether its bytes changed since publication.

## Handoffs

`handoff-create --input <REQUEST>` stores an immutable content-addressed receipt.
`handoff-resume --id <ID>` validates it against the current environment.
`handoff-resume --input <FILE> --rebind` explicitly rebinds a transported receipt.

## Optional adapters

- `configure --host generic|codex|copilot|claude|cursor`
- `mcp-config`, `mcp` — read-only stdio MCP query surface;
- `export-graph` — data-only GraphPatch projection;
- `benchmark --iterations N` — local mechanics only.

## Limits and exit behavior

Inputs, refs, state size, skill roots, catalogs, resource files and output budgets are
bounded in code. Errors are one JSON object with `status:error` and a stable code.
Common nonzero classes: invalid/unsafe input `2`, unavailable/stale/corrupt state `3`,
conflict `4`, active writer contention `5`. A failed command does not silently weaken a
guard or install anything.
