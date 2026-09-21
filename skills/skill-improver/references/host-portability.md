# Host Portability

Use when the target or improvement workflow must work across ChatGPT/Codex, Claude, GitHub Copilot, Cursor, or another Agent Skills-compatible host. `references/execution-runbook.md` owns concrete CLI examples; this file owns the portable runtime policy.

## Portable semantic core

Keep the semantic workflow independent of vendor-private runtimes:

- one Agent Skills directory with `SKILL.md` and portable `name`/`description` frontmatter;
- relative `scripts/`, `references/`, `assets/`, and optional `evals/`;
- lowercase hyphenated skill name and standard-library Python where practical;
- no correctness dependency on vendor-only metadata, CLI, install path, or path syntax.

`agents/openai.yaml` is an optional OpenAI adapter. Preserve intentional host extensions, but never make them prerequisites for the portable core.

## Capability-first execution

Detect capabilities, not product names: filesystem read/write, Python 3.10+ or equivalent code execution, command execution, network/research when freshness matters, independent evaluation, and artifact delivery. A missing capability downgrades only dependent checks to `not-run`/`blocked`; it never becomes an implicit pass.

## Python and filesystem rules

Use `<PYTHON>` for the host's available Python 3.10+ execution method. Scripts should use `sys.executable` for child Python, `pathlib` for paths, avoid Bash/POSIX-only semantic requirements and hard-coded temporary/drive paths, and return actionable errors for missing executables.

## Agent adapters

`scripts/skill_improver_loop.py` defaults to the generic `command` adapter; Codex is optional. Neither changes the semantic contract. The generic template is argv-tokenized without a shell and requires `{prompt}`; `{cwd}` and `{target}` are optional. Do not interpolate untrusted values into shell syntax. If a CLI cannot accept normal argv safely, use the host's native execution mechanism. See `references/execution-runbook.md` for exact invocations.

## Packaging and degraded execution

Package only the frozen skill folder; exclude caches, generated reports/evidence, secrets, old archives, and transient state; validate final contents and treat vendor metadata as optional unless the requested destination requires it. Read-only hosts may still support audit/plan work, but never claim script-dependent validation, evaluator verification, or reproducibility hardening when required execution did not run.
