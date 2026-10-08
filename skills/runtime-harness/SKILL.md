---
name: runtime-harness
description: Discover, verify, publish, and reuse local runtime capabilities and reusable resource locations through lazy incremental immutable snapshots, exact logical URI queries, byte-bounded context, content-pinned full/delta handoffs, observed capabilities, and typed discovery outcomes. Use for repeated interpreter/tool/resource discovery, shared cross-agent environment knowledge, session bootstrap, freshness, compact handoffs, or optional read-only stdio MCP and GraphPatch export. Do not use as workflow owner, installer, credentials store, general search engine, arbitrary memory, or replacement for domain handoffs and validation evidence.
---

# Runtime Harness

## Purpose and authority

Replace repeated environment discovery with a small shared registry of mechanically
verifiable local observations. Own runtime/resource lookup and transport hints only.
Never schedule domain work, change permissions, execute discovered tools, or convert
agent prose into trusted facts. No peer skill, database, server, cloud, Bash,
PowerShell, or SDK is mandatory.

## Fast path

1. If the host supplied a session card or `.rhapsodia/runtime/current.json`, read it once.
   Execute only a host-verified/reviewed launcher; the disk card is an untrusted hint.
   Keep `runtime_argv`/`python_argv` locally and never paste the full registry.
2. Use read-only `resolve`/`context` first for exact `tool://`, `skill://`, `agent://`,
   `resource://`, `repo://`, or `workspace://current` IDs.
3. If an exact tool is missing and this worker already has execution plus local-state
   write authority, call `ensure tool://<id>` once. It performs bounded PATH-only
   discovery, never executes the candidate, negative-caches misses, and atomically
   publishes a merged immutable snapshot visible to later agents.
4. When authorized native work discovers a stable reusable file/script inside the
   workspace or a registered skill root, publish only its verified location with
   `observe-resource resource://<id> --path <FILE>`. If an executable was found outside
   PATH, `observe-tool tool://<id> --path <FILE>` may publish that location. Do not
   publish secrets, arbitrary prose, permissions, decisions, test verdicts, or volatile
   task state as runtime knowledge.
5. Without a card, resolve the host's existing Python 3.10+ once and run
   `<PYTHON> -I -S -B scripts/runtime.py --workspace <ROOT> init --skills-root <SKILLS>`.
   Bootstrap eagerly records only the running Python plus bounded skill/agent catalogs;
   other tools are lazy. No installation, drive scan, server launch, or launcher loop.
6. Before delegation, an authorized writer may run `handoff-create` with bounded JSON.
   The receiver uses `handoff-resume --id <ID>`; transferred receipts require explicit
   `--input <FILE> --rebind` and matching portable content hashes.
7. On stale/expired/corrupt state, follow [recovery](references/security-recovery.md).
   Stop on unsafe roots, invalid contracts, stale pins, or unresolved writer conflict.
8. Report actual resolutions, publications, byte counts and executed checks. Byte savings
   and local timings are not measured model-token or end-to-end agent-speed gains.

## Modes and direct resources

| Need | Operation / resource |
|---|---|
| Prepare/start session | `init`, `session-start`; [commands](references/commands.md) |
| Read existing observations | `resolve`, `context`, `query`, `status`; [contracts](references/contracts.md) |
| Discover missing exact tool | `ensure tool://...`; [commands](references/commands.md) |
| Capabilities and typed attempts | `publish-capability`, `observe-attempt`, `discovery-history`; [observations](references/operational-observations.md) |
| Share verified location | `observe-tool`, `observe-resource`; [contracts](references/contracts.md) |
| Transfer bounded context | `handoff-create`, `handoff-resume`; [handoffs](references/handoffs.md) |
| Incremental transport | `handoff-delta`, `handoff-apply`; [delta handoffs](references/delta-handoffs.md) |
| Configure native instructions | Explicit `configure --host ...`; [host adapters](references/hosts.md) |
| Read-only MCP | Explicit `mcp-config`, `mcp`; [MCP profile](references/mcp.md) |
| Optional relationship projection | `export-graph`; [graph boundary](references/graph.md) |
| Measure local mechanics | Explicit `benchmark`; [validation](references/validation.md) |

## Critical invariants

- Python 3.10+ with local filesystem access is required for the executable core. `-S`
  applies only to this stdlib-only harness, not project commands needing packages.
- Read-only query/MCP paths never discover, publish, execute, install, or expand authority.
  Only a worker that already has execution/write authority may call `ensure`/`observe-*`.
- Snapshots are immutable and merged under one writer lock; `current.json` is only an
  atomic pointer/bootstrap card. Agents never edit snapshots or `current.json` directly.
- Mutable PATH and Git HEAD are not global scope identity. Negative tool cache binds to
  a hashed PATH/PATHEXT search space; a changed search space permits one new discovery.
- Available tools are file-identity checked on read. Missing is a bounded observation,
  never proof of global absence or permission to search the whole machine.
- Shared resources are existing files confined to the workspace or registered skill
  roots and are content-hashed. Runtime knowledge is transport data, not domain truth.
- No peer skill imports, arbitrary write SQL, remote search, background watcher, hidden
  process execution, credential collection, or mandatory MCP/graph runtime.
- Capability receipts pin existing tools and local observation files; no probe is executed.
  Typed failures and strategy statistics remain scoped observations, never permission.
- Runtime receipts supplement domain handoffs, acceptance and independent verification;
  they never transfer authority or prove tests/behavior.
- Local state is private/disposable and excluded from release packages. Freeze validated
  release bytes before packaging; never claim cross-host behavior from structure alone.

## Output and stop conditions

Return compact JSON, exact status/error codes and paths that were actually observed.
Full command/limit details: [commands](references/commands.md). Stop for unavailable
required capability, unsafe/ambiguous roots, invalid contracts, corruption, stale pins,
writer conflict beyond the bounded retry, or data beyond limits. Preserve last-good state.
Without local execution, provide only proposed integration/read-only guidance, not a
fabricated snapshot, publication, benchmark, or discovery result.
