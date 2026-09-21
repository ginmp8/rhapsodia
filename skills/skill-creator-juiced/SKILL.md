---
name: skill-creator-juiced
description: Create, redesign, substantially upgrade, validate, and package portable Agent Skills-compatible skill packages. Use when the user asks to build or improve a skill, convert a repeatable workflow into a skill, choose skill architecture, make a skill portable across ChatGPT/OpenAI, Claude, GitHub Copilot, Cursor, or other Agent Skills hosts, or coordinate specialist quality passes including reproducibility engineering, hardening, benchmarking, harnessing, activation review, testing, security, consistency, cleanup, and token efficiency. Do not use for ordinary code review, product strategy, document writing, or prompt-only rewrites unless the requested deliverable is a reusable skill package.
---

# Skill Creator Juiced

## Mission

Create high-quality reusable skills as operational packages, not generic instruction dumps. Keep the semantic core portable across Agent Skills-compatible hosts, reduce avoidable model freedom with objective mechanisms, preserve model judgment where it is useful, and validate before delivery.

In standalone use, this skill owns net-new skill creation, major redesigns, portability normalization, specialist orchestration, acceptance gates, and final package delivery. `PORTABILITY_OWNER = skill-creator-juiced`: do not create a parallel portability specialist unless this responsibility is deliberately extracted in a future architecture change. It does not replace the specialists it routes to.


## Scope

Use for skill packages, package architecture, workflow-to-skill conversion, host portability, progressive loading, reusable scripts/references/assets, validation, specialist routing, and final archive delivery.

Preserve one canonical skill when the operational responsibility is unchanged. Do not create a host-specific fork merely to support another compatible host; use a portable core plus optional adapters. Split only when activation, ownership, evidence, tools, or validation lifecycle materially differ.

## Required Inputs and Defaults

Resolve or infer before writing files:

1. target skill name, folder, or proposed capability;
2. activation, non-activation, ambiguous, and edge prompts when available;
3. expected inputs, outputs, language, format, citations, and evidence rules;
4. required capabilities such as filesystem read/write, command execution, network access, connectors, subagents, or artifact delivery;
5. target hosts when portability matters; portability/redesign defaults to `portable-core,openai,codex,claude,copilot,cursor` unless the user explicitly narrows support;
6. blocked paths, fixtures, expected outputs, secrets, evaluator evidence, and packaging expectations.

Default to the open Agent Skills format as the canonical core. Detect capabilities instead of assuming product-specific tool names. Mutate only the target skill folder. Keep `.git`, secrets, credentials, fixtures, expected outputs, frozen evaluator evidence, generated baseline evidence, old archives, and unrelated files protected.

## Modes

| Mode | Use when | Primary result |
|---|---|---|
| `create` | net-new skill from examples or workflow | complete skill package |
| `redesign` | existing skill needs architecture or portability change | bounded redesign and updated package |
| `quality-upgrade` | hardening, reproducibility, benchmark, validation, cleanup, or token-efficiency work | validated candidate plus specialist ledger |
| `portability` | host-neutralization or multi-host compatibility is the main goal, including Booster handoff for host-coupled external skills | portable core plus optional adapters and explicit compatibility matrix |
| `package` | final archive requested | validated `skill.zip` |
| `explain-or-route` | the request is not actually skill work | concise handoff |

## Authority Boundary

- **Standalone:** own creation/redesign/portability, acceptance, and package delivery within this skill's scope.
- **Delegated:** when an upstream orchestrator calls this skill, mutate only the assigned batch, preserve frozen evaluator/peer contracts, return candidate evidence, and leave global sequencing, final promotion, installation, and policy authority to the caller. A breaking peer contract requires a coordinated change set.

## Core Rules

- Preserve the target skill's purpose, constraints, examples, safety boundaries, and expected outputs.
- Infer the target's current lifecycle state and harvest established context before asking questions or repeating earlier workflow stages.
- Prefer one cohesive capability over duplicated host-specific variants.
- Keep `SKILL.md` as the compact control plane; move detailed branches, rubrics, schemas, and host notes to `references/`.
- Use scripts for deterministic, fragile, repetitive, validation-heavy, or packaging work; do not encode subjective judgment as fake determinism.
- Treat examples and evals as calibration or planned evidence until they are actually executed.
- For behavioral comparison, use `without-skill` as the net-new baseline when meaningful and an immutable prior-version snapshot for existing-skill updates; otherwise mark comparison `not-run`.
- Generalize from failures instead of hard-coding eval prompts, filenames, fixtures, or wording. Use held-out scenarios when making improvement or activation-quality claims.
- Never fabricate validation, benchmark scores, portability, package readiness, or security status.
- Prefer the lowest reliable control layer: `runtime/script > schema/type > validator/gate > reference/rubric > free-form prompt`.
- Preserve backward compatibility unless the user explicitly authorizes a breaking change and migration evidence exists.
- After the final passing validation, freeze the candidate. Any later content change requires rerunning affected gates before delivery.

## Host Portability

Read [references/host-portability.md](references/host-portability.md) whenever the target host is uncertain, multiple hosts are requested, or host-specific metadata/tools affect behavior.

Portable defaults:

- use the Agent Skills `SKILL.md` contract as source of truth;
- when portability is the objective, target `portable-core,openai,codex,claude,copilot,cursor` by default and record an explicit result for each profile;
- use relative package paths;
- keep scripts self-contained or document dependencies explicitly;
- describe required capabilities, not product-specific tool names, unless the skill intentionally targets one host;
- treat `agents/openai.yaml` and other host metadata as optional adapters, never as semantic requirements of the portable core;
- keep host-only frontmatter or installation conventions out of the canonical core unless portability is intentionally narrowed;
- when a host lacks a capability, degrade explicitly, mark the affected gate `not-run`, and do not claim equivalent validation.

## Resource Loading

Load only what the active branch needs:

- [references/creation-workflow.md](references/creation-workflow.md) for the ordered build/update path.
- [references/design-principles.md](references/design-principles.md) for cohesion, router, mode, split, and progressive-loading decisions.
- [references/host-portability.md](references/host-portability.md) for cross-host rules and adapters.
- [references/reproducibility-by-design.md](references/reproducibility-by-design.md) during package design to classify the reproducibility ceiling, map variability, and choose proportional controls before specialist routing.
- [references/reproducibility-routing.md](references/reproducibility-routing.md) for the `Reproducibility Engineer` decision gate, ownership, ordering, and cycle guards.
- [references/evaluation-and-generalization.md](references/evaluation-and-generalization.md) for lifecycle-aware entry, baseline selection, evaluation strategy, anti-overfitting, activation evals, and repeated-work extraction.
- [references/specialist-orchestration.md](references/specialist-orchestration.md) for specialist selection and sequencing.
- [references/quality-gates.md](references/quality-gates.md) before readiness or delivery claims.
- `evals/activation-scenarios.json` for the frozen baseline activation suite when present.
- `evals/portability-scenarios.json` for planned cross-host and reproducibility-routing coverage.
- `examples/creation-scenarios.md` for compact calibration examples.
- `scripts/validate_portability.py` for portable/static validation across `portable-core`, OpenAI, Codex, Claude, GitHub Copilot, and Cursor.
- `scripts/juiced_quality_gate.py` for structural package quality validation.
- `scripts/package_skill.py` for atomic validated packaging and package receipt generation.
- `assets/templates/skill-delivery-report.md.template` when a durable report is useful.

## Workflow

Follow [references/creation-workflow.md](references/creation-workflow.md):

1. Infer lifecycle state, harvest established context, and establish target identity, scope, protected evidence, host/runtime capabilities, and the appropriate baseline.
2. Decide cohesion: unified skill, modes, router, or split.
3. Design the portable package core and optional host adapters. When portability is the objective, preserve one semantic core, classify each host-specific feature as optional adapter/optimization, required capability, or blocker, and produce a compatibility matrix for `portable-core,openai,codex,claude,copilot,cursor` unless explicitly narrowed.
4. Draft or update the smallest coherent set of files, define the evaluation contract, and apply the proportional reproducibility-by-design pass from [references/reproducibility-by-design.md](references/reproducibility-by-design.md).
5. Run the reproducibility decision gate from [references/reproducibility-routing.md](references/reproducibility-routing.md) only after local design controls are understood; invoke the specialist when material gaps remain or deeper reproducibility work is explicitly required.
6. Run only the specialist passes that own material risks.
7. Evaluate against the correct baseline when possible; inspect failures for generalizable causes, use held-out scenarios for final claims, and reject eval-specific fixes.
8. Repair by diagnosis: rerun the narrowest failing gate after each fix; stop random search after two non-improving rounds.
9. Validate portability, package structure, scripts, references, and target-owned tests. Portability/redesign must run the requested host matrix; a structural pass is not runtime proof.
10. Apply change acceptance for existing-skill updates.
11. Freeze the passing candidate, package atomically, and report evidence by layer.

## Reproducibility Engineer Integration

`reproducibility-engineer` is conditional, not mandatory. Use [references/reproducibility-routing.md](references/reproducibility-routing.md) to classify it as `not-applicable`, `audit-only`, `plan-only`, `apply`, or `validation-only`.

Every substantive create/redesign first applies the local `reproducibility-by-design` checklist. Invoke the specialist when material variability still requires a dedicated transformation through semantic contracts, normalized routing, schemas, deterministic helpers, independent validators, bounded repair loops, frozen evaluators, immutable source evidence, traceable package identity, output-alias protection, recovery-aware delivery, or controlled external nondeterminism. Skip it when variability is intentionally subjective and the local controls already cover material risk.

The Juiced skill remains orchestrator and acceptance owner. `reproducibility-engineer` owns only the reproducibility transformation it is assigned. `skill-change-gate` owns candidate acceptance. Do not allow specialists to call each other recursively without a new unmet responsibility.

## Specialist Orchestration

Read [references/specialist-orchestration.md](references/specialist-orchestration.md). Use the smallest useful set of specialists. A high-quality request does not justify running irrelevant passes.

For existing-skill redesigns or quality upgrades, normally establish architecture and activation boundaries before the reproducibility gate. Run downstream testing, harness, benchmark, security, consistency, cleanup, and hardening against the resulting candidate. Use `skill-hypothesis-discovery` when several evidence-backed improvement directions compete, and `skill-change-gate` before accepting material changes.

## Quality Gates

Before delivery, apply [references/quality-gates.md](references/quality-gates.md). At minimum:

- validate Agent Skills frontmatter and package shape;
- validate local references and required support files;
- classify host-specific dependencies and adapters;
- record the reproducibility ceiling and proportional controls from `reproducibility-by-design` when material;
- confirm `reproducibility-engineer` routing status with rationale when applicable;
- verify material source/evaluator identity, output-path alias safety, last-good preservation/recovery, and durable receipts when those controls apply;
- run changed scripts or mark them `not-run` with reason;
- preserve frozen evaluator assets and protected evidence;
- verify that behavioral fixes are generalizable, use the correct comparison baseline, and keep objective assertions separate from subjective/perceptual review;
- require change acceptance for material updates to existing skills;
- package only the final validated candidate.

When command execution is available:

```text
<PYTHON> scripts/validate_portability.py <target-skill-folder> --hosts portable-core,openai,codex,claude,copilot,cursor
<PYTHON> scripts/juiced_quality_gate.py <target-skill-folder> --profile portable --hosts portable-core,openai,codex,claude,copilot,cursor
<PYTHON> scripts/package_skill.py --target <target-skill-folder> --output <output-dir>/skill.zip --profile portable --validate --portability-hosts portable-core,openai,codex,claude,copilot,cursor --json-output <output-dir>/package-receipt.json
```

Resolve `<PYTHON>` to an available Python 3 interpreter; do not assume the executable name.

## Evidence Layers

Keep claims separate:

- **structural evidence**: package shape, frontmatter, references, script syntax, hashes, validators;
- **behavioral evidence**: executed scenarios and evaluator results;
- **runtime evidence**: actual host/tool execution;
- **perceptual evidence**: human or image-capable review for subjective quality.

A pass in one layer does not imply another.

## Output Contract

For substantive creation or update work, report:

1. target skill and mode;
2. architecture decision, portability profile, requested host set, and compatibility matrix;
3. changed files and purpose;
4. specialists invoked, checklist-applied, skipped, unavailable, or not-applicable with reasons;
5. reproducibility-by-design classification/controls and the `reproducibility-engineer` routing decision when applicable;
6. commands executed with `pass`/`fail`/`not-run`;
7. structural, behavioral, runtime, and perceptual evidence separately;
8. change-gate status for material existing-skill updates;
9. residual risks and unsupported hosts/capabilities;
10. package path and hash only when the exact archive exists and all applicable hard gates pass.

## Stop Conditions

Stop or return a bounded partial result when:

- zero or multiple target roots exist and identity cannot be resolved;
- source truth required for semantic behavior is unavailable;
- the requested change would edit protected evidence or unrelated paths;
- portability requires a host-only capability with no safe degradation and the user requires equivalent behavior everywhere;
- a required evaluator cannot be frozen or protected;
- a specialist cycle would re-enter the current owner without new responsibility;
- validation fails and the only route to success is weakening semantics, safety, evidence, or thresholds;
- the user requests measured improvement without executed or supplied evidence.
