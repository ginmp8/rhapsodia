# Upgrade from RhapsodIA 0.7.0 to 0.8.0

## What changes

Install the complete 0.8.0 distribution together: 53 skills, seven agents and synchronized
marketplace manifests. Operational Context is new at 1.0.0; Runtime Harness is 1.2.0.
Other skill-local versions and canonical domain/agent-control contracts are unchanged.
No database, service, provider credential or additional Python dependency is required.

## Before switching

Keep the 0.7.0 source archive and any customized host instructions. Finish or stop active
writers before changing their executable/skill paths. Do not replace code under a running
worker. Keep `.rhapsodia/runtime/` and `.rhapsodia/cache/` out of source distributions.
Runtime snapshots contain local paths; they are not portable project assets.

## Install and refresh

Use the existing host installer/catalog process. No hooks are activated by unpacking.
For a full-repository installation, resolve Python 3.10+ and run the convenience launcher:

```text
<PYTHON> scripts/runtime.py --workspace <PROJECT> init --refresh
```

Supply the same registered roots/options used by the current installation when they are
needed. `init --help` lists the exact accepted arguments; do not guess root locations.
The standalone skill launcher is `skills/runtime-harness/scripts/runtime.py`.
Read-only consumers only consume an existing snapshot; they must not initialize it merely
because another worker could. Refresh is an authorized cache-writer operation.

The 1.2 reader accepts existing 1.1 snapshots at a consistent installation identity and
publishes additive catalogs only when needed. A changed installation root requires refresh.
A live handoff still validates its pinned source bytes. An old receipt never overrides a
required fresh or independent check.

## Optional host instructions

Explicitly opt in only when authorized:

```text
<PYTHON> scripts/runtime.py --workspace <PROJECT> configure --host <HOST>
```

Supported host keys remain `generic`, `codex`, `copilot`, `claude`, `cursor`. Configuration
preserves unmanaged text. It updates an unchanged owned managed block, rejects user-edited
or ambiguous blocks, and adds the two disposable directories to `.gitignore`. A conflict
requires review; do not delete user edits or force replacement automatically.

## Discover Operational Context

The helper is independent of Runtime Harness and can be used without it:

```text
<PYTHON> scripts/operational.py --workspace <PROJECT> describe --input <REQUEST_JSON>
```

Use `{}` for the small command inventory and `{"command":"pack"}` for one request schema.
Resolve paths from the selected project, not from the helper's installation directory.
Only explicit write commands create `.rhapsodia/cache/operational-context/`. Reading a pack,
querying an index, composing context or suggesting delegation does not execute tools.
Read the [standalone skill](../../skills/operational-context/SKILL.md) before selecting a mode.

## Protocol clients

Keep legacy MCP initialization unchanged for existing clients. The modern stdio profile is
selected per request by the documented 2026-07-28 metadata, not by a global unsafe protocol
switch. It does not add HTTP transport, OAuth, a shell tool or write methods. Tool-result
state is deliberately not cached by the catalog hint. Test the actual target client before
claiming deployment compatibility.

## Recovery and rollback

On stale/missing/corrupt helper state, use canonical files or rerun authorized discovery;
never infer success. Unknown publication locks are not automatically stolen. Stop writers,
confirm the lock owner is no longer active, preserve diagnostic metadata, and remove only
the disposable lock/cache under explicit local-maintenance authority.

The cache is bounded; offline pruning is a maintenance choice, not an automatic operation.
To roll back, stop writers and restore 0.7.0 including its agents/manifests. Do not expect the
1.1 runtime to read 1.2 snapshots. Rebuild disposable runtime/cache state under the restored
code, retaining any required canonical receipts elsewhere. No Nomia/Mago/Magia records,
approved plans, evidence gates or user instructions should be deleted during this process.
