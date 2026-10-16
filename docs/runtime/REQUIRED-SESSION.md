# Required sessions and memory in RhapsodIA 0.11.0

## Ownership and defaults

All eight profiles require a valid harness and local graph before task work. This includes
Supervisor, Analyst, Verifier, Nomia, Mago, Magia, Workspace and the new **Rhapsodia Adhoc**.
Adhoc selects and executes relevant installed skills inline; it has no subagent orchestration.
Supervisor retains governed lifecycle coordination. Existing domain authority is unchanged.

| Component | When and why |
|---|---|
| Runtime Harness | Every agent session: environment identity, tool/resource shortcuts, shared observations |
| Local Graph Engine | Every agent session: graph-first source lookup, reusable knowledge and diagnostic recipes |
| Rhapsodia Workspace | Only requested artifact catalogs/views; not initialization, runtime discovery or memory |
| Operational Context | Optional bounded packs/evidence reuse; cannot override required graph-first policy |

Only explicit user instructions can independently disable harness and/or graph for that request.
Missing skills, execution, permissions or valid state are blockers, not implied opt-outs.

## Run

From the source repository with an approved interpreter:

```text
python -I -S -B scripts/session.py --workspace <PROJECT_ROOT> --skills-root <APPROVED_SKILLS_ROOT>
```

Installed profiles discover `runtime-harness/scripts/agent_session.py` natively; they do not
require the source repository or this documentation. The adapter returns `runtime_argv` and
`memory_argv`, creates missing state and reuses valid state without a full repository scan.
The files are `.rhapsodia/runtime/current.json` and `.rhapsodia/graph/workspace.sqlite3`.

Explicit opt-out examples append `--no-graph --opt-out-reason user-request`,
`--no-harness --opt-out-reason user-request`, or both. No switch is persisted globally.

## Working loop

1. Require successful bootstrap before searches, project commands or delegation.
2. Query graph first. Read fresh exact references; search only unresolved source scope.
3. Pin and learn new useful definitions, relationships, configuration and verified remedies.
4. Resolve/ensure exact runtime tools rather than repeatedly probing the environment.
5. Reconcile touched sources and report compact session/knowledge evidence before return.

A graph miss never means the repository lacks the object. A source hash verifies content,
not correctness of a semantic claim. Inspect the source before changing its behavior. A stale
or truncated hit must not replace fresh inspection, acceptance or independent verification.

## Environment problems

Store normalized symptom, cause or hypothesis, applicable shell/tool/version, resolution,
verification and outcome. Store environment-variable names, not their values. Record actual
SSO/login as `auth-required` until an authorized human completes it; no credential material,
device-code URLs, raw logs or account identifiers belong in reusable recipes.

PowerShell `&&` is supported from version 7; Windows PowerShell 5.1 needs supported conditional
syntax. A plain semicolon is not equivalent because it does not preserve success gating.
ConstrainedLanguage is a policy constraint: choose permitted operations or escalate to the
administrator; never bypass it. Git ownership/lock errors and missing tools likewise require
diagnosis and authorization, not global trust changes, lock deletion or blind installation.

## Permissions and evidence limits

The local-maintenance exception is limited to reviewed helper operations writing private
`.rhapsodia/runtime` and `.rhapsodia/graph` state. Supervisor/Analyst remain domain-read-only.
VS Code's execute capability is coarse; prompt scope is not an OS sandbox or command allowlist.
Retain native tool approval. A restricted host must block unsupported maintenance rather than
pretend it happened. Structure/CLI tests do not prove compliance by every model or host.

Default reconciliation invalidates missing/changed references. Pruning requires confirmed
complete scope and applies only to missing single-source records; source history survives.
Do not prune from partial search, branch changes, sparse checkout or inaccessible paths.

## Direct references

- [Agent session adapter](../../skills/runtime-harness/references/agent-session.md): commands, opt-outs, partial failures and scope.
- [Workspace memory](../../skills/local-graph-engine/references/workspace-memory.md): learning, query, expiry, revision and pruning.
- [Knowledge schema](../../skills/local-graph-engine/contracts/workspace-knowledge-v1.schema.json): strict typed input.
- [Agent architecture](../agents/ARCHITECTURE.md): lifecycle owners, Adhoc, delegation and current control-plane rules.

## Primary reference sources

Behavioral guidance was checked against Microsoft PowerShell `about_Pipeline_Chain_Operators`
and `about_Language_Modes`, AWS CLI IAM Identity Center configuration, and VS Code custom-agent
documentation on 2026-10-16. Exact URLs and scope are recorded in the accompanying
[reference notes](REQUIRED-SESSION-SOURCES.md). These documents support guidance, not a claim
that Windows, SSO or native agent sessions were executed in the validation environment.
