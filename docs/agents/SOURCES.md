# Current Host Sources

Verified on 2026-09-22. These sources justify only the VS Code/GitHub Copilot adapter mechanics; Mago/Magia/Nomia semantics come from their installed skill contracts.

## VS Code

- Repository source profiles live in `agents/*.agent.md`.
- Install those profiles under `.github/agents/` in a target repository for VS Code discovery.
- Custom agents: https://code.visualstudio.com/docs/agent-customization/custom-agents
  - workspace custom agents under `.github/agents`;
  - `.agent.md` format;
  - `tools` scoping;
  - `agents` subagent allowlist;
  - `user-invocable` and `disable-model-invocation`;
  - native subagents and workspace sharing.
- Agent Skills: https://code.visualstudio.com/docs/agent-customization/agent-skills
  - project skills under `.github/skills/`, `.claude/skills/`, or `.agents/skills/`.
- Custom instructions / AGENTS.md: https://code.visualstudio.com/docs/agent-customization/custom-instructions
  - intentionally not used by this package because global workspace instructions would broaden scope unnecessarily.

## GitHub Copilot

- Custom agent configuration: https://docs.github.com/en/copilot/reference/custom-agents-configuration
  - common tool aliases: `read`, `search`, `edit`, `execute`, `agent`;
  - `target` defaults to both VS Code and GitHub Copilot when omitted;
  - unrecognized tools are ignored;
  - explicit tools follow least privilege.
- Custom agents and subagent orchestration: https://docs.github.com/en/copilot/how-tos/copilot-sdk/features/custom-agents

## Evidence boundary

The package has structural validation for the files and contract. It does not claim measured runtime equivalence across every host/model. VS Code is the primary adapter; other host support remains explicitly degraded or unverified until executed there.
