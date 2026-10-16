# RhapsodIA repository map

Canonical skills: `skills/`. Canonical agent profiles: `agents/`.
Release identity: `marketplace/catalog.json`; host manifests and `MANIFEST.json` are
generated projections. Preserve independent skill/schema versions.

## Mandatory session and memory

Every Rhapsodia agent must run `python -I -S -B scripts/session.py --workspace <ROOT>
--skills-root <APPROVED_SKILLS_ROOT>` before repository search, domain commands or delegation.
Installed agents locate `runtime-harness/scripts/agent_session.py` through native discovery.
Require actual ready receipts for `.rhapsodia/runtime/current.json` and the real Local Graph
Engine database `.rhapsodia/graph/workspace.sqlite3`. Missing state is initialized; valid
state is reused. Missing permission/capability or corrupt state blocks, never silent fallback.
Only explicit current-user opt-outs allow independent `--no-harness` and/or `--no-graph`
with `--opt-out-reason user-request`; propagate only that request's choice, not a global disable.

Use verified `runtime_argv` for exact resolve/context, bounded ensure and observed locations.
Use `memory_argv` for graph-first lookup; fresh hits lead to exact source reads, misses/stale
hits to bounded repository discovery. Pin and learn reusable references and sanitized
symptom/cause/resolution/verification/applicability recipes, then reconcile touched sources
before handoff/return. Never store credentials, environment values or raw logs. Partial
search, branch changes and permissions cannot prove deletion; preserve source history.

Private runtime/graph maintenance is allowed by all profiles only through reviewed helpers,
subject to host approval; domain authority does not expand. Supervisor/Analyst cannot run
project commands. Runtime/graph observations never replace domain handoffs, acceptance or
independent proof. Rhapsodia Workspace is optional artifact presentation, not memory bootstrap.
Rhapsodia Adhoc executes direct tasks and relevant skills inline without subagent orchestration.

## Validation and packaging

- Runtime: `python -I -S -B -m unittest discover -s skills/runtime-harness/tests -p 'test_*.py'`.
- Required sessions: `python -I -S -B -m unittest discover -s tests -p 'test_required_session*.py'`.
- Integration: `python -S -B -m unittest tests.test_runtime_integration`.
- Agent gates: `python -B scripts/validate_agents.py --target .`.
- Release: `python -B scripts/prepare_release.py --check`.

Use ordinary project interpreter settings for tests needing installed packages; `-S` is for
stdlib-only helpers, not arbitrary product commands. Never commit `.rhapsodia/`, credentials
or execution snapshots. Direct guidance: `docs/runtime/REQUIRED-SESSION.md`.
