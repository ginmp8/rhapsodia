# Host Portability

## At a Glance

- **Purpose:** Define the two-dimensional portability model that separates semantic/runtime profiles from client/distribution surfaces and protects one canonical portable core.
- **Load when:** Multiple or uncertain hosts are targeted, an IDE/client surface is named, or a host-specific feature could affect package semantics.
- **Decision impact:** Determines canonical core versus adapter responsibilities, profile/surface mapping, packaging profiles, safe degradation, and the scope of portability claims.

## Contents

- Two-dimensional portability model
- Canonical portable core
- Common-denominator rules
- Default profile matrix
- Host-extension containment
- Runtime and surface notes
- Canonical package versus distribution adapters
- Packaging profiles
- Current source anchors
- Validation command


Use this reference when creating or updating a skill for more than one semantic runtime, when the target runtime is uncertain, when a client/IDE/distribution surface is named, or when a host-specific feature could leak into the canonical workflow.

## Two-dimensional portability model

Do not treat runtimes, IDEs, and distribution clients as one flat host list.

### Dimension 1: semantic/runtime profiles

These profiles answer whether the same skill semantics and required capabilities can run under a compatible agent runtime:

`portable-core,openai,codex,claude,copilot,cursor`

They are the default structural portability matrix unless the user deliberately narrows support.

### Dimension 2: client/distribution surfaces

These surfaces answer where the skill is discovered, installed, uploaded, packaged, or updated. They do not create a new semantic fork by themselves.

| Surface | Semantic profile | Meaning |
|---|---|---|
| `chatgpt` | `openai` | ChatGPT skill surface |
| `openai-api` | `openai` | OpenAI API/tool skill distribution |
| `codex` | `codex` | Codex skill discovery/execution surfaces |
| `claude-code` | `claude` | Claude Code skill discovery |
| `claude-ai-api` | `claude` | claude.ai/API custom skill packaging |
| `copilot-github` | `copilot` | GitHub-hosted Copilot agent surface |
| `copilot-vscode` | `copilot` | VS Code Copilot skill discovery |
| `copilot-visual-studio` | `copilot` | Visual Studio Copilot Agent Skills surface |
| `cursor` | `cursor` | Cursor Agent Skills surface |

A surface mapping is structural/distribution evidence only. It does not prove runtime behavior in that client.

## Canonical portable core

Treat the open Agent Skills format as the canonical core:

```text
skill-name/
├── SKILL.md
├── scripts/      # optional
├── references/   # optional
├── assets/       # optional
└── ...           # additional package files when useful
```

The portable core must not depend semantically on a single vendor's UI metadata, install path, tool-call syntax, agent runtime implementation detail, or client/IDE discovery path. Host-specific files may coexist as optional adapters when another runtime can safely ignore them.

## Common-denominator rules

1. Keep `name` and `description` valid under the Agent Skills specification.
2. Keep canonical `SKILL.md` frontmatter to the standard Agent Skills fields. Host-only fields belong in adapters or intentionally narrowed host packages; a package claiming `portable-core` must reject host-only frontmatter leakage.
3. Use `license`, `compatibility`, `metadata`, or `allowed-tools` only when they add real value; `allowed-tools` is experimental and must never be required for correctness or permission bypass.
4. Use relative paths from the skill root for bundled resources.
5. Keep required branch resources directly discoverable from `SKILL.md` or one declared root index; do not make a required rule depend on a hidden multi-hop reference chain.
6. Describe capabilities such as filesystem read/write, command execution, network access, subagents, connectors, browser access, and artifact delivery. Do not hardcode a vendor-specific tool name unless the skill intentionally targets one runtime.
7. Resolve runtime executables by capability. For example, resolve an available Python 3 interpreter instead of assuming `python` exists.
8. Portable helper behavior must not change merely because an optional third-party parser/runtime package is installed. Use one bundled/standard-library path or declare the dependency as a real capability requirement.
9. Keep validation claims capability-aware. Missing shell, Python, browser, network, subagents, or connectors means the affected gate is `not-run`, not passed.
10. Keep install/discovery locations outside the semantic contract. A skill folder should be movable without rewriting its instructions.
11. Do not duplicate the skill merely because clients use different discovery directories.

## Default profile matrix

When portability is the objective, validate these semantic profiles unless the user explicitly narrows scope:

`portable-core,openai,codex,claude,copilot,cursor`

Use one canonical package. Report each semantic profile as one of:

- `validated`: runtime evidence actually executed and passed;
- `structurally-compatible`: static package/profile checks passed, runtime not executed;
- `adapter-required`: core is portable but optional host metadata/adapter is required for the requested integration surface;
- `capability-limited`: the runtime lacks a capability and the skill has an explicit safe degradation;
- `not-run`: relevant verification could not execute;
- `unsupported`: no safe equivalent/degradation exists for a required capability.

Never promote `structurally-compatible` to `validated` without runtime evidence.

For client/distribution surfaces, report the mapped semantic profile, adapter/discovery requirement, and whether surface-specific verification actually ran. A static map is not an IDE/runtime test.

## Host-extension containment

The canonical portable `SKILL.md` may use only Agent Skills frontmatter fields. Known examples of host extensions that must not leak into a package claiming `portable-core` include:

- Cursor-specific fields such as `paths` and `disable-model-invocation`;
- Claude Code-only fields such as `argument-hint`, `user-invocable`, `model`, `context`, `agent`, or `hooks` when they are not part of the open Agent Skills contract;
- vendor-private tool-call syntax, sandbox paths, install directories, or permission bypass assumptions in the portable body.

Classify every host-specific feature as one of:

- `optional-adapter`: safe to include because the portable core works without it;
- `optional-optimization`: improves one runtime/client but does not change semantics;
- `required-host-capability`: narrows the support matrix and must be declared;
- `portability-blocker`: the user requires equivalent multi-platform behavior but no common or degradable implementation exists.

For every retained extension record the owning host/surface, semantic effect, fallback when ignored, and support-matrix impact. Do not silently convert a portable skill into a single-host skill.

## Runtime and surface notes

### OpenAI / ChatGPT / API

OpenAI consumes Agent Skills-compatible packages. `agents/openai.yaml` may be included as OpenAI-specific UI/policy/dependency metadata, but portable behavior must not depend on it. Hosted/API packaging may use a zip or directory bundle. Keep the archive rooted at one skill directory.

Treat ChatGPT and OpenAI API as distribution surfaces mapped to the `openai` semantic profile. Upload/version-pointer behavior belongs to the distribution layer, not the portable semantic core.

### Codex

Treat Codex as its own semantic profile even when it shares OpenAI ecosystem metadata. Codex-specific discovery paths or private tool names must not be required by the package.

### Claude

Anthropic's Skills implementation and reference ecosystem use `SKILL.md` skill folders and point to the Agent Skills specification. Claude Code can expose additional frontmatter and execution controls; those are host extensions and must not be required by the portable core. claude.ai/API packaging is a separate distribution surface and may reject Claude Code-only metadata.

### GitHub Copilot / VS Code / Visual Studio

Use one `copilot` semantic profile. Treat GitHub-hosted, VS Code, and Visual Studio experiences as distinct client/distribution surfaces because discovery locations and release cadence can differ.

Visual Studio Agent Skills support does not justify a `visual-studio` semantic fork. Map `copilot-visual-studio -> copilot` and validate runtime behavior separately only when that client is actually available.

### Cursor

Cursor supports Agent Skills and discovers skills from its own directories plus compatibility locations. Cursor-only frontmatter such as `paths` or `disable-model-invocation` can be useful for a narrowed Cursor package, but it must not be required by the portable core.

## Canonical package versus distribution adapters

The canonical source package is the validated skill folder/archive whose semantics are independent of installation client.

Distribution adapters may add or record:

- upload/version pointers;
- repository origin/ref/tree provenance;
- install/update commands;
- plugin manifests or wrappers;
- client-specific UI metadata;
- discovery locations.

They must not silently rewrite the canonical `SKILL.md` semantics. Record requested distribution surfaces separately in the package receipt when available.

Release/version policy, changelog strategy, and publish governance remain separate responsibilities from package semantics.

## Packaging profiles

### `portable`

Canonical package profile and hard gate for `portable-core`. Validate the Agent Skills core, relative references, package hygiene, host-neutral semantics, host-extension containment, and self-contained mechanics. Do not require `agents/openai.yaml`.

### `openai`

Use only when an OpenAI-specific package is explicitly requested. Run all portable checks, then require the OpenAI adapter expected by the package contract.

Other runtimes normally consume the same portable folder in their supported discovery location. Do not create separate semantic package contents unless runtime behavior, authority, evidence, or validation genuinely differ.

## Current source anchors

Rules in this reference were aligned on 2026-10-04 with:

- Agent Skills specification: `https://agentskills.io/specification`
- Agent Skills creator best practices: `https://agentskills.io/skill-creation/best-practices`
- OpenAI Skills guide: `https://developers.openai.com/api/docs/guides/tools-skills`
- OpenAI plugin skills guide: `https://developers.openai.com/plugins/build/skills`
- GitHub Copilot Agent Skills: `https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills`
- GitHub Copilot CLI customization comparison: `https://docs.github.com/en/copilot/concepts/agents/copilot-cli/comparing-cli-features`
- VS Code Agent Skills: `https://code.visualstudio.com/docs/agent-customization/agent-skills`
- Visual Studio Agent Skills: `https://learn.microsoft.com/en-us/visualstudio/ide/copilot-agent-skills?view=visualstudio`
- Cursor Agent Skills: `https://cursor.com/docs/skills`
- Claude Code Skills: `https://code.claude.com/docs/en/skills`

Host behavior can change. Recheck authoritative documentation when a platform-specific feature is material to correctness.

## Validation command

```text
<PYTHON> scripts/validate_portability.py <target> \
  --hosts portable-core,openai,codex,claude,copilot,cursor \
  --surfaces chatgpt,openai-api,codex,claude-code,copilot-vscode,copilot-visual-studio,cursor
```

The validator provides structural profile and surface-mapping evidence. Runtime compatibility remains a separate evidence layer.
