# Required sessions and memory in RhapsodIA 0.11.0

## At a Glance

**Purpose:** Explain why every agent must reuse runtime observations and accumulate useful workspace knowledge, then show how to apply that rule without ritual queries or indiscriminate recording.
**Load when:** Starting a task, reviewing memory behavior, choosing what to learn, troubleshooting the environment or adapting host instructions.
**Decision impact:** Keep mandatory independent opt-outs, bounded maintenance authority, graph-first discovery, selective learning, source authority and honest proof. Fewer calls never justify weaker correctness.

## Contents

- Why these components are required
- Ownership and defaults
- Run
- Reuse and learning decisions
- Environment problems
- Completion and useful evidence
- Permissions, recovery and enforcement limits
- Direct references

## Why these components are required

Agents should not repeatedly pay for the same environment discovery, repository exploration,
troubleshooting or lost decisions. Harness retains verified runtime/resource observations;
Graph preserves structural knowledge and operational experience across agents and sessions
in the approved workspace. Reuse what is relevant and current before rediscovering it, then
retain new reusable findings for the next task. Initialization is not a ritual or success metric.

Structural memory answers where definitions, callers, dependencies and decisions live.
Operational memory explains what failed, why, what was tried, what worked and when it applies. Distinct source-pinned feature failures may be stored as advisory v2 execution lessons; a read-only `review-lessons` never authorizes changes to frozen criteria or prompts.
The repository and live environment remain authoritative. Graph-first changes discovery
order; it does not waive necessary source inspection, current acceptance or independent proof.

## Ownership and defaults

All eight profiles require valid harness and graph gates: Supervisor, Analyst, Verifier,
Nomia, Mago, Magia, Workspace and Rhapsodia Adhoc. Adhoc selects and executes relevant skills
inline without subagent orchestration; existing governed lifecycle ownership is unchanged.

| Component | Purpose and boundary |
|---|---|
| Runtime Harness | Reuse environment identity, exact tool/resource locations and discovery outcomes; not semantic memory or an installer |
| Local Graph Engine | Reuse references, relationships, rationale and diagnostic recipes; not canonical truth or an execution queue |
| Rhapsodia Workspace | Present existing producer-owned artifacts; optional, not memory bootstrap |
| Operational Context | Compose bounded temporary packs and eligible evidence references; cannot replace required gates |

Only the current user's explicit instructions disable harness and/or graph independently for
that request. Missing tools, permissions or valid state are blockers, not implied opt-outs.
Private memory is not automatically shared across unrelated workspaces, hosts or people.

## Run

From the source repository, using an approved interpreter:

```text
python -I -S -B scripts/session.py --workspace <PROJECT_ROOT> --skills-root <APPROVED_SKILLS_ROOT>
```

Installed profiles discover `runtime-harness/scripts/agent_session.py` natively. Minimal
approved launcher/helper discovery may precede the gate; ordinary project discovery may not.
Use the returned `runtime_argv` and `memory_argv`. Missing private state is created; valid
state is reused without a full repository scan. Require actual ready receipts for
`.rhapsodia/runtime/current.json` and `.rhapsodia/graph/workspace.sqlite3`.

Append `--no-graph --opt-out-reason user-request`, `--no-harness --opt-out-reason user-request`,
or both only when reflecting the explicit request. No switch is persisted globally; propagate
that selection to delegated work. Bootstrap again on a new task/resume or relevant drift.

## Reuse and learning decisions

| Situation | Action |
|---|---|
| Known tool/resource needed | Harness `resolve/context` first; bounded `ensure` or verified `observe-*` only when needed |
| New source question or recurring error | Graph `lookup` with the question, symbol, path or sanitized error signature |
| Same question/scope and unchanged evidence within the task | Reuse the existing lookup, not a new query for every adjacent read |
| Fresh relevant sufficient hit | Read exact authoritative references required for the task; avoid broad rediscovery |
| Missing, stale, truncated, irrelevant or insufficient hit | Narrow the query or inspect unresolved source scope; never force a match or infer absence |
| New useful finding | `pin` and `learn` one reusable question/answer per stable key, with actual status and provenance |
| Existing finding changes | Recheck evidence and update using `expected_revision`; do not duplicate or refresh expiry blindly |
| Sources/environment changed | Reconcile affected tracked sources and recheck applicability before reuse |
| No reusable new finding | Report `no-new-reusable-knowledge` and why; do not create filler records |

Learn relevant, repeatable knowledge that changes a future decision: component entry points,
callers/dependencies, canonical rationale, configuration prerequisites, verified remedies,
failed attempts and pending authentication requirements. Avoid trivia, whole files, raw logs,
transcripts, duplicate summaries and secrets. A source hash verifies bytes, not semantic truth.
For no relevant source/environment question, explain that lookup is unnecessary; bootstrap
still applies. All necessary safe learning updates must finish before handoff or completion.

## Environment problems

Store normalized symptom, confirmed cause or labeled hypothesis, resolution, verification,
evidence status, applicability and expiry. Store variable names and purpose, never values.
Useful categories include PowerShell syntax/language mode, Git locks/ownership/worktrees,
missing dependencies, expired SSO, tool locations and required configuration variables.

PowerShell `&&` starts in version 7; a plain semicolon does not preserve success gating.
ConstrainedLanguage is a policy constraint, not permission to bypass it. Git problems require
scope/active-operation checks, not blanket trust or blind lock removal. Missing tools require
verified discovery and existing installation authority, not automatic downloads.

Record pending login as `auth-required` until the authorized workflow completes; preserve no
tokens, account identifiers, device URLs or login material. Verify current shell/tool/profile
applicability before reuse. Documentation, a hypothesis or a failed attempt is not an observed
fix. Never repeat a materially identical failed strategy without new evidence.

## Completion and useful evidence

Return compact `session_memory` evidence alongside the task result: gate/opt-outs, useful
lookups, learned or updated keys/revisions, reconciliation and blockers. A no-new-learning
result is valid with a reason such as already-known, unchanged, not-reusable or unsafe-to-store.
These are reporting decisions, not new CLI enums or mandatory fabricated writes.

Judge useful verified reuse, not graph size or invocation counts. Observe useful retrieval,
source coverage, avoided repeat failures and correctness. Report bytes, provider tokens,
tool calls and elapsed time separately only when measured; unknown gains stay unknown.
Never use stored success or cache receipts to pass a new candidate's required proof.

## Permissions, recovery and enforcement limits

All profiles may maintain private runtime/graph state through reviewed helpers under host
approval. Supervisor/Analyst remain domain-read-only. No graph recipe grants permission for
installation, SSO, project commands, policy changes, external sharing or destructive work.

Missing/changed/inaccessible evidence is invalidated by default. Pruning requires confirmed
complete scope and only missing single-source records; history and other evidence survive.
Partial searches, sparse checkouts, branch changes and access failures do not prove deletion.
Rebuildable source indexes differ from learned experience that may have no independent copy:
preserve history and reviewed backups before any separately authorized destructive reset.

Agent instructions and static guards are not a universal tool interceptor. The installed
managed host guidance repeats these rules, but no hidden hooks or services are installed.
CLI checks do not prove compliance by every model or editor. Preserve native permissions
and report blocked capability; never claim an unsupported gate was enforced.

## Direct references

- [Agent session adapter](../../skills/runtime-harness/references/agent-session.md): exact commands, scope and failures.
- [Workspace memory](../../skills/local-graph-engine/references/workspace-memory.md): CLI, pins, revisions and reconciliation.
- [Learning criteria](../../skills/local-graph-engine/references/workspace-learning.md): selection, practical examples and recovery.
- [Knowledge schema](../../skills/local-graph-engine/contracts/workspace-knowledge-v1.schema.json): existing record types.
- [Agent architecture](../agents/ARCHITECTURE.md): role authority and lifecycle boundaries.
- [Primary operational sources](REQUIRED-SESSION-SOURCES.md): PowerShell, SSO and host guidance.
- [Research rationale](../research/shared-memory-purpose-0.11.0.md): bounded findings and exclusions; not startup reading.
