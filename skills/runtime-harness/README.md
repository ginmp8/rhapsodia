# Runtime Harness 1.1.0

A stdlib-only local runtime registry bundled with RhapsodIA 0.7.0. It is intentionally
**lazy and incremental**: bootstrap records only the running Python plus bounded
skill/agent catalogs. Agents discover exact missing tools only when needed and can
publish mechanically verifiable reusable resource locations for later agents.

The registry is shared through immutable snapshots under `.rhapsodia/runtime/`.
Agents never edit `current.json` or snapshots directly; writers merge observations and
atomically move the pointer to a new content-identified snapshot.

## Start

```text
python -I -S -B scripts/runtime.py --workspace . init
python -I -S -B scripts/runtime.py --workspace . resolve tool://python skill://runtime-harness
```

For another workspace, supply the installed skills directory explicitly:

```text
<PYTHON> -I -S -B <RUNTIME_SCRIPT> --workspace <PROJECT> init --skills-root <SKILLS_ROOT>
```

## Lazy tool discovery

`resolve` never searches. An execution-authorized worker can request one bounded
discovery when a tool is actually required:

```text
<PYTHON> -I -S -B <RUNTIME_SCRIPT> --workspace <PROJECT> ensure tool://dotnet
<PYTHON> -I -S -B <RUNTIME_SCRIPT> --workspace <PROJECT> ensure tool://docker
```

`ensure` searches only the explicit current `PATH` (plus `PATHEXT` on Windows), never
executes the candidate, and publishes the observation for all later agents. Missing
results are negative-cached. A changed search-space fingerprint invalidates only that
negative observation; it does not invalidate the whole runtime snapshot.

If native work already found an executable outside PATH, share its verified location:

```text
<PYTHON> ... observe-tool tool://custom-tool --path <EXECUTABLE>
```

## Share reusable resources

If an agent finds a stable file/script that later agents would otherwise search for
again, it may publish a typed local resource:

```text
<PYTHON> ... observe-resource resource://validation/main --path <WORKSPACE>/scripts/validate.py
<PYTHON> ... resolve resource://validation/main
```

Resources must be regular files inside the workspace or a registered skill root. Their
live bytes are hashed on resolution/handoff. The registry never accepts arbitrary prose,
permissions, domain decisions, test verdicts, secrets, or conversation history as
shared runtime knowledge.

## Session preparation

```text
<PYTHON> -I -S -B <RUNTIME_SCRIPT> --workspace <PROJECT> session-start
```

A configured host can inject the small result once before model work. `configure --host`
supports generic/Codex, Copilot, Claude and Cursor instruction surfaces. This does not
install hooks, start services, or expand model permissions.

## Handoff

```text
<PYTHON> ... handoff-create --input <REQUEST>
<PYTHON> ... handoff-resume --id <RETURNED_ID>
```

Receipts may pin tools, skills, agents, repository files, shared `resource://` files and
the workspace identity. They verify identity only; they do not transfer workflow ownership,
permission, compatibility or test success.

## Design boundary

- `resolve`, `context`, query and MCP are read-only.
- `ensure`, `observe-tool`, `observe-resource`, init/configuration and handoff creation
  require whatever execution/write authority the host already granted the caller.
- No cloud, database, background watcher, package manager, shell or peer skill is required.
- Optional GraphPatch export is a derived relationship projection, never the fast lookup path.
- Exact byte counts are not measured model-token savings.

See [commands](references/commands.md), [contracts](references/contracts.md),
[handoffs](references/handoffs.md), [host adapters](references/hosts.md),
[security/recovery](references/security-recovery.md), and [validation](references/validation.md).
