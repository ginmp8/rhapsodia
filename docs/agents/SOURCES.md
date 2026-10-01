# Current Host Sources

Verified on 2026-10-01. These sources justify only host-adapter mechanics; Mago/Magia/Nomia semantics come from their installed skill contracts.

## VS Code

- Custom agents: https://code.visualstudio.com/docs/agent-customization/custom-agents
  - workspace custom agents can use `.agent.md` profiles;
  - profiles can declare explicit `tools` scopes;
  - `agents` can restrict which subagents are available from a parent custom agent;
  - `user-invocable: false` can keep a profile available as a subagent without exposing it as a normal picker choice;
  - subagents can run with custom agents and operate in separate contexts;
  - available behavior depends on the active agent harness.
- Agent Skills: https://code.visualstudio.com/docs/agent-customization/agent-skills
  - project skills may be discovered from host-supported skill roots.
- Custom instructions: https://code.visualstudio.com/docs/agent-customization/custom-instructions
  - intentionally not used by this package because global workspace instructions would broaden scope unnecessarily.

## GitHub Copilot

- Custom agent configuration: https://docs.github.com/en/copilot/reference/custom-agents-configuration
  - explicit `tools` lists restrict the tools available to a custom agent;
  - omitted tools may expose all configured tools, so Rhapsodia profiles use explicit lists;
  - tool aliases include read/search/edit/execute on supported Copilot surfaces;
  - unsupported/unrecognized tools may be ignored by a surface, which is why runtime support remains host-specific evidence.
- Custom agents and sub-agent orchestration: https://docs.github.com/en/copilot/how-tos/copilot-sdk/features/custom-agents
  - custom subagents can have isolated context and scoped tools;
  - GitHub documents read-only custom agents by giving them only read/search/view-style tools;
  - parallel dispatch is a separate runtime capability and must not be assumed universally.
- IDE subagents: https://docs.github.com/en/copilot/how-tos/copilot-in-your-ide/use-copilot-agents/use-subagents
  - subagent enablement/invocation varies by editor and active surface.

## Design implications used by Rhapsodia

1. `Rhapsodia Supervisor` remains read-only and owns orchestration state.
2. `Rhapsodia Analyst` is a separate profile with only `read` and `search`, giving read-only work units a mechanically narrower tool surface than Nomia/Mago/Magia writers.
3. Write-capable Nomia/Mago/Magia workers are never used as a parallel fan-out pool.
4. Parallel analyst dispatch is optional. If the active host/surface cannot safely parallelize, execution degrades to serial analyst work or one canonical worker.
5. `adaptive-workflow-orchestration` is an optional semantic skill, not a required third-party runtime.

## Evidence boundary

The package has structural validation for its source profiles, contract, scenarios, installer, and manifest. Official documentation establishes declared host capabilities; it does not prove runtime equivalence for every editor, model, account, or Copilot surface.

Keep these claims separate:

- structural package validation;
- documented host capability;
- observed host behavior;
- measured runtime behavior.
