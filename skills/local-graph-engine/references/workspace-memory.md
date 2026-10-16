# Workspace memory and reusable environment recipes

## At a Glance

**Purpose:** Operate source-pinned workspace memory and diagnostic recipes.
**Load when:** Using lookup, learn, reconcile or recovering existing knowledge.
**Decision impact:** Preserve current-source authority, selective learning, recipe applicability, history and scoped writes.

## Contents

- Purpose and authority
- Commands
- Required graph-first loop
- Environment recipe contract
- Reconciliation and deletion
- Safety and completion

## Purpose and authority

Use this mode for persistent per-workspace references, learned relationships and recurring
troubleshooting. Rhapsodia agents require it unless the user explicitly disables graph use.
Standalone dataset workflows remain domain-neutral and do not require a harness or another
skill. The graph is evidence-backed working memory, not repository truth or authority.
Rebuildable source projections and non-reconstructible operational notes have different recovery
needs: preserve history and reviewed backups before any separately authorized destructive reset.

The stdlib CLI is `scripts/workspace_memory.py --workspace <ROOT> <COMMAND>`; use an approved
Python 3.10+ with `-I -S -B`. The fixed private database is
`.rhapsodia/graph/workspace.sqlite3`. No installation, server, watcher or project command runs.

## Commands

| Command | Behavior |
|---|---|
| `start` | Idempotently create/reuse a real scoped graph and check integrity |
| `status` | Read-only scope/integrity check; never initializes absent state |
| `lookup "<question/symbol/path/error>"` | Bounded indexed-knowledge query with fresh source checks |
| `lookup "<text>" --key <KEY> --budget-bytes 8192` | Exact key, bounded context; no repository scan |
| `pin <relative-file> [<relative-file> ...]` | Read-only source SHA-256 pins, maximum 16 files |
| `learn [--input <JSON>]` | Validate pins, then atomically publish one typed note; otherwise stdin |
| `reconcile [--paths <relative-file> ...]` | Check tracked references, persist invalidation, keep history |
| `reconcile --prune-missing --confirm-complete-scope` | Remove only confirmed missing single-source references |
| `import-runtime [--input <JSON>]` | Apply a runtime-owned GraphPatch; not arbitrary execution |

`lookup` does not create directories or modify the database. Its `coverage` is always
`indexed-knowledge-only`; `truncated` means a bounded result, not proof of completeness. The
budget is 1024..65536 UTF-8 JSON bytes, not a model-token estimate. Candidate retrieval is
bounded to 128 records; narrow queries/keys when truncated. Reconciliation filters up to
256 exact `--paths` before its 1024 matching-record cap, so unrelated graph growth does not
block focused maintenance. Broader selections fail explicitly; no repository scan occurs.

## Required graph-first loop

The objective is useful verified reuse across agents and sessions, not a ritual or a record
quota. Reuse a lookup for the same question/scope and unchanged evidence within the task;
refresh after source/environment drift. Retrieve only relevant compact context. Query before
broad keyword search or retrying a known failure. For a fresh sufficient hit,
read the exact referenced source rather than searching again. Recheck live pins, environment
and declared shell/tool applicability. On a miss, stale hit, insufficient coverage or a new
relationship, inspect only the unresolved repository scope, then add useful reusable evidence.
Do not index every file or duplicate transcripts merely to claim completeness. Keep necessary
source reads and independent proof. Apply the [learning filter](workspace-learning.md): one
specific reusable question per stable record, actual evidence status, no duplicate writes.
If nothing qualifies, report `no-new-reusable-knowledge` with its reason. No relevant lookup
topic does not disable the mandatory enclosing agent-session gate.

References require nonempty sources with exact relative `path` and `sha256`. Read first, obtain
`pin`, and build `workspace-knowledge-v1` input using the actual observed pins. A changed pin
blocks publication rather than silently blessing a new source. Stable keys deduplicate notes;
updates require `expected_revision` from lookup. Keys `root` and `workspace` are reserved.
Shared-source edges use `supported-by`; other semantic relations can use the existing general
GraphPatch interface with their own evidence. Do not infer calls, ownership or causality from
similar labels. Include source-owned references when learning repository flows.

## Environment recipe contract

The direct schema is [workspace-knowledge-v1](../contracts/workspace-knowledge-v1.schema.json).
A `remedy` requires `symptom`, `cause`, `resolution`, `verification`, `evidence_status`,
`applicability`, `environment_variables` and `ttl_seconds`, in addition to common fields.
Sources may be empty for an explicitly agent-reported environment observation. Such a note
is not independently verified; lookup labels its `evidence_basis` as `agent-reported`.

Supported status: `observed-success`, `documented`, `hypothesis`, `failed`, `auth-required`.
Only fresh observed-success/documented notes are reuse candidates, still requiring present
applicability checks and authorization. Hypotheses and failed attempts remain visible to avoid
repeated blind retries. Never turn a documented example or unexecuted suggestion into a fix.
Record shell family/version/language mode, tool/version or configuration preconditions as
needed; `environment_variables` contains names only. The helper records an environment digest
and expiry (60 seconds..30 days), not values. Changed PATH/host/interpreter or expired time
invalidates reuse. Shell/profile/tool-specific changes also require the caller's applicability
check; the helper does not inspect interactive authentication or the parent shell's state.

Examples: PowerShell syntax/version constraints, ConstrainedLanguage restrictions, Git
ownership/lock failures, missing dependencies, expired SSO, tool locations and configuration
variable names. Never automatically login, install, disable execution policy, trust every Git
directory, delete live locks or run recipe text. Templates are advice, never a command queue.
The [documented PowerShell example](../examples/workspace-remedy.json) is not measured evidence.

## Reconciliation and deletion

Changed, missing, inaccessible, expired or environment-mismatched notes are not fresh facts.
Refresh changed knowledge from current source evidence using revision control. A failed search,
branch switch, sparse/partial checkout or permission error is not deletion evidence. Default
reconciliation invalidates, never prunes. Explicit complete-scope pruning removes only a
confirmed missing single-source reference; multi-source knowledge and source revision history
remain. Review broader cleanup through the graph's existing source-history tools.

## Safety and completion

Writes use a finite non-stealing writer lock and the engine's atomic GraphPatch transactions.
Never replace corrupt, foreign-workspace, symlinked or hard-linked state. Protected sources,
credentials, environment values, raw logs and suspicious secret assignments are rejected;
producer-side sanitization remains required. Files over eight MiB and oversized requests fail
rather than silently truncating evidence. Private state stays out of release artifacts.

Before handoff/return, learn reusable discoveries and reconcile touched references; report keys,
revisions and blockers compactly. Missing required publication blocks an unqualified completion
claim, not preservation of completed work. Graph hits never replace fresh tests or independent
proof. No native-host adherence or measured token reduction follows from CLI/structural tests.

A stale remedy is renewed only after checking applicability and re-verifying the outcome,
then publishing the current `expected_revision`. Identical fresh records remain no-ops;
identical stale recipes cannot silently reset their environment identity or expiry.
