# Host Compatibility Contract

Use this reference whenever the target host matters or a multi-platform claim is requested. The portable core follows the open Agent Skills package model; host-specific files are optional adapters, never prerequisites for the core workflow.

## Portable core

Require only:

- one skill directory whose name matches `SKILL.md` `name`;
- `SKILL.md` with `name` and `description`;
- package-local relative references;
- optional `scripts/`, `references/`, and `assets/`;
- scripts whose dependencies and failure modes are explicit;
- no vendor-private tool names, sandbox paths, or installation directories in the core workflow.

Keep the core frontmatter on the common denominator. `name` must be lowercase hyphen-case, at most 64 characters, and match the parent directory. `description` must be non-empty, at most 1024 characters, and state what the skill does and when to use it. Avoid host-specific frontmatter in the portable core. `allowed-tools` exists in the open specification but is experimental and varies by implementation, so do not rely on it for correctness or permission bypass.

## Host profiles

| Profile | Discovery/distribution notes | Adapter policy | Important constraints |
|---|---|---|---|
| `openai` | ChatGPT/OpenAI skill surfaces consume the same Agent Skills-compatible package. | `agents/openai.yaml` is optional and may define OpenAI UI/policy/tool metadata. The core must still work without it. | Do not put OpenAI-private tool names or sandbox paths in `SKILL.md`. |
| `codex` | Codex consumes Agent Skills-compatible directories; repository/user discovery location is a host concern. | No separate semantic fork is required. OpenAI metadata remains optional. | Do not make Codex-specific discovery paths or tool names a semantic dependency. |
| `claude` | Claude Code discovers `.claude/skills/` and `~/.claude/skills/`; claude.ai/API can accept custom skill packages. | No OpenAI adapter is required. | Claude API skill containers may have no network and no runtime package installation; keep bundled helpers self-contained. Claude reserves `anthropic` and `claude` in skill names. |
| `copilot` | GitHub Copilot supports project skills in `.github/skills`, `.claude/skills`, or `.agents/skills`, and personal skills in `~/.copilot/skills` or `~/.agents/skills`. | No extra package file is required. | `allowed-tools` can pre-approve shell access; omit it from this portable skill so permissions remain host/user controlled. |
| `cursor` | Cursor discovers `.agents/skills`, `.cursor/skills`, user equivalents, and compatibility locations including `.claude/skills` and `.codex/skills`. | Cursor-specific fields such as `paths` or `disable-model-invocation` are optional host extensions and should not be required by the portable core. | Cloud/remote agents do not necessarily inherit unsynced local user skills. |

`.agents/skills` is a useful repository-level interoperability location for Codex, Copilot, and Cursor. Claude Code documents `.claude/skills`; distribute the same skill directory there rather than maintaining a forked `SKILL.md`. Installation location is a host concern, not package logic.

## Capability model

Resolve capabilities before execution instead of branching on vendor name:

1. **read-files**: can the host read the target package and bundled references?
2. **write-files**: can it mutate the target in the allowed scope?
3. **run-processes**: can it execute deterministic helpers?
4. **python3**: is a Python 3 runtime available?
5. **invoke-specialists**: can the host actually dispatch another named skill/agent, or only apply a checklist?
6. **network**: only required by a target-specific evaluator; Skill Booster's bundled validators do not require it.

Classify missing capabilities as `blocked` or `unavailable`. Never translate missing execution into a fabricated `pass`.

## Python launcher policy

Bundled helpers require Python 3.10+ and no third-party Python packages; they use the standard library plus bundled sibling modules. The active host may expose Python as `python`, `python3`, `py -3`, an absolute interpreter path, or an execution tool that accepts the script directly. Resolve one launcher and denote it as `<PYTHON>` in reports/instructions. Record the exact command used.

Scripts that invoke sibling scripts must use `sys.executable`; they must not spawn a hard-coded `python` or `python3`. If Python is unavailable, deterministic script gates are `blocked`; checklist-only review may provide observations but cannot satisfy a script-required readiness claim.

## Specialist invocation policy

Specialist names describe capabilities, not APIs. A host may invoke them through native skill selection, subagents, CLI commands, plugin tooling, or no delegation mechanism at all.

- When a specialist was actually dispatched, record `execution_type: invoked-skill`.
- When only its documented checklist was applied, record `execution_type: checklist-only`.
- When the host cannot dispatch it, use `unavailable` or `blocked` as appropriate.
- Never place implementation-specific calls such as private tool function names in the target skill.

## Host adapter isolation

Host-specific metadata may coexist with the portable package when it is optional and ignored safely elsewhere. For this package:

- `agents/openai.yaml` is the OpenAI adapter.
- There is no duplicated Claude/Copilot/Cursor `SKILL.md`.
- Do not add Cursor-only frontmatter, Copilot `allowed-tools`, or Claude-specific paths to the portable core merely to advertise compatibility.

## Portability acceptance

The deterministic packager normalizes ZIP timestamps and permission bits, avoiding archive drift caused only by Unix/Windows mode metadata. Candidate file bytes are not rewritten; runtime behavior and checkout line-ending transformations remain separate concerns.

For `complete optimization`, the default structural matrix is `portable-core,openai,codex,claude,copilot,cursor`. Individual runtime behavior may still be `not-run` or capability-limited.

A multi-platform claim requires:

1. structural validation passes;
2. `scripts/validate_portability.py` passes for every claimed host;
3. no core instruction requires a vendor-private API;
4. host adapters are optional and valid for their host;
5. required runtime capabilities are available or explicitly reported as blocked;
6. runtime/behavioral claims remain separate from structural portability.

## Sources verified 2026-09-19

- Agent Skills specification: https://agentskills.io/specification
- OpenAI skills: https://developers.openai.com/docs/build-skills
- Claude Agent Skills: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- GitHub Copilot agent skills: https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills
- Cursor Agent Skills: https://cursor.com/docs/skills
