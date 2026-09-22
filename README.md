# RhapsodIA

A curated collection of Agent Skills, evaluation harnesses, benchmarks, delivery workflows, and native-host agent profiles for agent-assisted software and product work.

## Purpose

RhapsodIA organizes reusable skills, prompts, validation utilities, benchmarks, governance workflows, planning workflows, execution workflows, and agent profiles so they can be reused, inspected, validated, and evolved independently.

The broader repository is intentionally split by responsibility:

- **Skills** own reusable capabilities and their semantic contracts.
- **Agents** operate those capabilities with an explicit mission, authority boundary, tools, state, routing, and termination behavior.
- **Validators/evals** provide structural or behavioral evidence without becoming the source of domain truth.
- **Delivery workflows** preserve ownership between governance, technical planning, and execution.

The design goal is not to create one universal agent. It is to preserve clear ownership and let the host compose the smallest set of capabilities required for the active task.

## Distribution scope

This archive is the **Agent-layer distribution** of RhapsodIA. It intentionally contains only:

- the four Mago/Magia/Nomia custom-agent profiles;
- the portable agent-system contract;
- architecture and host-source documentation directly related to those agents;
- the deterministic installer;
- validators, scenarios, tests, manifest, and license required to validate and distribute the agent layer.

It does **not** bundle the full RhapsodIA skill catalog, benchmarks, unrelated validators, or other repository tooling.

The reduced archive scope must not be confused with the scope of RhapsodIA itself. The sections below preserve the repository-level context needed to understand where these agents fit.

## Full repository model

In the full RhapsodIA repository, the conceptual structure is:

```text
agents/                   # Canonical source custom-agent profiles
  *.agent.md

skills/
  <skill-name>/
    SKILL.md              # Main skill instructions and activation contract
    agents/               # Optional host metadata
    references/           # Supporting contracts/guidance
    scripts/              # Optional validators/helpers/packagers
    assets/               # Optional templates/assets
    evals/                # Optional scenarios/evaluation inputs

# Additional repository-level documentation, validation, benchmark,
# delivery, and governance artifacts may exist outside this distribution.
```

Each Skill is an independent reusable capability. Start from its SKILL.md and progressively load supporting resources only when the active workflow requires them.

The `agents/` directory is different: it contains operators around capabilities rather than copies of Skill instructions.

## RhapsodIA usage model

Typical full-repository workflows include:

- creating or improving Agent Skills;
- reviewing skill architecture and activation contracts;
- reproducibility, hardening, consistency, testing, and packaging;
- benchmark/harness execution and evidence review;
- product/delivery governance;
- technical planning and reconciliation;
- bounded repository implementation, debugging, testing, and validation;
- custom-agent design and multi-agent orchestration using native host capabilities.

A Skill remains the source of truth for its competency. An Agent should not duplicate an entire Skill merely to call it.

For the Mago/Magia/Nomia ecosystem, that separation is central:

```text
Nomia Skill  = product/delivery governance capability
Mago Skill   = technical planning/reconciliation capability
Magia Skill  = bounded repository execution/validation capability

Nomia Agent  = bounded operator around Nomia
Mago Agent   = bounded operator around Mago
Magia Agent  = bounded operator around Magia
Supervisor   = orchestration only; not a fourth domain capability
```

## RhapsodIA Agents for VS Code

This distribution provides a VS Code-first custom-agent layer for coordinating the existing Nomia, Mago, and Magia Agent Skills through native subagent delegation.

It does not merge or fork those Skills and does not require an external orchestration runtime.

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
  install_agents.py
  validate_agents.py

tests/
  agent-scenarios.json
  test_install_agents.py
  test_validate_agents.py

MANIFEST.json
LICENSE
```

`agents/` is the canonical distribution source. It is intentionally **not** a VS Code discovery location.

The detailed agent architecture lives in [docs/agents/ARCHITECTURE.md](docs/agents/ARCHITECTURE.md). Host-specific evidence used to justify the VS Code adapter lives in [docs/agents/SOURCES.md](docs/agents/SOURCES.md). The portable source/build-time contract lives in [docs/agents/contracts/rhapsodia-agent-system.json](docs/agents/contracts/rhapsodia-agent-system.json).

### Required Skills

The target repository must already expose the current `nomia`, `mago`, and `magia` Agent Skills through one host-supported project skill root:

```text
.github/skills/<skill-name>/SKILL.md
.claude/skills/<skill-name>/SKILL.md
.agents/skills/<skill-name>/SKILL.md
```

Install each required Skill in exactly one supported root. Install the **complete Skill directory**, not only SKILL.md, because its references, scripts, assets, evals, and validators may be part of the capability contract.

This Agent distribution verifies the prerequisite but never copies or mutates those Skills.

### Installation

Preferred deterministic installation:

```text
python scripts/install_agents.py --target <TARGET_REPOSITORY>
```

The installer copies only:

```text
agents/*.agent.md
    -> <TARGET_REPOSITORY>/.github/agents/*.agent.md
```

Useful modes:

```text
python scripts/install_agents.py --target <TARGET_REPOSITORY> --dry-run
python scripts/install_agents.py --target <TARGET_REPOSITORY> --check
python scripts/install_agents.py --target <TARGET_REPOSITORY> --force
```

- `--dry-run`: verify prerequisites and show the install plan without mutation.
- `--check`: verify the installed profiles against this package and confirm that Nomia, Mago, and Magia are discoverable.
- `--force`: replace a differing existing agent profile. Without it, differing files fail closed.

Manual installation is also valid: copy the four profiles from `agents/` to `.github/agents/` in the target repository.

After installation, open the target repository in VS Code with GitHub Copilot/agent support enabled and confirm that the four custom agents plus the three required Agent Skills are discovered.

The primary user-facing entry point is **Rhapsodia Supervisor**. Nomia, Mago, and Magia are configured as specialist subagents rather than normal user-selected modes.

### Runtime boundary

The deployed runtime requires only:

```text
.github/agents/
  rhapsodia-supervisor.agent.md
  nomia.agent.md
  mago.agent.md
  magia.agent.md

<one supported skill root>/
  nomia/
  mago/
  magia/
```

The portable JSON contract shipped in this archive is a **design/build-time validation contract**, not a runtime dependency that must be copied to every target repository.

At runtime:

- **Rhapsodia Supervisor** owns orchestration, owner resolution, bounded delegation, transition validation, cycle control, and terminal integration.
- **Nomia** owns one product/delivery-governance phase through the Nomia Skill.
- **Mago** owns one technical-planning or reconciliation phase through the Mago Skill.
- **Magia** owns one bounded implementation/validation phase through the Magia Skill.

### Native-only runtime policy

Normal operation requires only native host capabilities:

- repository read/search;
- scoped editing in specialist workers;
- bounded command execution in specialist workers;
- native custom-agent/subagent invocation in the supervisor;
- native Agent Skills discovery.

The package does not require Orca, LangGraph, CrewAI, AutoGen, MCP, a provider-specific Agents SDK, or a custom orchestration service.

Knowledge from those systems may inform design patterns, but they are not runtime dependencies.

### Tool scoping

| Agent | Tools | Purpose |
|---|---|---|
| Rhapsodia Supervisor | `read`, `search`, `agent` | Read-only routing and native delegation |
| Nomia | `read`, `search`, `edit`, `execute` | Governance artifacts and Nomia validators |
| Mago | `read`, `search`, `edit`, `execute` | Planning artifacts and Mago validators |
| Magia | `read`, `search`, `edit`, `execute` | Bounded implementation and execution proof |

Workers intentionally do not receive the `agent` tool. Worker-to-worker recursive orchestration is excluded by the package design.

Tool availability is not equivalent to semantic authority: each worker remains bounded by its corresponding Agent Skill.

### Governed lifecycle

The canonical governed lifecycle is:

```text
Nomia -> Mago -> Magia -> Mago -> Nomia
```

This is a lifecycle, not a requirement to replay every phase on every invocation. The supervisor may resume in the middle when canonical state and valid typed evidence establish the active phase.

A bounded Magia ADHOC task may bypass the governed lifecycle only when it is outside a governed board/package flow and the repository scope, intended behavior, protected paths, and proving check are explicit.

### Delegation and evidence-transfer contracts

Two different contracts intentionally coexist:

- `handoff/v1`: supervisor-to-worker **agent-control delegation**;
- ecosystem handoff v3: **Skill-owned evidence transfer** between Nomia, Mago, and Magia domains.

They are not synonyms.

The supervisor keeps orchestration ownership during native subagent delegation. It may inspect a validated ecosystem handoff v3, but it never generates, repairs, or rewrites that Skill-owned evidence contract.

### Routing and autonomy boundaries

The system is designed for **policy-bounded autonomy with human/external-authority escalation by exception**, not unlimited autonomy.

The Supervisor may continue an already-authorized low-risk transition when owner, authority, evidence, and validation are resolved.

It must stop or escalate when, for example:

- ownership or authority is unresolved;
- business-risk acceptance or a delivery commitment requires external governance authority;
- destructive, privileged, production, financial, identity/access, or externally communicative action lacks explicit authorization;
- material architecture, public-contract, data, security, sequencing, or user-behavior change crosses the active role boundary;
- canonical evidence conflicts;
- privacy/provenance lineage is insufficient;
- required validation cannot be performed truthfully;
- retry/re-entry/routing budgets are exhausted.

### Cycle and repair safety

The portable contract uses bounded routing rather than open-ended collaboration:

```text
max specialist delegations: 12
max re-entries per owner: 2
materially identical handoff repeats: 0
```

A re-entry requires new evidence, changed state/artifact, a completed repair, or a new authorization decision.

Repeated identical routing is an escalation condition, not a reason to keep prompting agents until one says `done`.

### Host configuration

No profile pins a model. Model selection remains under the active host/account/user configuration instead of creating a dependency on a model identifier that may change over time.

The package deliberately avoids global workspace instruction files such as AGENTS.md or `.github/copilot-instructions.md`. Mago/Magia/Nomia rules should apply when these agents/skills are active, not to every unrelated Copilot interaction in a repository.

VS Code is the primary adapter. The semantic contract can inform future adapters for GitHub Copilot surfaces, Cursor, Claude, Codex, Visual Studio, or other compatible hosts without changing domain ownership.

A portable semantic contract does **not** by itself prove runtime parity on those hosts.

### Validation and evidence

Validate the source package with an available Python 3 interpreter:

```text
python scripts/validate_agents.py --target .
python -m unittest discover -s tests -p "test_*.py" -v
```

The Agent-layer validator checks, among other things:

- exact four-agent source set;
- frontmatter and tool boundaries;
- Supervisor allowlist and finite routing invariants;
- worker non-delegation;
- portable contract invariants;
- scenario coverage;
- manifest file-set/hash/size integrity;
- package hygiene;
- installer/documentation presence.

The installer can validate an actual target installation with:

```text
python scripts/install_agents.py --target <TARGET_REPOSITORY> --check
```

The scenario suite in this archive is **planned/structural evidence** until executed against a real model and host runtime. Static validation must not be reported as measured routing accuracy, runtime reliability, or proof of zero-HITL operation.

## Validation in the full RhapsodIA repository

Validation remains capability-specific in the full repository. Individual Skills may own their own scripts, references, evals, validators, package gates, benchmark evidence, or release rules.

There is intentionally no assumption that one command validates every RhapsodIA Skill.

The Agent-layer checks in this archive validate the integration boundary around Nomia/Mago/Magia; they do not replace the validators owned by those Skills.

## Third-party and adapted content

The full RhapsodIA repository may contain original, copied, adapted, derived, or conceptually inspired material under different source licenses and attribution requirements.

The repository-level policy is to preserve upstream notices and keep attribution close to the relevant Skill/resource. Known repository-level entries documented by the source README include:

- **skill-creator** includes OpenAI skill-creator content with the original Apache License 2.0 notice preserved by the full repository.
- **streamlit** is an original RhapsodIA skill built from and cross-referencing official Streamlit documentation and project sources; the upstream Streamlit repositories are Apache-2.0 licensed.
- **context-architect** is inspired by GitHub's `awesome-copilot` Context Architect agent; the upstream source is MIT licensed, Copyright GitHub, Inc.
- **skill-creator-juiced** is an original RhapsodIA orchestration skill conceptually related to skill-creator and maintains its own source/license notes.
- **karpathy-guidelines** is an original RhapsodIA skill inspired by public software-engineering guidance commonly associated with Andrej Karpathy.
- **decision-engine** is an original RhapsodIA skill conceptually inspired by JEV's structured decision approach.
- **llm-wiki-maintainer** is an original RhapsodIA skill that operationalizes and paraphrases the public `llm-wiki.md` pattern by Andrej Karpathy.
- Other Skills may carry upstream/adaptation notes in their own reference files.

Those packages are **not bundled in this Agent-only archive** unless explicitly present in the package tree. The list is retained because it is part of the RhapsodIA repository context and prevents this reduced distribution from appearing to represent the entirety of the repository or its licensing provenance.

The Agents in this archive are original RhapsodIA package content unless an included file states otherwise.

## License

Copyright 2026 ginmp8

Unless otherwise stated in an included file, this distribution is licensed under the [Apache License 2.0](LICENSE).

The Apache License 2.0 applies to prompts, agents, skills, scripts, examples, templates, and documentation created specifically for RhapsodIA when those artifacts do not declare another license.

In the full RhapsodIA repository, copied or adapted third-party content remains subject to its original license and notices and is not relicensed merely by inclusion in the repository.
