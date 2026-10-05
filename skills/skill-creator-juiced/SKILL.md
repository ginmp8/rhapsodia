---
name: skill-creator-juiced
description: Create or substantially redesign portable Agent Skills-compatible packages. Use for net-new skills, workflow-to-skill conversion, skill architecture, major portability redesigns, or coordinated quality upgrades that change package structure. Do not use for ordinary optimization of an existing skill whose responsibility stays the same; use Skill Booster for that.
---

# Skill Creator Juiced

## Mission

Create high-quality reusable skills as operational packages, not generic instruction dumps. Keep one portable semantic core, reduce avoidable model freedom with objective mechanisms, preserve useful model judgment, and validate before delivery.

Own net-new skill creation, major redesign, portability normalization, specialist orchestration, acceptance gates, and final package delivery. `PORTABILITY_OWNER = skill-creator-juiced`; do not create a parallel portability specialist unless responsibility is deliberately extracted.

## Activation and Routing

Use this skill when the requested deliverable is a reusable Agent Skills package and at least one is true:

- create a net-new skill from examples, workflow, artifacts, or a specification;
- convert repeated work into a skill package;
- choose or change skill architecture, cohesion, split/router/mode boundaries, or portability model;
- substantially redesign an existing skill so activation, ownership, evidence, tools, or validation lifecycle changes;
- coordinate a quality upgrade whose accepted solution changes package architecture.

Do not use for ordinary application code, generic repository refactors, document writing, product strategy, or prompt-only rewrites. For an existing skill that keeps the same responsibility and mainly needs optimization, hardening, benchmarking, compression, validation, or packaging, route to `skill-booster`.

## Top-100 Context Contract

Every skill created or substantially redesigned here must make its primary decision and execution surface visible within the first 100 physical lines of `SKILL.md`.

Within those first 100 lines, expose the smallest complete control plane needed to act correctly:

1. frontmatter `name` and a discriminative `description` that states what the skill does, when to use it, and a material non-use boundary when overlap is plausible;
2. purpose/scope and activation or routing boundary;
3. mode/router decision when the skill has materially different branches;
4. workflow, quick start, or execution sequence sufficient to begin correctly;
5. non-negotiable rules, constraints, or invariants that could materially change behavior;
6. direct pointers to branch-specific resources needed after the initial decision.

Treat line 100 as a context-engineering budget, not a reason to duplicate details. Put branch detail after the decision surface or in directly linked references. Read [references/context-loading-contract.md](references/context-loading-contract.md) for the reusable authoring and validation rules.

Supporting Markdown follows the same preview-first contract: every editable `.md` over 100 physical lines must put an `At a Glance`, summary, or equivalent near the top followed by a `Contents`/section map derived from its actual material `##` headings in document order. The index must not invent headings, omit material H2 sections, or drift after heading changes; generated/vendor Markdown may use the explicit documented exception defined in the context-loading contract. Missing or stale long-document previews fail structural readiness. Prefer a single reference level: `SKILL.md -> supporting file`. Avoid reference-to-reference discovery chains; if a supporting file is important, link it directly from `SKILL.md`.

## Modes

| Mode | Use when | Primary result |
|---|---|---|
| `create` | net-new skill from examples or workflow | complete skill package |
| `redesign` | existing skill needs architecture, activation-boundary, or portability change | bounded redesign and updated package |
| `quality-upgrade` | a coordinated quality pass materially changes package structure | validated candidate plus specialist ledger |
| `portability` | host-neutralization or multi-host compatibility is the main goal | portable core plus optional adapters and explicit compatibility matrix |
| `package` | final archive requested | validated `skill.zip` |
| `explain-or-route` | the request is not actually skill work | concise handoff |

## Workflow at a Glance

1. Infer lifecycle state, creation origin, target identity, scope, protected evidence, runtime capabilities, and baseline.
2. Run the Artifact Selection Gate; stop if a skill is the wrong customization primitive.
3. Decide cohesion: one skill, modes, router, or split.
4. Design the portable core and optional host adapters.
5. Draft the smallest coherent package and enforce the Top-100 Context Contract before adding detail.
6. Define evaluation and proportional reproducibility controls.
7. Run only specialist passes that own material risks.
8. Evaluate against the correct baseline; use held-out activation cases for final routing claims when possible.
9. Repair diagnosed causes, not individual eval wording.
10. Validate structure, direct references, Top-100 coverage, scripts, requested hosts/surfaces, and target-owned tests.
11. Apply change acceptance for material existing-skill updates.
12. Freeze the passing candidate, package atomically, and report evidence by layer.

## Core Rules

- Preserve purpose, constraints, safety boundaries, examples, and expected outputs unless the authorized redesign intentionally changes them.
- Do not assume every reusable customization belongs in a skill; route always-on rules, custom agents, tools/MCP, hooks, plugins, or prompt/document assets to their proper owner.
- Prefer one cohesive portable capability over duplicated host-specific variants.
- Keep `SKILL.md` as a compact control plane; keep its main decision/execution surface in the first 100 lines and detailed branch material in directly linked resources.
- Prefer one-level Markdown discovery. A reference may use anchors or external sources, but do not make another Markdown file the only route to required instructions.
- Apply model-neutral minimality: isolate host/model workarounds in adapters or scoped references with provenance.
- Use scripts for deterministic, fragile, repetitive, validation-heavy, or packaging work; do not fake determinism for subjective judgment.
- Treat examples and evals as calibration or planned evidence until executed.
- Generalize from failures instead of hard-coding eval prompts, filenames, fixtures, or wording.
- Never fabricate validation, benchmark scores, portability, package readiness, or security status.
- Prefer the lowest reliable control layer: `runtime/script > schema/type > validator/gate > reference/rubric > free-form prompt`.
- Preserve backward compatibility unless a breaking change is explicitly authorized and migration evidence exists.
- After final passing validation, freeze the candidate; any later content change requires affected gates to rerun.

## Resource Loading

Load only what the active branch needs, and keep required Markdown directly reachable from this file:

- [references/context-loading-contract.md](references/context-loading-contract.md) for Top-100, preview-first Markdown, discovery metadata, and one-level reference rules.
- [references/creation-workflow.md](references/creation-workflow.md) for the ordered build/update path.
- [references/design-principles.md](references/design-principles.md) for artifact choice, cohesion, progressive loading, and minimality.
- [references/host-portability.md](references/host-portability.md) for cross-host rules, profiles, surfaces, and adapters.
- [references/reproducibility-by-design.md](references/reproducibility-by-design.md) for proportional reproducibility controls.
- [references/reproducibility-routing.md](references/reproducibility-routing.md) for the `Reproducibility Engineer` decision gate.
- [references/evaluation-and-generalization.md](references/evaluation-and-generalization.md) for lifecycle-aware evaluation, activation cases, and anti-overfitting.
- [references/specialist-orchestration.md](references/specialist-orchestration.md) for specialist ownership and sequencing.
- [references/quality-gates.md](references/quality-gates.md) before readiness or delivery claims.
- [evals/activation-scenarios.json](evals/activation-scenarios.json) and [evals/portability-scenarios.json](evals/portability-scenarios.json) for frozen scenario coverage.
- [examples/creation-scenarios.md](examples/creation-scenarios.md) for compact calibration examples.
- `scripts/validate_portability.py`, `scripts/juiced_quality_gate.py`, and `scripts/package_skill.py` for deterministic validation and packaging.

## Required Inputs and Defaults

Resolve or infer before writing files:

1. requested reusable outcome and whether a skill is the correct customization primitive;
2. target skill name/folder or proposed capability;
3. creation origin: `extract-from-run`, `synthesize-from-artifacts`, `design-from-spec`, or `adapt-existing`, plus strongest source and material evidence gaps;
4. activation, non-activation, ambiguous, boundary, and edge prompts when available;
5. expected inputs, outputs, language, format, citations, and evidence rules;
6. required capabilities such as filesystem, command execution, network, connectors, subagents, or artifact delivery;
7. semantic/runtime profiles when portability matters; default to `portable-core,openai,codex,claude,copilot,cursor` unless explicitly narrowed;
8. client/distribution surfaces when discovery, installation, packaging, or publication matters; keep them separate from semantic/runtime profiles;
9. blocked paths, fixtures, expected outputs, secrets, evaluator evidence, and packaging expectations.

Default to the open Agent Skills format as canonical core. Detect capabilities instead of assuming product-specific tool names. Mutate only the target skill folder. Protect `.git`, secrets, credentials, fixtures, expected outputs, frozen evaluator evidence, generated baseline evidence, old archives, and unrelated files.

## Authority Boundary

- **Standalone:** own creation/redesign/portability, acceptance, and package delivery within this skill's scope.
- **Delegated:** when an upstream orchestrator calls this skill, mutate only the assigned batch, preserve frozen evaluator/peer contracts, return candidate evidence, and leave global sequencing, final promotion, installation, and policy authority to the caller. A breaking peer contract requires a coordinated change set.

## Host Portability

Read [references/host-portability.md](references/host-portability.md) whenever target host is uncertain, multiple hosts are requested, or host-specific metadata/tools affect behavior.

Portable defaults:

- use the Agent Skills `SKILL.md` contract as source of truth;
- treat `portable-core,openai,codex,claude,copilot,cursor` as semantic/runtime profiles, not a flat list of clients;
- model distribution surfaces separately; for example VS Code and Visual Studio are distinct Copilot surfaces sharing the `copilot` semantic profile;
- use relative package paths and keep canonical semantics identical across compatible distribution surfaces;
- keep scripts self-contained or document dependencies explicitly;
- describe required capabilities, not product-private tool names, unless intentionally host-specific;
- treat `agents/openai.yaml` and other host metadata as optional adapters, never semantic requirements of the portable core;
- reject host-only frontmatter in canonical portable `SKILL.md`;
- when a capability is unavailable, degrade explicitly, mark affected gates `not-run`, and do not claim equivalent validation.

## Reproducibility Engineer Integration

`reproducibility-engineer` is conditional, not mandatory. Use [references/reproducibility-routing.md](references/reproducibility-routing.md) to classify it as `not-applicable`, `audit-only`, `plan-only`, `apply`, or `validation-only`.

Every substantive create/redesign first applies the local reproducibility-by-design checklist. Invoke the specialist only when material variability still needs dedicated transformation through semantic contracts, normalized routing, schemas, deterministic helpers, validators, bounded repair loops, frozen evaluators, immutable evidence, traceable package identity, recovery-aware delivery, or controlled external nondeterminism.

Skill Creator Juiced remains orchestrator and acceptance owner. `reproducibility-engineer` owns only its assigned reproducibility transformation. `skill-change-gate` owns candidate acceptance. Do not allow recursive specialist cycles without a new unmet responsibility.

## Specialist Orchestration

Read [references/specialist-orchestration.md](references/specialist-orchestration.md). Use the smallest useful specialist set.

For research-backed changes, route bounded source -> finding -> requirement/change accounting through `research-traceability` when available. For existing-skill quality work that does not change architecture, prefer handoff to `skill-booster`. Use `skill-hypothesis-discovery` when several evidence-backed directions compete and `skill-change-gate` before accepting material changes.

## Quality Gates

Before delivery, apply [references/quality-gates.md](references/quality-gates.md). At minimum:

- validate Agent Skills frontmatter and package shape;
- enforce the Top-100 Context Contract for long `SKILL.md` files;
- require editable supporting Markdown over 100 lines to have an early summary plus heading-derived Contents synchronized with material H2 headings, or record an explicit generated/vendor/unsafe-to-rewrite exception;
- verify required Markdown is directly discoverable from `SKILL.md` and avoid deeper reference chains;
- validate local references, scripts, semantic/runtime profiles, and requested client/distribution surfaces;
- preserve frozen evaluator assets and protected evidence;
- separate structural, behavioral, runtime, and perceptual evidence;
- require change acceptance for material updates to existing skills;
- package only the final validated candidate.

When command execution is available:

```text
<PYTHON> scripts/validate_portability.py <target-skill-folder> --hosts portable-core,openai,codex,claude,copilot,cursor --surfaces chatgpt,openai-api,codex,claude-code,copilot-vscode,copilot-visual-studio,cursor
<PYTHON> scripts/juiced_quality_gate.py <target-skill-folder> --profile portable --hosts portable-core,openai,codex,claude,copilot,cursor --surfaces chatgpt,openai-api,codex,claude-code,copilot-vscode,copilot-visual-studio,cursor
<PYTHON> scripts/package_skill.py --target <target-skill-folder> --output <output-dir>/skill.zip --profile portable --validate --portability-hosts portable-core,openai,codex,claude,copilot,cursor --distribution-surfaces chatgpt,openai-api,codex,claude-code,copilot-vscode,copilot-visual-studio,cursor --json-output <output-dir>/package-receipt.json
```

Resolve `<PYTHON>` to an available Python 3 interpreter; do not assume one spelling.

## Evidence Layers

Keep claims separate:

- **structural evidence:** package shape, frontmatter, Top-100 coverage, reference depth, links, script syntax, hashes, validators;
- **behavioral evidence:** executed scenarios and evaluator results;
- **runtime evidence:** actual host/tool execution;
- **perceptual evidence:** human or image-capable review for subjective quality.

A pass in one layer does not imply another.

## Output Contract

For substantive creation or update work, report target/mode; artifact and architecture decisions; hosts/surfaces; changed files; specialist/reproducibility routing; validation commands and outcomes; Top-100/reference-depth status; evidence by layer; change-gate status; residual risks; and package path/hash only when the exact archive exists and applicable hard gates pass.

## Stop Conditions

Stop or return a bounded partial result when target identity cannot be resolved; source truth required for semantic behavior is unavailable; protected evidence/unrelated paths would be modified; artifact selection shows a skill is the wrong primitive; equivalent cross-host behavior is required but a capability has no safe degradation; a required evaluator cannot be frozen; a specialist cycle would re-enter without new responsibility; validation fails and the only path to green weakens semantics/safety/evidence/thresholds; or measured improvement is requested without executed or supplied evidence.
