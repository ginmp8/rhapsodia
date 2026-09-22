# RhapsodIA

A curated collection of agent skills, evaluation harnesses, benchmarks, and delivery workflows.

## Purpose

RhapsodIA organizes reusable skills, prompts, validation utilities, benchmarks, and delivery workflows for agent-assisted work.

The repository is intended to make skill creation, review, hardening, testing, packaging, and execution workflows easier to reuse, inspect, and evolve.

## Repository structure

```text
agents/                   # Source custom-agent profiles
  *.agent.md
skills/
  <skill-name>/
    SKILL.md          # Main skill instructions and activation contract
    agents/           # Optional agent metadata
    references/       # Supporting documentation and reusable guidance
    scripts/          # Optional validation, packaging, or helper scripts
    assets/           # Optional templates or reusable assets
    evals/            # Optional scenarios, checks, or evaluation inputs
```

Each skill should be treated as an independent package. Start with the skill's `SKILL.md` and inspect supporting files only when needed.

## Usage

Browse the `skills/` directory and open the relevant `SKILL.md` for the task you want to perform.

Typical workflows include:

- creating or improving skills;
- reviewing skill architecture and activation rules;
- validating skill packages;
- hardening skills, prompts, scripts, and references;
- benchmarking or evaluating reusable agent workflows;
- organizing delivery, planning, and execution workflows.

When a skill includes scripts, read the local instructions before running them. Some scripts are intended for validation, packaging, inventory, or report generation and may have package-specific assumptions.

## Rhapsodia Agents for VS Code

Rhapsodia includes a VS Code-first custom-agent layer for coordinating the existing Nomia, Mago, and Magia Agent Skills through native subagent delegation. It does not merge or fork those skills and does not require an external orchestration runtime.

### Included package

```text
agents/
  rhapsodia-supervisor.agent.md
  nomia.agent.md
  mago.agent.md
  magia.agent.md

docs/agents/
  ARCHITECTURE.md
  SOURCES.md
  contracts/
    rhapsodia-agent-system.json

scripts/
  validate_agents.py

tests/
  agent-scenarios.json
  test_validate_agents.py
```

The [agent architecture](docs/agents/ARCHITECTURE.md) is the detailed source of truth for ownership, authority, routing budgets, lifecycle recovery, and handoff boundaries. The [agent sources](docs/agents/SOURCES.md) document the host-specific mechanics and compatibility evidence.

### Required skills

The package expects the current `nomia`, `mago`, and `magia` Agent Skills to be available through the host's native skill discovery. It does not bundle or fork those skills. The RhapsodIA repository keeps the source skills under `skills/`. When using this package in a target repository, install each skill in one of the following host-supported locations:

```text
.github/skills/<skill-name>/SKILL.md
.claude/skills/<skill-name>/SKILL.md
.agents/skills/<skill-name>/SKILL.md
```

Install each skill once in one supported location. Do not copy the full skill instructions into the custom agents.

### Install and use

Copy the profiles from `agents/` into `.github/agents/` in the target repository, then open that repository in VS Code with GitHub Copilot and agent support enabled. Use the custom-agent configuration or diagnostics UI to confirm that the four agents and the three required Agent Skills are discovered.

The primary user-facing entry point is `Rhapsodia Supervisor`. Nomia, Mago, and Magia use `user-invocable: false`; they are native subagents of the supervisor rather than independent user-selected modes.

### Native-only runtime policy

Normal operation requires only host-native capabilities:

- repository read and search;
- scoped editing in specialist workers;
- bounded command execution in specialist workers;
- native custom-agent/subagent invocation in the supervisor;
- native Agent Skills discovery.

The core package does not depend on MCP, LangGraph, CrewAI, AutoGen, Orca, a provider SDK, or a custom orchestration service. An optional integration may still be used by a host if separately configured, but it is not a package requirement.

### Tool scoping

| Agent                | Tools                               | Purpose                                    |
| -------------------- | ----------------------------------- | ------------------------------------------ |
| Rhapsodia Supervisor | `read`, `search`, `agent`           | Read-only routing and native delegation    |
| Nomia                | `read`, `search`, `edit`, `execute` | Governance artifacts and Nomia validators  |
| Mago                 | `read`, `search`, `edit`, `execute` | Planning artifacts and Mago validators     |
| Magia                | `read`, `search`, `edit`, `execute` | Bounded implementation and execution proof |

Workers intentionally do not receive the `agent` tool, which prevents recursive worker-to-worker orchestration. Capability does not grant authority beyond the role-specific Agent Skill contract.

### Governed lifecycle

```text
Nomia -> Mago -> Magia -> Mago -> Nomia
```

This is a lifecycle, not a requirement to replay every phase. The supervisor may resume from the middle when canonical state and valid typed evidence establish the active phase. A bounded Magia ADHOC request may bypass the governed lifecycle only when no governed board or package is involved and the direct repository scope and proof are explicit.

Two handoff layers coexist:

- `handoff/v1`: agent-control delegation from the supervisor to a worker;
- ecosystem handoff v3: skill-owned evidence transfer between Nomia, Mago, and Magia.

The supervisor does not generate or repair ecosystem handoff v3. The [portable agent-system contract](docs/agents/contracts/rhapsodia-agent-system.json) defines the semantic boundary.

### Host configuration

No profile pins a `model`; the selected host model is inherited so the package does not depend on a model identifier that varies across accounts, hosts, or time. The package also deliberately avoids global `AGENTS.md` or `copilot-instructions.md` files so Mago, Magia, and Nomia rules apply only when their agents or skills are active.

### Validation and evidence

Run the package validator and tests with an available Python 3 interpreter:

```text
python scripts/validate_agents.py --target .
python -m unittest discover -s tests -p "test_*.py" -v
```

The validator checks the agent profiles, portable contract, scenario coverage, and package documentation. The included tests and scenarios prove structure and selected policy invariants; `tests/agent-scenarios.json` remains `planned` evidence until executed by an actual model and host harness. Structural validation must not be interpreted as measured runtime routing precision or autonomous reliability.

VS Code is the primary, structurally validated adapter. GitHub Copilot surfaces share common frontmatter and tool aliases, but VS Code-specific subagent allowlisting may not behave identically everywhere. The semantic contract is reusable by Cursor, Claude, Codex, and Visual Studio, but this package does not include host-specific runtime validation for those environments.

## Validation

Validation is handled per skill. Check each skill package for available scripts, references, or evaluation files before making changes.

Common validation-related locations include:

```text
skills/<skill-name>/scripts/
skills/<skill-name>/evals/
skills/<skill-name>/references/
```

Do not assume that one validation command applies to every skill package.

## Third-party and adapted content

Some packages may include copied, adapted, derived, or inspired third-party material. When present, original license notices and attribution notes must be preserved in the relevant files or directories.

Known third-party or adapted content:

- `skills/skill-creator/` includes OpenAI `skill-creator` content with its original Apache License 2.0 notice preserved in `skills/skill-creator/LICENSE.txt`.
- `skills/streamlit/` is an original RhapsodIA skill built from and cross-referencing the official Streamlit documentation and Streamlit project sources. The official upstream repositories `streamlit/docs` and `streamlit/streamlit` are licensed under Apache License 2.0; see `skills/streamlit/references/source-and-license.md` for source and attribution notes.
- `skills/context-architect/` is inspired by GitHub's `awesome-copilot` Context Architect agent. The upstream source is licensed under the MIT License, Copyright GitHub, Inc.; see `skills/context-architect/references/upstream-source.md` for source and adaptation notes.
- `skills/skill-creator-juiced/` is an original RhapsodIA orchestration skill conceptually related to `skills/skill-creator/`; see `skills/skill-creator-juiced/references/source-and-license.md` for attribution and update rules.
- `skills/karpathy-guidelines/` is an original RhapsodIA skill inspired by public software-engineering guidance commonly associated with Andrej Karpathy; see `docs/public-source-attribution-audit.md` for provenance and update rules.
- `skills/decision-engine/` is an original RhapsodIA skill conceptually inspired by JEV's structured decision approach; see `docs/public-source-attribution-audit.md` for provenance and update rules.
- `skills/llm-wiki-maintainer/` is an original RhapsodIA skill that operationalizes and paraphrases the public [`llm-wiki.md`](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) pattern by Andrej Karpathy.
- Some skills may include upstream or adaptation notes in their own `references/` files.

See `docs/public-source-attribution-audit.md` for the public-source similarity and attribution review that supports the current attribution list.

Third-party content is not relicensed by this repository unless its original license allows it.

## License

Copyright 2026 ginmp8

Unless otherwise stated, this repository is licensed under the [Apache License 2.0](LICENSE).

The Apache License 2.0 applies to prompts, skills, scripts, examples, templates, and documentation created specifically for this repository.

If this repository includes copied or adapted third-party content, its original license notices are preserved and that content is not relicensed unless the original license allows it.
