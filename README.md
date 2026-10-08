# RhapsodIA

## 0.7.0 - Lazy shared runtime knowledge and compact agent handoffs

RhapsodIA 0.7.0 adds **Runtime Harness**, a portable Python-standard-library layer
that lets agents reuse environment knowledge instead of repeatedly searching for tools,
skills, scripts and local resources. The catalog contains **52 Agent Skills and seven
agent profiles**.

- Minimal bootstrap: running Python + bounded skill/agent catalogs only.
- Lazy `ensure tool://<id>` discovery for exactly the dependency an authorized agent needs.
- Cross-agent immutable snapshot sharing with atomic merge; agents never edit runtime state directly.
- Negative missing-tool cache bound to TTL and PATH/PATHEXT fingerprint.
- `observe-tool` and `observe-resource` for mechanically verifiable reusable locations.
- Exact `tool://`, `skill://`, `agent://`, `resource://`, `repo://` and workspace lookups.
- Compact content-pinned handoffs; resource changes invalidate old pins without forcing full rediscovery.
- Read-only `resolve/context` and MCP; publication never expands an agent's existing authority.
- No mandatory database, graph service, shell, cloud, model provider or third-party Python package.
- All seven agents know how to reuse, discover and share bounded runtime observations while preserving domain ownership.

Start with [Runtime Harness](skills/runtime-harness/README.md). Read the complete
[0.7.0 release notes](docs/releases/0.7.0.md) and [migration guide](docs/runtime/MIGRATION-0.7.0.md).
Host configuration remains opt-in; installing the ZIP alone does not start hooks/services.

## 0.6.0 (historical) — Local graph workbench, interactive exploration, and PDF workbench

RhapsodIA 0.6.0 expands the catalog with three portable skills: `local-graph-engine`, `local-graph-explorer`, and `pdf-workbench`. The catalog now contains **51 Agent Skills and seven agent profiles**.

- `local-graph-engine` models, ingests, queries, analyzes, and exports evidence-backed local graphs in SQLite, including bounded context extraction and portable `GraphView` output.
- `local-graph-explorer` consumes the shared `graph-view-v1` contract and provides an offline interactive viewer with graph/table/timeline/matrix/summary views, node dragging, and finite directed walkthroughs.
- `pdf-workbench` provides capability-routed PDF inspection, extraction, editing, forms, OCR, redaction, rendering, and conformance-oriented validation with explicit safeguards for signed, XFA, encrypted, tagged, damaged, and untrusted PDFs.

This release also refines `skill-booster`, `skill-creator-juiced`, and `reproducibility-engineer` around eval-first evidence, catalog coexistence, runtime trust/authority boundaries, and model-neutral reproducibility. Package release metadata is `0.6.0`; skill-local semantic or implementation versions remain independently versioned.

Release validation now covers the three added skills, verifies their packaging, keeps the shared graph-view contract byte-identical across producer and viewer, and retains the existing agent/marketplace/version gates.

## 0.5.0 (historical) — Top-100 control surfaces and progressive loading

RhapsodIA 0.5.0 makes skill selection and safe task startup more reliable under partial context. For every long `SKILL.md` touched by this release, the primary control surface is moved into the first 100 physical lines: purpose and boundaries, material modes, a usable workflow, critical invariants, stop/acceptance conditions, and direct pointers to branch-specific resources.

The release updates **39 existing skills** and adds **three new skills** — `discernment-nudge`, `systematic-debugging`, and `visual-code-intelligence` — bringing the catalog to **48 Agent Skills and seven agent profiles**. Long authored supporting Markdown now follows a semantic-preview-first pattern with decision-useful `Purpose`, `Load when`, and `Decision impact` signals plus synchronized navigation, while one-hop discovery keeps required guidance directly reachable from `SKILL.md`.

The control-plane policy is enforced by the skill creation, optimization, reproducibility, traceability, and change-gating surfaces instead of relying on prose convention alone. Internal semantic contract versions remain independently versioned; this package release does not globally rewrite workflow/schema identities merely to match `0.5.0`.

Packaging remains deterministic and release metadata is validated from the canonical marketplace version before archive creation.

## Artifact-native workspace (Mags 2.0.0)

Mago, Magia and Nomia now operate on independent producer-owned artifacts by default. The supervisor routes the owner; that owner's skill decides which documents are necessary and returns live-validated `artifact_actions`. No Board, Workspace installation, external orchestrator, database or network service is required for domain work.

| Component | Owns | Never owns |
|---|---|---|
| Nomia | Governance in `docs/product/<work_item_id>` | Technical planning or execution evidence |
| Mago | Planning in `docs/specs/<work_item_id>` | Runtime execution or product priority |
| Magia | Execution records in `docs/implementation/<work_item_id>` | Mago task definitions/checkboxes or governance closure |
| Rhapsodia Workspace | Rebuildable catalog and local HTML views | Canonical source content, source metadata, or domain decisions |

The optional `rhapsodia-workspace` skill and bounded Workspace agent support portfolio, metadata updates, relations and per-skill views. Unknown states and missing relationships remain explicit. A snapshot is not a live watcher and an updated-at timeline is not reconstructed process history.

```bash
python skills/rhapsodia-workspace/scripts/workspace.py index --repo-root /path/to/project
python skills/rhapsodia-workspace/scripts/workspace.py render --repo-root /path/to/project
```

Open the generated `.rhapsodia/views/index.html` locally. Search, filter, inspect source hashes/relations, switch view/theme, or import/export snapshots without remote dependencies. Source content never executes in the viewer. See [the complete native workflow](docs/agents/ARTIFACT-ORCHESTRATION.md), [Workspace commands](skills/rhapsodia-workspace/references/commands.md), and [migration/rollback](skills/mago/references/ecosystem-migration.md).

Existing Board tools remain an explicit `legacy-board` compatibility profile, not the storage model for new work. The implemented owner-side migration copies recognized artifacts, preserves originals and supports hash-approved recovery. The coordinated Mags release must be installed as one exact-version set. Historical evaluator bytes are retained with explicit SHA-256 pins.

Release packaging is data-only. Run `scripts/validate_and_attest.py --target skills/mago --output /outside/repo/mago-validation.json --trust-target-code`, then pass that evidence to `skills/mago/scripts/package_skill.py --target skills/mago --output /outside/repo/skill.zip --validation-evidence /outside/repo/mago-validation.json --validate`. Repeat per skill. A changed tree invalidates its receipt. Executing validators requires an explicitly trusted target; merely packaging never executes target scripts.


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

The repository contains the complete RhapsodIA distribution: the canonical Skill catalog, Agent layer, documentation, validators, tests, and marketplace manifests. Release archives are built from this source tree; generated validation evidence is intentionally kept outside the versioned source.

The root `MANIFEST.json` remains the deterministic manifest for the **Agent-layer distribution surface** (README, agent profiles, agent docs, installer/validator, and agent tests). Individual Skills own their own package/integration validation contracts. A full-project ZIP is therefore broader than the root Agent manifest by design.

Previously integrated capabilities retained by this release include:

- `test-oracle-engineering`: executable falsifiable proof contracts and receipts;
- `perceptual-validation`: optional semantic visual comparison with explicit invalid-state handling;
- `Rhapsodia Verifier`: independent executable proof operator around `test-oracle-engineering`.

The retained baseline also evolves `adaptive-workflow-orchestration` with backward-compatible `workflow-plan/v2` gated convergence while preserving `workflow-plan/v1`, and adds checkpoint-candidate semantics to the Magia execution surface.

See the [Rhapsodia Workspace documentation](docs/workspace/README.md) for ownership, commands, validation, migration boundaries, and offline-view behavior. The [offline demo](docs/workspace/demo.html) uses synthetic records only.

## Marketplace distribution

RhapsodIA is distributed from **one canonical `skills/` tree and one canonical `agents/` tree**. Platform-specific files contain metadata and routing only; they do not own copies of Skill or Agent content.

The repository deliberately does **not** keep a root Agent Plugins `plugin.json`. Agent Plugins 1.0 standardizes Skills and MCP servers, but not custom agents. Keeping that manifest at the repository root would force Copilot into Agent Plugins semantics and require a second `com.github.copilot/agents/` tree. Instead:

- GitHub Copilot uses `.github/plugin/plugin.json` and points directly at `agents/` and `skills/`;
- Cursor uses `.cursor-plugin/plugin.json` and points at the same canonical directories;
- Claude Code uses `.claude-plugin/` with the canonical `agents/` and `skills/`;
- OpenAI/ChatGPT/Codex uses `.codex-plugin/plugin.json` for the canonical Skills;
- generic Agent Plugins 1.0 clients use a generated portable package containing Skills/MCP only.

The canonical marketplace metadata lives in `marketplace/catalog.json`. Regenerate and verify host manifests with:

```text
python scripts/generate_marketplace_manifests.py
python scripts/generate_marketplace_manifests.py --check
python -m unittest tests.test_marketplace_manifests
```

Build the standards-based portable Agent Plugins artifact when needed:

```text
python scripts/build_portable_agent_plugin.py --output dist/agent-plugin/rhapsodia
```

`agents/` is the only source of custom-agent definitions. `com.github.copilot/agents/` is intentionally absent from the repository and guarded by tests.

See [docs/marketplace.md](docs/marketplace.md) for platform files, installation commands, capability differences, and the portability rationale.

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
Supervisor   = orchestration/promotion only; not a fourth domain capability
Analyst      = read-only isolated analysis/adversarial-review operator; no domain ownership
Verifier     = executable proof operator; verification-only writes, no production repair
Test Oracle  = reusable falsifiable proof capability
Perceptual   = optional semantic visual evidence capability
```

## RhapsodIA Agents

The Agent layer has a portable semantic contract plus a validated VS Code-first custom-agent adapter for coordinating the existing Nomia, Mago, and Magia Agent Skills through native subagent delegation.

It does not merge or fork those Skills and does not require an external orchestration runtime.

### Included package

```text
agents/
  rhapsodia-supervisor.agent.md
  rhapsodia-analyst.agent.md
  rhapsodia-verifier.agent.md
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

The target repository must already expose the current `nomia`, `mago`, `magia`, and `test-oracle-engineering` Agent Skills through one host-supported project skill root:

```text
.github/skills/<skill-name>/SKILL.md
.claude/skills/<skill-name>/SKILL.md
.agents/skills/<skill-name>/SKILL.md
```

Install each required Skill in exactly one supported root. Install the **complete Skill directory**, not only SKILL.md, because its references, scripts, assets, evals, and validators may be part of the capability contract.

This Agent distribution verifies the prerequisite but never copies or mutates those Skills.

### External supporting Agent Skills

Rhapsodia does not maintain a catalog of language, framework, security, database, cloud, testing, or other specialist skills. When a phase needs extra expertise, the Supervisor/accepted workflow expresses the need as a **semantic capability** and the active worker resolves a matching installed Agent Skill through the host's native discovery mechanism.

The canonical skill remains authoritative for the phase. A supporting skill cannot change lifecycle ownership, tools, write scope, acceptance criteria, handoff direction, approval policy, or stop conditions. Missing required capability blocks the affected unit; missing optional capability is recorded as `not-run`/degraded only when the workflow remains semantically valid.

This keeps external skills independently installable and replaceable. No external skill package name, repository path, vendor, model, or fixed mapping is required by Rhapsodia.

### Optional orchestration and perceptual Skills

`adaptive-workflow-orchestration` is optional. When installed, the Supervisor may use `workflow-plan/v1` for classic dynamic patterns and `workflow-plan/v2` for gated checkpoint convergence inside an already-resolved lifecycle phase. The canonical lifecycle remains functional without it and falls back to conservative single/serial execution.

`perceptual-validation` is optional. A plan may require it only when semantic visual equivalence is part of acceptance and the active host exposes image-capable or human review. Missing required perceptual capability blocks that gate; optional perceptual gates may remain `not-run`.

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

Manual installation is also valid: copy the six profiles from `agents/` to `.github/agents/` in the target repository.

After installation, open the target repository in VS Code with GitHub Copilot/agent support enabled and confirm that the six custom agents plus the four required canonical Agent Skills are discovered. Any additional installed Agent Skills remain independently discoverable as supporting semantic capabilities; they do not need to be copied into Rhapsodia.

The primary user-facing entry point is **Rhapsodia Supervisor**. Rhapsodia Analyst, Nomia, Mago, and Magia are configured as subagents rather than normal user-selected modes; Analyst is read-only and hidden from ordinary user selection.

### Runtime boundary

The deployed runtime requires only:

```text
.github/agents/
  rhapsodia-supervisor.agent.md
  rhapsodia-analyst.agent.md
  rhapsodia-verifier.agent.md
  nomia.agent.md
  mago.agent.md
  magia.agent.md

<one supported skill root>/
  nomia/
  mago/
  magia/
  test-oracle-engineering/
```

Additional supporting Agent Skills are optional runtime inputs discovered by the active host/worker when a semantic capability requires them; they are deliberately outside this fixed prerequisite set.

The portable JSON contract shipped in this archive is a **design/build-time validation contract**, not a runtime dependency that must be copied to every target repository.

At runtime:

- **Rhapsodia Supervisor** owns orchestration, owner resolution, bounded delegation, adaptive read-only work-unit synthesis, transition validation, cycle control, and terminal integration.
- **Rhapsodia Analyst** owns one isolated read-only analysis/adversarial-review unit and never owns canonical lifecycle state.
- **Rhapsodia Verifier** owns one independent executable proof unit, may write only verification artifacts, and never repairs production code or promotes checkpoints.
- **Nomia** owns one product/delivery-governance phase through the Nomia Skill.
- **Mago** owns one technical-planning or reconciliation phase through the Mago Skill.
- **Magia** owns one bounded implementation/validation phase through the Magia Skill.

### Native-only runtime policy

Normal operation requires only native host capabilities:

- repository read/search;
- scoped editing in specialist workers;
- bounded command execution in specialist workers;
- native custom-agent/subagent invocation in the supervisor;
- an explicit read/search-only analyst profile for isolated read-only work units;
- an explicit verifier profile with verification-only edit/execute authority plus the `test-oracle-engineering` Skill;
- native Agent Skills discovery.

The package does not require Orca, LangGraph, CrewAI, AutoGen, MCP, a provider-specific Agents SDK, or a custom orchestration service.

Knowledge from those systems may inform design patterns, but they are not runtime dependencies.

### Tool scoping

| Agent | Tools | Purpose |
|---|---|---|
| Rhapsodia Supervisor | `read`, `search`, `agent` | Read-only routing, synthesis, and native delegation |
| Rhapsodia Analyst | `read`, `search` | Isolated read-only analysis/adversarial review |
| Rhapsodia Verifier | `read`, `search`, `edit`, `execute` | Independent executable oracle proof; edit restricted to verification artifacts |
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


### Adaptive execution inside a lifecycle phase

The default remains one canonical worker. The Supervisor may decompose read-only evidence into Rhapsodia Analyst work units. Inside an accepted Magia gated-convergence plan it may additionally invoke Rhapsodia Verifier for independent executable proof. Nomia, Mago, and Magia are never used as a parallel writer pool. Any canonical production mutation, phase completion, or ecosystem handoff v3 remains owned by exactly one canonical worker; Verifier writes only explicit verification artifacts.

If safe parallel subagent scheduling is unavailable, the same analyst units run serially. No third-party orchestrator is installed as a fallback.

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
max total subagent delegations: 24
max analyst work units per phase: 4
max parallel analyst work units: 4 (host permitting; otherwise serial)
max gated checkpoints per Magia phase: 4
max checkpoint repairs after initial candidate: 2
max adversarial Analyst reviews per checkpoint: 2
max Verifier proof units per candidate attempt: 1
max ordinary re-entries per canonical owner: 2
materially identical handoff/analyst/verifier repeats: 0
```

A re-entry requires new evidence, changed state/artifact, a completed repair, or a new authorization decision.

Repeated identical routing is an escalation condition, not a reason to keep prompting agents until one says `done`.

### Host configuration

No profile pins a model. Model selection remains under the active host/account/user configuration instead of creating a dependency on a model identifier that may change over time.

The package deliberately avoids global workspace instruction files such as AGENTS.md or `.github/copilot-instructions.md`. Mago/Magia/Nomia rules should apply when these agents/skills are active, not to every unrelated Copilot interaction in a repository.

VS Code is the primary validated adapter. The Skills and `agent-system-contract/v2` form the portable semantic core for OpenAI/ChatGPT, Codex, Claude, GitHub Copilot/VS Code, Cursor, Visual Studio, and other capable hosts. Hosts with different custom-agent discovery formats require an adapter that preserves the same authority, gate, state, and termination semantics.

A portable semantic contract does **not** by itself prove runtime parity on those hosts; unsupported adapters remain explicitly `adapter-required`.

### Validation and evidence

Validate the source package with an available Python 3 interpreter:

```text
python scripts/validate_agents.py --target .
python -m unittest discover -s tests -p "test_*.py" -v
```

The Agent-layer validator checks, among other things:

- exact six-agent source set;
- frontmatter and tool boundaries;
- Supervisor allowlist, adaptive read-only fan-out, single-writer, and finite routing invariants;
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

Those packages are present only when they exist in this complete snapshot. Their local notices remain authoritative; this README does not replace package-specific attribution or licensing metadata.

The Agents in this archive are original RhapsodIA package content unless an included file states otherwise.

## Design inspirations for this update

The following research-derived patterns informed this update while creating **no runtime coupling** to the referenced systems:

- **Runtime-adaptive orchestration:** isolated execution contexts, pipeline and barrier semantics, adversarial verification, bounded loops, explicit resumability boundaries, and the principle that simple work should remain simple.
- **Checkpoint convergence:** small reviewable checkpoints, non-overridable gates, repair-before-progression, and accepted-feedback carry-forward.
- **Executable verification:** test oracles, independent verification, deterministic critical mechanics, and model-independent harness design.
- **Agent and evaluation architecture:** simple composable patterns, environment ground truth, evaluator separation, trace and evaluation evidence, and bounded approvals.

These patterns are adapted into RhapsodIA-specific, host-neutral contracts and execution semantics. Detailed source provenance, including the public Anthropic, OpenAI, and Shopify materials that informed the design, and the corresponding adaptation boundaries are documented in [docs/agents/SOURCES.md](docs/agents/SOURCES.md).

## License

Copyright 2026 ginmp8

Unless otherwise stated in an included file, this distribution is licensed under the [Apache License 2.0](LICENSE).

The Apache License 2.0 applies to prompts, agents, skills, scripts, examples, templates, and documentation created specifically for RhapsodIA when those artifacts do not declare another license.

In the full RhapsodIA repository, copied or adapted third-party content remains subject to its original license and notices and is not relicensed merely by inclusion in the repository.


## 0.3.0 (historical) — dual workflow architecture

RhapsodIA 0.3.0 keeps the package release at `0.3.0` while separating two internal control planes:

- `adaptive-workflow-orchestration` / `dynamic-workflow-plan/v1` for runtime-adaptive compile-to-workflow execution;
- `checkpoint-convergence` / `convergence-plan/v1` for reference-grounded checkpoint/gate progression.

Historical `workflow-plan/v1` and `workflow-plan/v2` remain compatibility surfaces. Internal contract versions are semantic and are not forced to match the package release.
