# Host Portability

## Purpose

Use this reference when the target skill must work across multiple agent hosts or when the active host/runtime is uncertain. Keep the semantic workflow in the open Agent Skills core and isolate host-specific metadata, discovery paths, invocation syntax, and optional capabilities at the edges.

## Canonical portable core

Prefer the interoperable subset:

- one skill directory containing `SKILL.md`;
- YAML frontmatter with portable `name` and `description` fields;
- Markdown instructions in the body;
- optional `scripts/`, `references/`, and `assets/` using relative paths from the skill root;
- lowercase hyphenated skill name that matches the packaged root directory;
- scripts that are self-contained, emit useful errors, and do not depend on a particular agent brand.

Do not make correctness depend on a host-only frontmatter field or metadata file unless the user explicitly requests a host-specific skill.

## Host adapters

| Host | Typical project discovery | Typical user/global discovery | Adapter notes |
|---|---|---|---|
| ChatGPT / Codex | Codex supports `.agents/skills/`; ChatGPT can install/upload packaged skills | product-managed installation; Codex also has user/admin/system scopes | `agents/openai.yaml` is optional OpenAI metadata for UI, invocation policy, and tool dependencies. It is not part of the portable semantic core. |
| Claude / Claude Code | `.claude/skills/<name>/` | Claude-managed/custom-skill surfaces vary by product | Claude supports the Agent Skills format and may support host-specific frontmatter such as tool permissions. Preserve such fields when they are intentional, but do not require them for portable behavior. |
| GitHub Copilot | `.github/skills/`, `.claude/skills/`, or `.agents/skills/` | `~/.copilot/skills/` or `~/.agents/skills/` | Copilot uses Agent Skills across cloud agent, code review, CLI, app, and IDE agent mode. |
| Cursor | `.agents/skills/` or `.cursor/skills/` | `~/.agents/skills/` or `~/.cursor/skills/` | Cursor also discovers compatible Claude/Codex skill directories. Cursor-specific fields such as `paths` are extensions, not portable core requirements. |

Discovery locations change faster than the core specification. If installation layout is part of the requested deliverable, verify the current official host documentation before changing package structure.

## Capability contract

Branch on capabilities first, product name second. Record at least:

1. **filesystem-read** — can the host read the target package and references?
2. **filesystem-write** — can it preserve a baseline and write a candidate/work directory?
3. **python-3.10+** — can it execute the bundled standard-library validators?
4. **command-execution** — can it invoke local scripts and subprocesses?
5. **network/research** — is current external documentation reachable when freshness matters?
6. **subagents/evaluators** — can independent comparison arms run, or must behavioral claims be limited?
7. **artifact-delivery** — can the host return or persist a ZIP/report artifact?

Do not claim a gate passed when the capability required to run it is absent.

## Python execution

The bundled scripts require Python 3.10+ and use the standard library only. Resolve `<PYTHON>` using the host's execution environment instead of hard-coding an executable name. Common CLI spellings include `python3`, `python`, and Windows `py -3`, but the host may expose Python through a code-execution tool rather than a shell command.

After Python starts, scripts must use `sys.executable` for child Python processes and `pathlib` for filesystem work. Avoid Bash-only pipelines, shell-specific quoting, POSIX-only utilities, hard-coded `/tmp` paths, and Windows-only path assumptions inside the skill contract.

## Host-specific metadata rules

- `agents/openai.yaml`: optional OpenAI adapter. Validate it only when using an OpenAI delivery profile or when the file exists and its syntax/content is being reviewed.
- Claude-specific frontmatter such as `allowed-tools`, `model`, or invocation fields: preserve when semantically intentional; do not add them to the portable core merely for convenience.
- Cursor-specific `paths`: preserve when the skill intentionally scopes itself to files; treat it as a host extension.
- GitHub provenance fields written by `gh skill`: treat them as distribution metadata, not workflow semantics.

A portable skill may contain host-specific adapters, but the same core behavior must remain understandable and executable when those adapters are ignored.

## Portable packaging rules

1. Validate the host-neutral core with `scripts/validate_target_package.py --profile portable`.
2. Use `--profile openai` only when OpenAI metadata is required by the delivery target.
3. Package with `scripts/package_target.py`; the archive root must come from `SKILL.md:name`, not from a temporary staging-directory name.
4. Keep a single root skill; no nested archives or escaping symlinks.
5. Freeze and hash the exact candidate that is packaged.

## Degraded execution

If the host can read files but cannot execute Python:

- `audit-only` and `plan-only` may continue with manual structural inspection;
- `apply` may continue only for changes whose safety can be established without the missing gate;
- script-based validation, frozen-evaluator verification, and package validation must be reported `not-run`;
- do not label the result `reproducibility-hardened` unless all applicable hard gates actually ran and passed.

## Official sources to re-check when host behavior matters

- Agent Skills specification: `https://agentskills.io/specification`
- OpenAI skill authoring: `https://developers.openai.com/docs/build-skills`
- GitHub Copilot agent skills: `https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills`
- Cursor Agent Skills: `https://cursor.com/docs/skills` (or the current Cursor documentation route)
- Anthropic Agent Skills repository/spec pointer: `https://github.com/anthropics/skills`

Treat these URLs as source pointers, not as frozen truth. Re-verify unstable product-specific details when the user's request depends on current behavior.
