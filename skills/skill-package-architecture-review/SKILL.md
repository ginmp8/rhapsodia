---
name: skill-package-architecture-review
description: review, map, compare, or assess the internal architecture of an Agent Skills-compatible skill package, including SKILL.md control-plane design, references, scripts, assets, examples, evals, validators, dependency/resource/ownership maps, progressive loading, boundaries, handoffs, package cohesion, and whether to keep unified, split, extract a mode, create a router, merge resources, or make no structural change. use for evidence-based package architecture review, not generic implementation, hardening execution, benchmark ownership, or target-domain rewrites.
---

# Skill Package Architecture Review

## Purpose

Review a reusable skill package as a system of control plane, resources, evidence, ownership boundaries, workflows, validators, and handoffs. Make repeated reviews of the same package materially comparable by starting from the same package identity, structural evidence model, rubric version, and report contract.

Preserve valid architecture. Reduce unjustified reviewer variance; do not replace context-dependent architectural judgment with rigid standardization.

## Authority boundary

This skill is review-first. It may run read-only inventory and report validators. It does not mutate the reviewed target unless the user separately grants mutation authority and the appropriate implementation/hardening workflow is active.

Do not:

- implement generic code changes;
- rewrite the target skill domain without package, repository, user, or supplied-source evidence;
- mutate benchmark fixtures or expected outputs;
- recommend deletion from filename, size, or absent direct `SKILL.md` reference alone;
- call planned scenarios, static inspection, or rubric scores measured behavior;
- force a preferred folder pattern when the existing design is coherent and maintainable.

## Reproducibility ceiling

This is a research/analytic skill.

Mechanically reproducible:

- deterministic inventory and package identity;
- dependency, resource, ownership-role, and direct loading maps;
- local-link checks;
- report field/schema validation;
- scenario/evaluator identity.

Bounded judgment remains necessary for cohesion, maintenance cost, ownership fit, future evolution, and trade-offs between valid architectures. Every such judgment must cite evidence and remain distinguishable from observation.

## Modes

Use the smallest mode that answers the request. Explicit user mode wins.

| Mode | Select when | Output |
|---|---|---|
| `package-map` | files, roles, dependencies, consumers, ownership surface, or package identity are the question | deterministic structural evidence |
| `progressive-loading-review` | control-plane size, conditional references, hidden loading, or context efficiency is the question | loading findings |
| `resource-integration-review` | orphan/duplicate/excess/misplacement/integration is the question | resource findings after consumer tracing |
| `governance-boundary-review` | ownership, authority, handoffs, adjacent skills, or stop conditions are the question | boundary findings |
| `content-quality-review` | reference clarity, actionability, flow, or maintainability is the question | content findings |
| `repo-structure-review` | folder layout, package hygiene, validators, or artifact boundaries are the question | structure findings |
| `architecture-recommendation` | user asks whether to keep, split, extract, route, merge, or change architecture | one primary architecture decision plus alternatives |
| `review-report` | user asks for a complete/durable review across several areas | canonical report contract |

If several modes could apply and the user asks for a complete architecture review, use `review-report`. Otherwise prefer the narrowest matching mode.

## Progressive loading

Read target `SKILL.md` first. Then load only what the active mode needs:

- [`references/architecture-evidence-model.md`](references/architecture-evidence-model.md): evidence identity, deterministic maps, resource/ownership taxonomy, consumer tracing, and observation versus judgment.
- [`references/package-architecture-rubric.md`](references/package-architecture-rubric.md): rubric v2.0.0, decision criteria, evidence minimums, tie-breakers, severity, and scoring when requested.
- [`references/progressive-loading-patterns.md`](references/progressive-loading-patterns.md): loading review criteria and recommendation patterns.
- [`references/resource-integration-checklist.md`](references/resource-integration-checklist.md): integration/duplicate/orphan/deletion discipline.
- [`references/governance-boundary-checklist.md`](references/governance-boundary-checklist.md): authority, ownership, handoffs, and adjacent-skill boundaries.
- [`references/architecture-report-contract.md`](references/architecture-report-contract.md): stable logical report schema and claim vocabulary.
- [`evals/architecture-review-scenarios.json`](evals/architecture-review-scenarios.json): frozen regression/activation suite; treat as planned until actually executed.
- [`assets/templates/package-review-report.md.template`](assets/templates/package-review-report.md.template): Markdown rendering skeleton for durable reports.
- [`scripts/inventory_skill_package.py`](scripts/inventory_skill_package.py): deterministic structural evidence and package SHA-256.
- [`scripts/validate_architecture_report.py`](scripts/validate_architecture_report.py): machine-readable report gate.
- [`scripts/self_test.py`](scripts/self_test.py): deterministic helper self-test.

Keep the portable semantic core in `SKILL.md`, references, scripts, assets, and evals. Treat `agents/openai.yaml` and equivalent host metadata as optional adapters unless package evidence proves the semantic workflow depends on them.

## Workflow

### 1. Resolve the exact target

Identify one package root containing the target `SKILL.md`. Record target path/source, selected mode, available capabilities, and missing evidence. If target identity is ambiguous, stop rather than combining packages.

### 2. Freeze structural identity before judgment

When command execution and Python 3.10+ are available, run:

```text
<PYTHON> scripts/inventory_skill_package.py --target <TARGET> --json-output <WORK>/inventory.json
```

Record `package_identity_sha256` and inventory schema version. For repeated reviews, compare only reports tied to the same package identity unless the change is intentional and explicitly noted.

If the script cannot run, build the same evidence classes manually, mark exact package identity `not-measured`, and do not claim exact-repeatability or package-hash equivalence.

### 3. Build the same evidence model

Use `references/architecture-evidence-model.md`.

Capture, in deterministic path order when possible:

1. file/resource inventory;
2. dependency edges;
3. resource role/taxonomy;
4. ownership-role map;
5. consumer evidence;
6. `SKILL.md` direct progressive-loading declarations;
7. local-link and package hygiene facts;
8. validators, templates, evals, and host adapters.

Never interpret `unresolved-no-evidence` as `orphaned`.

### 4. Trace consumers before resource judgments

Before `orphaned`, `obsolete`, `duplicate`, merge, deprecation, or deletion recommendations, trace:

- direct `SKILL.md` references;
- references and mode routing;
- script imports, reads, globs, path construction, templates, validators, and package commands;
- eval/example consumers;
- intentionally asset-only/runtime use;
- host adapters and external consumers when evidence indicates they may exist.

If consumers cannot be ruled out, classify the resource `unknown` or `weakly-integrated`, not removable.

### 5. Analyze progressive loading

Apply `references/progressive-loading-patterns.md`. Separate observed loading facts from judgment about cognitive/context cost. Size alone is never a split criterion.

### 6. Apply rubric v2.0.0

Use `references/package-architecture-rubric.md` for every `architecture-recommendation` and `review-report` decision.

Evaluate exactly these primary decisions:

- `keep_unified`
- `split`
- `extract_mode`
- `create_router`
- `merge_resources`
- `no_change`

A handoff is a next action, not a seventh architecture decision.

Use the rubric's minimum evidence and tie-breaker order. When several architectures remain valid, prefer the smallest change that resolves an evidenced problem. If no evidenced problem requires structural change, `no_change` is valid and should not be treated as indecision.

### 7. Separate observation from architectural judgment

Every material claim must be one of:

- **observation**: mechanical, declared-contract, behavioral, supplied, or derived evidence;
- **judgment**: architectural interpretation tied to observation IDs and confidence;
- **recommendation**: proposed action tied to observations/judgments plus a validation gate.

Do not rewrite observations into stronger judgments without evidence.

### 8. Validate and report

For durable reports, follow `references/architecture-report-contract.md`. When emitting the canonical JSON companion, validate it:

```text
<PYTHON> scripts/validate_architecture_report.py <REPORT.json>
```

Report exact package identity when measured, rubric version, evidence inspected, observations, judgments, decision, alternatives, measured commands/scenarios, and residual risks.

### Evaluator and evidence freeze

For before/after or repeated-review comparisons, treat the rubric version, report validator, scenario suite, target package identity, and any material external source snapshot as evaluator/evidence inputs. Do not edit them after seeing a candidate result and still call the comparison equivalent. If an evaluator must change, version it and start a new comparison.

When external repository/files materially determine a judgment, capture the exact source bytes or immutable revision identity before analysis. Do not mix observations from one source version with a decision based on another without explicit re-baselining.

### Diagnostic repair loop

If inventory/report validation fails, repair the smallest diagnosed contract defect and rerun the same failing gate before adjacent checks. Never weaken the rubric, delete evidence, change frozen scenarios, or lower validation requirements to obtain a pass. After a durable report passes its final validator, treat that report as frozen for the recorded package/evidence identity; later edits require revalidation.

## Architectural invariants

- Preserve a cohesive skill when one domain, activation surface, owner/evidence lifecycle, and progressive-loading model explain it.
- Do not split because of file count, line count, reference count, or stylistic preference.
- Do not merge resources merely because both are short or often adjacent; require overlapping decision ownership or drift evidence.
- Do not create a router unless there are separable destinations and stable dispatch evidence.
- Do not extract a mode unless it has meaningfully distinct activation and at least one independent lifecycle signal such as resources, validators, ownership, release cadence, or user expectation.
- Do not recommend deletion until consumer tracing and retention purpose are checked.
- Prefer integration, relocation, clearer routing, or no change before destructive cleanup when evidence is incomplete.
- Preserve host-specific adapters when useful, but do not make them semantic core dependencies for a portable package.

## Output contract

Every substantive review must include:

1. target, selected mode, package identity status, and rubric version;
2. evidence inspected, commands executed, and missing evidence;
3. mechanical observations: inventory, dependency/resource/ownership/consumer/loading facts;
4. architectural judgments with evidence IDs and confidence;
5. one primary decision from the six-decision enum when a decision is requested;
6. alternatives considered and the tie-breaker used;
7. recommendations with evidence, expected benefit, risk, and validation gate;
8. measured versus unmeasured behavioral evidence;
9. residual risks and next-action handoff when relevant.

Use the stable field definitions in `references/architecture-report-contract.md` for durable or machine-readable output.

## Stop conditions

Stop or return a bounded review when:

- zero or multiple ambiguous target roots exist;
- exact package identity is required but the package bytes cannot be accessed;
- the requested conclusion depends on benchmark/scenario evidence that was not supplied or executed;
- a split, merge, router, extraction, deletion, or domain rewrite lacks the rubric's minimum evidence;
- hidden/external consumers may exist and cannot be inspected for a destructive recommendation;
- package files contain secrets/credentials or blocked paths that should not be opened;
- the only way to reach a preferred architecture is to weaken validation, safety, ownership, or evidence requirements;
- validation fails and the next change would require out-of-scope implementation.
