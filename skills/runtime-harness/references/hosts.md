# Native host adapters

## Portable core

The core uses Python 3.10+ standard library, filesystem operations and argv arrays. It
does not require Bash, PowerShell, a package manager, daemon, database, cloud service or
host-private SDK. Windows/Linux/macOS differences are confined to bounded executable
lookup rules (PATH/PATHEXT versus POSIX execute bits) and optional bootstrap launchers.

The repository wrapper is `scripts/runtime.py`; a standalone skill uses its own
`scripts/runtime.py`. The host must provide one already-available Python or an explicitly
reviewed optional launcher. The harness cannot discover the interpreter required to run
itself without any execution capability.

## Managed instruction adapters

`configure --host ...` writes a short managed block while preserving unrelated content:

| Host | File |
|---|---|
| generic / Codex | `AGENTS.md` |
| Copilot | `.github/copilot-instructions.md` |
| Claude | `CLAUDE.md` |
| Cursor | `.cursor/rules/rhapsodia-runtime.mdc` |

The block tells agents to:

1. reuse existing exact observations first;
2. keep `resolve/context` read-only;
3. when already execution/write-authorized, use `ensure tool://<id>` for exactly one
   missing tool instead of repeated native probing;
4. publish a stable reusable file location with `observe-resource` only after authorized
   native work already found it;
5. never publish arbitrary prose, permissions, decisions, secrets or test verdicts.

Configuring instructions does not prove a host loaded them and does not grant tools.

## Session-start

A trusted host-native setup may run `session-start` before model work and inject the small
card once. Repeated subagents should reuse the same current pointer/registry. The host may
still discover new requested tools later through `ensure`; this produces a new immutable
snapshot without rerunning session bootstrap.

`session-start --format vscode-local` emits the documented Local `SessionStart` envelope.
Other hosts have their own hook formats; do not copy that envelope and claim compatibility.

## Optional launchers

`bootstrap.sh` and `bootstrap.ps1` are bounded conveniences. They try only known Python
launcher forms or explicit `RHAPSODIA_PYTHON`, never install Python, scan drives or change
execution policy. They are not dependencies of the Python core.

## MCP

`mcp-config` emits reviewed command/args for the optional local stdio MCP. MCP remains
read-only and intentionally cannot `ensure` or `observe-*`. A host that wants autonomous
publication must already expose authorized local command execution outside the MCP reader.

## Evidence boundary

Repository CI contains Windows/Linux/macOS lanes, but source configuration is not proof
that each target host was executed for the exact package. Report actual platform runs
separately from structural portability.
