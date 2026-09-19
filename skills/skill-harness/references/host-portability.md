# Host Portability

Use when the target skill must work across ChatGPT/OpenAI, Claude/Claude Code, GitHub Copilot, Cursor, or another Agent Skills-compatible host.

## Canonical portable core

Treat the open Agent Skills format as the source of truth for semantics:

- one skill directory containing `SKILL.md`;
- YAML frontmatter with portable `name` and `description`;
- optional standard `compatibility`, `license`, and `metadata` fields when useful;
- Markdown instructions in the body;
- optional `scripts/`, `references/`, and `assets/` addressed with relative paths from the skill root;
- lowercase hyphenated name matching the parent skill directory;
- scripts that do not depend on a product brand unless the skill itself is host-specific.

Do not make correctness depend on a host-only adapter or discovery path. Host-specific metadata may coexist with the portable core, but another host must be able to ignore it without losing the skill's semantic workflow.

## Capability-first execution

Branch on capabilities before product names. Record at least:

1. filesystem read;
2. filesystem write for `apply`/`package`;
3. Python 3.10+ for this harness's standard-library helpers;
4. command execution for deterministic gates;
5. network/current research when the selected mode requires it;
6. independent agents/evaluators when behavioral comparison needs them;
7. artifact delivery/persistence when a ZIP or report must be returned.

If a capability is absent, mark the dependent gate `not-run`; do not convert missing execution into a pass.

## Current host adapters and discovery

These are installation adapters, not semantic dependencies. Product-specific paths can change; verify official docs when installation layout is part of the requested deliverable.

| Host | Current discovery/adapter guidance |
|---|---|
| ChatGPT / OpenAI | Use the product-managed skill upload/install surface. `agents/openai.yaml` may provide OpenAI UI/policy metadata; keep it optional to the portable core. |
| Claude / Claude Code | Uses the Agent Skills format. Claude-specific frontmatter such as `allowed-tools` can be retained when intentional, but portable behavior must not require another host to understand it. |
| GitHub Copilot | Project skills are discovered under `.github/skills`, `.claude/skills`, or `.agents/skills`; personal skills under `~/.copilot/skills` or `~/.agents/skills`. |
| Cursor | Project skills are discovered under `.agents/skills` or `.cursor/skills`; user skills under `~/.agents/skills` or `~/.cursor/skills`. Cursor also discovers compatible Claude/Codex skill directories. Cursor-only `paths` is an extension, not a portable requirement. |

## Portable frontmatter rules

Use the Agent Skills constraints for the core:

- `name`: 1-64 characters, lowercase letters/numbers/hyphens, no leading/trailing/consecutive hyphen, matches parent directory;
- `description`: 1-1024 characters and states both what the skill does and when to use it;
- `compatibility`: optional in the open specification, at most 500 characters, but some host validators may not accept it; for maximum portability, keep runtime requirements in the body/reference unless every required host accepts the field;
- `metadata`: optional string-to-string map;
- `allowed-tools`: experimental; support varies by host.

Unknown host extensions must not silently become hard requirements for the portable profile.

## Python/runtime portability

Resolve `<PYTHON>` to whatever Python 3.10+ execution method the host actually exposes. Do not assume the executable is named `python` or that a Bash shell exists.

Bundled harness scripts should:

- use the Python standard library unless a dependency is explicitly declared;
- use `pathlib`/`os` rather than shell-only path manipulation;
- use `sys.executable` for Python child processes;
- avoid POSIX-only pipelines, hard-coded `/tmp`, Windows-only paths, or product-specific tool APIs;
- emit machine-readable errors and deterministic exit codes where practical.

## Validation profiles

`portable` is the default and validates only the host-neutral Agent Skills contract plus harness gates.

`openai`, `claude`, `copilot`, and `cursor` run the same portable core and may add profile-specific adapter checks. A host profile must never weaken the portable core merely to pass.

Use:

```text
<PYTHON> scripts/skill_harness_portability.py --target <TARGET_SKILL_PATH> --profile portable --output <report-dir>/portability.json
<PYTHON> scripts/skill_harness_validate.py --target <TARGET_SKILL_PATH> --profile portable --output <report-dir>/validation.json
```

Run additional host profiles when the delivery requirement explicitly names those hosts.

## Packaging rule

The ZIP is a delivery wrapper, not the semantic standard. Preserve a single canonical root directory named from `SKILL.md:name`, so extracting the archive recreates the required Agent Skills directory shape independent of the staging-folder name.

## Source pointers to re-check

- Agent Skills specification: `https://agentskills.io/specification`
- Anthropic Agent Skills: `https://github.com/anthropics/skills`
- GitHub Copilot Agent Skills: `https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills`
- Cursor Agent Skills: `https://cursor.com/docs/skills`
- OpenAI Skills overview: `https://openai.com/academy/skills/`

Treat product-specific discovery locations as current external facts, not frozen package truth.
