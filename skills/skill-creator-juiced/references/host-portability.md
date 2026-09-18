# Host Portability

Use this reference when creating or updating a skill for more than one host, when the target host is unknown, or when a host-specific feature could leak into the canonical workflow.

## Canonical portability target

Treat the open Agent Skills format as the canonical core:

```text
skill-name/
├── SKILL.md
├── scripts/      # optional
├── references/   # optional
├── assets/       # optional
└── ...           # additional package files when useful
```

The portable core must not depend semantically on a single vendor's UI metadata, install path, tool-call syntax, or agent runtime. Host-specific files may coexist as optional adapters when another host can safely ignore them.

## Common-denominator rules

1. Keep `name` and `description` valid under the Agent Skills specification.
2. Prefer only standard Agent Skills frontmatter in the canonical core. Use `license`, `compatibility`, `metadata`, or `allowed-tools` only when they add real value; `allowed-tools` is experimental and must never be required for correctness.
3. Use relative paths from the skill root for bundled resources.
4. Describe capabilities such as filesystem read/write, command execution, network access, subagents, connectors, browser access, and artifact delivery. Do not hardcode a vendor-specific tool name unless the skill intentionally targets that host.
5. Resolve runtime executables by capability. For example, resolve an available Python 3 interpreter instead of assuming `python` exists.
6. Keep validation claims capability-aware. Missing shell, Python, browser, network, subagents, or connectors means the affected gate is `not-run`, not passed.
7. Keep install locations outside the semantic contract. A skill folder should be movable without rewriting its instructions.
8. Do not duplicate the skill merely because hosts use different discovery directories.

## Host adapters

### OpenAI / ChatGPT / Codex

OpenAI documents support for the Agent Skills standard. `agents/openai.yaml` may be included as OpenAI-specific UI/dependency metadata, but portable behavior must not depend on it. Hosted/API packaging may use a zip archive; keep the archive rooted at one skill directory.

### Claude

Anthropic's Skills implementation and reference repository use `SKILL.md` skill folders and point to the Agent Skills specification. Claude-specific plugin metadata or install layout is an adapter concern, not part of the portable semantic core.

### GitHub Copilot / VS Code

Copilot discovers Agent Skills from supported project or personal skill directories and loads `SKILL.md` plus referenced resources. Installation location belongs to the consumer environment. Host-specific frontmatter such as UI hints or pre-approved tools must not become a cross-host correctness dependency.

### Cursor

Cursor supports Agent Skills and discovers skills from its own directories plus several compatibility locations. Cursor-only frontmatter such as `paths` is useful for Cursor scoping but narrows portability if core behavior depends on it. Prefer repository placement or explicit portable instructions over requiring `paths` in a multi-host skill.

## Host-specific extension policy

Classify every host-specific feature as one of:

- `optional-adapter`: safe to include because the portable core works without it;
- `optional-optimization`: improves one host but does not change semantics;
- `required-host-capability`: narrows the support matrix and must be declared;
- `portability-blocker`: the user requires equivalent multi-host behavior but no common or degradable implementation exists.

Do not silently convert a portable skill into a single-host skill.

## Packaging profiles

### `portable`

Default. Validate the Agent Skills core, relative references, package hygiene, and host-neutral semantics. Do not require `agents/openai.yaml`.

### `openai`

Use only when an OpenAI-specific package is explicitly requested. Run all portable checks, then require the OpenAI adapter expected by the package contract.

Other hosts normally consume the same portable folder in their supported discovery location. Do not create separate package contents unless host semantics genuinely differ.

## Current source anchors

Rules in this reference were aligned on 2026-09-18 with:

- Agent Skills specification: `https://agentskills.io/specification`
- OpenAI Skills guide: `https://developers.openai.com/api/docs/guides/tools-skills`
- OpenAI ChatGPT Skills help: `https://help.openai.com/en/articles/20001066`
- GitHub Copilot Agent Skills: `https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills`
- VS Code Agent Skills: `https://code.visualstudio.com/docs/agent-customization/agent-skills`
- Cursor Agent Skills: `https://cursor.com/docs/skills`
- Anthropic Skills repository: `https://github.com/anthropics/skills`

Host behavior can change. Recheck authoritative host documentation when a platform-specific feature is material to correctness.
