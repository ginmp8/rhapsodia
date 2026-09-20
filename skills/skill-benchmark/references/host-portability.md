# Host Portability Contract

Use this reference whenever the benchmark itself must run across hosts or the target skill claims multi-host support. Keep benchmark semantics in the open Agent Skills core and isolate host-specific metadata/discovery paths at the edges.

## Portable core

Require only:

- one skill directory containing `SKILL.md`;
- portable `name` and `description` frontmatter;
- relative package-local references;
- optional `references/`, `scripts/`, `assets/`, `examples/`, and `evals/`;
- self-contained helpers with explicit runtime requirements;
- no vendor-private tool names, sandbox paths, or installation locations in the core workflow.

The benchmark's deterministic path uses Python 3.10+ standard library only. Resolve `<PYTHON>` from host capabilities; never require the executable to be named `python3`.

## Host profiles

| Profile | Discovery/distribution | Adapter policy |
|---|---|---|
| `openai` | ChatGPT/OpenAI skill surfaces consume the portable Agent Skills package. | `agents/openai.yaml` is optional OpenAI metadata. Never award score merely because it exists. |
| `codex` | Codex discovers Agent Skills-compatible packages, including repository skills under `.agents/skills`. | The same optional `agents/openai.yaml` may provide OpenAI/Codex metadata, but the portable core must work without it. |
| `claude` | Claude Code discovers `.claude/skills/<name>/`; claude.ai supports uploaded custom skill ZIPs. | No OpenAI adapter required. Keep bundled helpers self-contained because hosted execution may restrict package installation/network. |
| `copilot` | Project skills may live in `.github/skills`, `.claude/skills`, or `.agents/skills`; personal skills may live in `~/.copilot/skills` or `~/.agents/skills`. | No extra adapter required. Do not require host-specific tool-permission frontmatter for correctness. |
| `cursor` | Cursor discovers `.agents/skills`, `.cursor/skills`, user equivalents, and compatible Claude/Codex locations. | Cursor-specific frontmatter is optional. Cloud agents may require project/synced skills rather than unsynced local skills. |

Distribution paths are host concerns. Do not duplicate or fork `SKILL.md` per host merely to install the same semantic skill.

## Capability model

Resolve capabilities before execution:

1. filesystem read;
2. filesystem write outside protected target evidence;
3. Python 3.10+ or equivalent script execution;
4. optional independent evaluator/subagent execution;
5. artifact delivery;
6. network only when freshness research is actually required.

If a capability is missing, mark the affected gate `blocked`/`not-run`; never convert missing execution into a pass.

## Python launcher policy

The active environment may expose Python as `python`, `python3`, `py -3`, an absolute interpreter path, or a host execution tool. Denote it as `<PYTHON>` in portable instructions and record the exact launcher used in evidence.

Bundled Python scripts use only the standard library plus sibling modules. Child Python processes, if ever added, must use `sys.executable`. Avoid Bash-only pipelines, POSIX-only commands, hard-coded `/tmp`, and Windows-only path assumptions in the semantic workflow.

## Host-neutral scoring

A target must not receive or lose benchmark points solely because it has or lacks a vendor adapter such as `agents/openai.yaml`. Score the semantic portable core first. Report adapters separately:

- `present-valid`;
- `present-invalid`;
- `not-present`;
- `not-required`.

When the user explicitly asks whether a target is portable, run `scripts/validate_portability.py` for the requested profiles. Structural portability does not prove runtime behavior on those hosts.

## Portability acceptance

A multi-platform claim requires:

1. portable-core structural validation passes;
2. requested host profiles pass structural checks;
3. core instructions contain no vendor-private API/tool requirement;
4. host adapters are optional and valid where present;
5. deterministic helpers have declared runtimes and no undeclared package dependency;
6. runtime/behavioral support is reported separately from structural portability.

## Current source pointers verified 2026-09-20

- Agent Skills specification: `https://agentskills.io/specification`
- OpenAI skill authoring: `https://developers.openai.com/docs/build-skills`
- Claude Agent Skills: `https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview`
- GitHub Copilot agent skills: `https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills`
- Cursor skills: `https://cursor.com/docs/skills`

Re-check these sources when a future request depends on current host-specific behavior.
