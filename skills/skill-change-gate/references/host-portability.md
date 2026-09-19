# Host Portability Contract

## Purpose

Keep `skill-change-gate` and the skills it reviews portable across Agent Skills-compatible hosts. Treat the open Agent Skills format as the semantic core and isolate host-specific discovery paths, metadata, invocation syntax, and capabilities at the edges.

## Portable core

A portable skill should be understandable when the host sees only:

- one directory whose name matches `SKILL.md:name`;
- `SKILL.md` with portable `name` and `description` frontmatter;
- Markdown instructions;
- optional `scripts/`, `references/`, `assets/`, examples, tests, or evals referenced with relative paths;
- self-contained scripts with explicit runtime requirements and useful errors.

Do not make correctness depend on a host-only metadata field, private tool name, absolute sandbox path, or another installed skill.

## Host adapters

Host-specific adapters may coexist with the portable core when they are optional.

| Host | Common discovery / delivery | Portability treatment |
|---|---|---|
| ChatGPT / OpenAI | packaged/uploaded skills; OpenAI runtimes may consume `agents/openai.yaml` | Treat `agents/openai.yaml` as an optional adapter. Core behavior must not depend on it. |
| Claude / Claude Code | custom skill ZIP/API and `.claude/skills/<name>/` | Keep core in standard `SKILL.md`; do not require Claude-only fields for semantics. |
| GitHub Copilot | `.github/skills/`, `.claude/skills/`, `.agents/skills/`; user scopes may use `~/.copilot/skills/` or `~/.agents/skills/` | Same portable package can be placed in a supported discovery directory. |
| Cursor | `.agents/skills/`, `.cursor/skills/`; user equivalents; compatible Claude/Codex directories may also be discovered | Cursor-only frontmatter such as `paths` is an extension, not a portable-core requirement. |

Discovery locations change faster than the format. When installation layout itself is part of the requested deliverable, verify current official host documentation before changing package structure.

## Capability-first execution

Before requiring a mechanical gate, determine whether the host can provide:

1. filesystem read;
2. filesystem write for reports/work directories;
3. Python 3.10+ or another compatible way to run the bundled helper;
4. command execution;
5. access to the before and after candidate bytes;
6. artifact/receipt access when delivery integrity is being gated.

Do not claim a script-based gate passed when the required runtime is unavailable. Continue with semantic/manual review only when that still supports a truthful decision; otherwise return `insufficient-evidence`.

## Python portability

`scripts/static_change_gate.py` uses the Python standard library only and targets Python 3.10+.

Resolve `<PYTHON>` from the active host instead of assuming one executable spelling. Examples include `python3`, `python`, Windows `py -3`, or a host code-execution tool. The contract must not depend on Bash, POSIX-only utilities, `/tmp`, `/home/...`, drive letters, or shell-specific quoting.

## Host-neutral review rules

Treat these as portability regressions when introduced into the semantic core without an explicit host-specific scope:

- internal tool identifiers such as a host connector function name;
- `skills://...`, `sandbox:/...`, or another private runtime URI as a required workflow primitive;
- absolute sandbox/user paths;
- mandatory dependency on `agents/openai.yaml`, Cursor-only frontmatter, Claude-only permissions, or another host extension;
- instructions that say a gate passed solely because one host auto-loaded a resource;
- scripts that require undeclared third-party packages when a standard-library implementation is practical.

Product names in descriptive text are not themselves portability defects. The defect is semantic dependence on one product's private mechanism.

## Portable gate profile

Use the static helper's portable profile for cross-host acceptance:

```text
<PYTHON> scripts/static_change_gate.py \
  --target <AFTER> \
  --before <BEFORE> \
  --profile portable \
  --policy <normal|strict|advisory>
```

Use `--profile openai` only when the delivery target specifically requires OpenAI adapter metadata. Passing the OpenAI profile does not make the skill less portable; making that adapter mandatory to the core would.

## Source pointers to re-check when current host behavior matters

- Agent Skills specification: `https://agentskills.io/specification`
- OpenAI Skills guidance: `https://openai.com/academy/skills/`
- GitHub Copilot agent skills: `https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills`
- Cursor Agent Skills: `https://cursor.com/docs/skills`
- Claude Agent Skills: `https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview`

Treat these as source pointers, not frozen installation truth.
