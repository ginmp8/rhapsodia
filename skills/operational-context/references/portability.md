# Portable execution and host surfaces

The canonical semantic core is this `SKILL.md` and self-contained Python 3.10+ scripts.
Optional `agents/openai.yaml` only controls display/discovery. No host-specific import,
absolute installation path, SDK, Bash requirement, model dependency, MCP dependency or
peer skill package is needed. Resolve the installed package via the host's native discovery.

| Semantic profile | Distribution surfaces | Actual dependency |
|---|---|---|
| portable-core | Any compatible Agent Skills host | Local read; execution/write only for selected commands |
| openai | ChatGPT, OpenAI API clients | Host exposes files/execution; metadata optional for core |
| codex | Codex | Native skill discovery and authorized execution |
| claude | Claude Code | Native skill discovery and authorized execution |
| copilot | VS Code, Visual Studio | Surface must support skills/local tools; do not assume identical discovery |
| cursor | Cursor | Native skill discovery and authorized execution |

These mappings describe package structure, not runtime certification. Local Linux/Python
and stdio behavior is tested during release; Windows/macOS matrix jobs are supplied but
must actually run before claiming those environments or IDEs were tested. No paid/native
model session was exercised by the package tests.

Read-only hosts can consume supplied packs and canonical evidence with native tools. A host
without execution cannot run the CLI or assert recomputed hashes; return not-run for that
layer. Missing optional context/cache support must not block a valid domain workflow.

Native prompt caching remains host-controlled. Stable-prefix output and provider-reported
usage adapters are available; no API setting, price, retention policy or hidden injected
prompt is assumed. Do not translate byte savings into token, billing or latency claims.

Shell-independent invocation uses an argv array with an already available interpreter.
Use `-I -S -B` for these stdlib-only scripts, not arbitrary project commands that need site
packages. No installation is performed to repair a missing interpreter.
