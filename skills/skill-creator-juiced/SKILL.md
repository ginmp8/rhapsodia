---
name: skill-creator-juiced
description: use this skill to create, redesign, or substantially upgrade chatgpt or agent skills with a quality-heavy workflow. use when the user asks to build a skill, turn a repeatable workflow into a skill, choose skill architecture, package skill assets, or coordinate specialist quality workflows such as hardening, benchmarking, harnessing, hypothesis discovery, consistency repair, activation review, testing, token efficiency, documentation, security, code discipline, context mapping, or prompt architecture. do not use for ordinary code review, product strategy, document writing, or prompt-only rewrites unless the user asks to create or upgrade a skill package.
---

# Skill Creator Juiced

## Mission

Create high-quality reusable skills from real workflows, not generic advice. Treat each skill as an operational package with a clear activation surface, compact control plane, progressive loading, evidence-backed resources, validation gates, and a package-ready delivery path.

Use this skill as an enhanced creator and orchestrator. It owns net-new skill creation, major redesigns, specialist quality orchestration, hypothesis-discovery routing, and change-gate acceptance for skill packages.

## Scope

Use for skill packages, agent-skill packages, skill architecture decisions, repeatable workflow-to-skill conversion, specialist routing, package validation, and final skill.zip delivery. Do not use for ordinary application-code fixes, product strategy, generic documentation, document artifacts, or prompt-only rewrites unless the requested output is a skill package or a skill-quality pass.

## Required Inputs and Defaults

Resolve or infer before writing files:

1. target skill name, folder, or proposed capability;
2. activation prompts, non-activation prompts, ambiguous cases, and edge cases when available;
3. expected inputs, outputs, language, tone, citation style, and formatting;
4. tools, connectors, repositories, scripts, assets, and validation commands the skill may use;
5. safety boundaries, blocked paths, read-only files, fixtures, expected outputs, secrets, and packaging expectations.

Defaults: proceed with explicit assumptions when missing details do not change scope or safety; mutate only the target skill folder; keep `.git`, secrets, credentials, fixtures, expected outputs, generated evidence, old zips, and unrelated files blocked.

## Mode Selection

| Mode | Use when | Output |
|---|---|---|
| `create` | net-new skill from examples or workflow | package plan or files |
| `redesign` | existing skill needs architecture change | decision and bounded patch plan |
| `quality-upgrade` | hardening, benchmark, validation, cleanup, or token-efficiency ask | specialist pass ledger and evidence |
| `package` | final archive ask | validated `skill.zip` only after gates pass |
| `explain-or-route` | prompt, doc, or product request rather than skill work | clarify or hand off |

## Core Rules

- Preserve the user's target skill purpose, language needs, constraints, examples, and expected outputs.
- Prefer one cohesive capability over many unrelated topics. Size is secondary; cohesion, activation precision, and ownership clarity are primary.
- Keep `SKILL.md` as the control plane. Move detailed rubrics, schemas, long examples, and branch-specific guidance to `references/`.
- Use scripts only for deterministic, fragile, repeatable, or validation-heavy work. Do not add code where concise instructions are enough.
- Use assets only when they are copied, filled, rendered, or otherwise used in outputs. Do not load assets as reasoning context.
- Treat examples and evals as calibration evidence. Never report behavioral metrics unless scenarios were executed or supplied as results.
- Do not fabricate validation, benchmark scores, package readiness, security status, or script pass rates.
- Ask follow-up questions only when missing information blocks a safe skill design. Otherwise proceed with explicit assumptions.
- Before packaging, remove scaffold, placeholders, caches, generated reports, old zips, and unused example files.
- Use `skill-hypothesis-discovery` in redesign or quality-upgrade work when several improvement directions exist, no bounded hypothesis is supplied, or evidence is saturated. Do not use it for routine net-new creation unless the user asks for a post-creation improvement backlog.
- For existing-skill updates or redesigns, use `skill-change-gate` or its checklist before accepting material changes. For net-new skills, use it only as an advisory final gate when there is no before/after candidate evidence.

## Governance and Authority Controls

- Treat tool use, filesystem writes, connector access, specialist handoffs, and packaging as bounded authority governed by the active user request, platform policy, and target package scope.
- Require explicit user approval before expanding writable scope beyond the target skill folder, editing protected files, or weakening validation, safety, evidence, or package gates.
- Fail closed when source truth, validation evidence, specialist review, package checks, or authority boundaries are insufficient for a readiness claim.
- Preserve an audit trail in the final report: assumptions, specialists invoked or classified, commands run, files changed, blocked paths protected, accepted trade-offs, and remaining risks.

## Resource Loading

Load only what the active branch needs:

- `references/creation-workflow.md` for the ordered creation, redesign, validation, and reporting path.
- `references/design-principles.md` for cohesion, mode, router, split, and progressive-loading decisions.
- `references/quality-gates.md` before readiness, validation, packaging, or final delivery claims.
- `references/specialist-orchestration.md` when choosing or sequencing specialist passes, including `skill-hypothesis-discovery` for evidence-backed hypothesis backlogs and `skill-change-gate` for candidate acceptance.
- `references/source-and-license.md` for source, attribution, and update rules when documenting, auditing, packaging, or updating this package's relationship to `skills/skill-creator/`.
- `evals/activation-scenarios.json` for planned activation, non-activation, ambiguous, and edge coverage. Treat it as planned evidence until executed.
- `examples/creation-scenarios.md` for human-readable calibration examples.
- `scripts/juiced_quality_gate.py` for local structural validation.
- `scripts/package_skill.py` for deterministic `skill.zip` packaging after validation passes.
- `assets/templates/skill-delivery-report.md.template` when a durable creation, update, or package evidence report is useful.

## Creation Workflow

Follow the workflow in `references/creation-workflow.md`:

1. Intake and concrete examples.
2. Capability boundary and cohesion decision.
3. Package architecture and progressive loading plan.
4. Draft `SKILL.md`, references, scripts, assets, examples, and evals.
5. Specialist quality passes, including hypothesis discovery when redesign or quality-upgrade work needs a prioritized backlog.
6. Change-gate review for material updates, validation, cleanup, packaging, and final evidence report.

## Specialist Orchestration

Use `references/specialist-orchestration.md` as the routing table. Do not invoke every specialist blindly. Use the smallest specialist pass that improves the package, but run the full juiced path when the user asks for a very high-quality, benchmarked, or hardened skill.

Default path: use the ordered specialist map in `references/specialist-orchestration.md`. For ordinary new skills, start with prompt/architecture/activation review, then docs, code/testing, security, consistency, cleanup, token efficiency, and advisory change gate as applicable. For production-ready, publish-ready, high-risk, redesign, or quality-upgrade work, add harness, benchmark, hypothesis discovery, improver, required change gate, and final hardening in that reference order.

## Design Principles

Load `references/design-principles.md` when deciding skill size, modes, routers, resources, examples, scripts, or activation boundaries.

Key decisions:

- A large skill can be healthy when one domain, one owner model, and one activation surface explain the package.
- A small skill can be unhealthy when it mixes unrelated contexts.
- Use modes when they are variants of one operational role.
- Use a router when the package should classify work and hand off to separate specialist skills.
- Split a mode when it has separate triggers, evidence, owner, validation lifecycle, or failure modes.

## Quality Gates

Before final delivery, apply `references/quality-gates.md`. At minimum, verify:

- frontmatter has `name` and `description`, and the description states when to use the skill and when not to use it;
- activation, non-activation, ambiguous, and edge scenarios exist or are intentionally omitted with rationale;
- `SKILL.md` has scope, required inputs, mode selection, workflow, resource loading rules, stop conditions, and output contract;
- every referenced local file exists;
- every important support file is referenced, script-consumed, template-filled, validated, or intentionally asset-only;
- no placeholder scaffold or unfinished marker remains;
- added or changed scripts were run at least once, or the reason is reported;
- package validation passes before sharing `skill.zip`;
- `skill-hypothesis-discovery` has produced a backlog, been applied by checklist, or been marked not-applicable when redesign or quality-upgrade work has multiple possible improvement directions;
- `skill-change-gate` has passed, been applied by checklist, or been explicitly marked advisory/not-applicable with rationale before final delivery when the work modified an existing skill.

Use `scripts/juiced_quality_gate.py <target-skill-folder>` for a local structural quality pass when filesystem access is available. Use `scripts/package_skill.py --target <target-skill-folder> --output <output-dir>/skill.zip --validate` for deterministic archive creation and validation.

## Output Contract

When creating or updating a skill, final responses include:

1. skill name and target path;
2. what was created or changed;
3. architecture decision: unified skill, modes, router, or split recommendation;
4. specialist passes applied and any passes skipped with rationale;
5. `skill-hypothesis-discovery` status and top backlog items when redesign, quality-upgrade, or measured optimization was requested;
6. accepted and rejected hypotheses when optimization was requested;
7. `skill-change-gate` status for material updates or final advisory review;
8. files created or changed;
9. validation commands and pass/fail/not-run status;
10. package result, including `skill.zip` path only when the archive exists and validation passed;
11. remaining assumptions, risks, and next quality pass.

## Stop Conditions

Stop or narrow the work when:

- the target has zero or multiple candidate root `SKILL.md` files and the correct root is unclear;
- the requested skill would mix unrelated contexts without a router or split strategy;
- required source truth, examples, schemas, policies, or repository evidence are absent and the skill would otherwise invent domain facts;
- requested edits touch secrets, credentials, `.git`, fixtures, expected outputs, generated benchmark baselines, or unrelated files;
- validation or package checks fail and cannot be safely fixed within scope;
- required `skill-change-gate` review reports a blocking regression that cannot be safely repaired within scope;
- the user requests measured benchmark, precision, recall, robustness, or improvement claims without executed or supplied evidence.
