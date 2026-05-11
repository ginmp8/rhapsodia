---
name: skill-package-architecture-review
description: use when asked to review the internal architecture of a chatgpt or agent skill package, including skill.md control-plane design, references, scripts, assets, examples, evals, templates, validators, contracts, boundaries, handoffs, progressive loading, modularization, resource integration, dependency shape, packaging structure, or whether a skill should stay unified, split, merge resources, extract modes, or add a router. use as a package architecture reviewer, not as a generic implementer, hardening executor, benchmark owner, or domain rewriter.
---

# Skill Package Architecture Review

## Purpose

Review the architecture of a reusable skill package as a system of control plane, supporting resources, evidence, ownership boundaries, workflows, validators, and handoffs. Produce architectural findings and recommendations without rewriting the target domain unless the target package itself provides evidence for that change.

This skill complements consistency repair, hardening, harness, improver, and benchmark workflows. Use it to decide whether the package architecture is coherent before recommending tactical repairs, hardening batches, experiments, or benchmark gates.

## Scope boundary

Review package architecture across:

- `SKILL.md` frontmatter, activation description, routing, modes, workflows, stop conditions, and output contract;
- `references/` rubrics, process docs, schemas, checklists, and conditional loading rules;
- `scripts/` deterministic inventory, validation, report generation, packaging, or helper interfaces;
- `assets/`, especially `assets/templates/`, as operational output skeletons rather than reasoning references;
- `examples/` and `evals/` as planned or measured behavior evidence;
- `agents/` metadata only where it conflicts with package purpose or activation expectations;
- local links, resource declarations, loading paths, handoffs, package hygiene, and dependency shape.

Do not implement generic code changes, mutate benchmark fixtures, change the target skill domain without evidence, remove resources only because they look unused, or claim measured behavior without supplied results or executed commands.

## Modes

Select the smallest mode that answers the user request:

| Mode | Use for | Primary output |
|---|---|---|
| `package-map` | map files, roles, dependencies, resource consumers, and package surface | structural inventory and dependency map |
| `progressive-loading-review` | evaluate whether `SKILL.md` works as a compact control plane and routes to references on demand | loading findings and context-efficiency recommendations |
| `resource-integration-review` | detect orphaned, duplicate, excessive, misplaced, or weakly integrated resources | resource findings with evidence before deletion advice |
| `governance-boundary-review` | review ownership, authority, handoffs, escalation, stop conditions, and non-overlap with adjacent skills | boundary findings and handoff recommendations |
| `content-quality-review` | evaluate technical clarity, flow, completeness, actionability, and reference utility | content-quality findings and targeted improvements |
| `repo-structure-review` | review folder layout, naming, package hygiene, validators, and artifact boundaries | structure findings and packaging risks |
| `architecture-recommendation` | decide whether to keep unified, fragment, extract a mode, merge resources, create a router, or leave unchanged | recommendation with decision evidence |
| `review-report` | produce a durable report across selected modes | report using the bundled template |

## Progressive loading map

Read the target `SKILL.md` first. Then load only the relevant reference:

- `references/package-architecture-rubric.md`: scoring, architectural judgment, cohesion versus size, decision rules.
- `references/progressive-loading-patterns.md`: control-plane and conditional loading review.
- `references/resource-integration-checklist.md`: orphan, duplicate, excessive, misplaced, script/template/validator, and deletion checks.
- `references/governance-boundary-checklist.md`: ownership, authority, stop conditions, handoffs, and adjacent-skill boundaries.
- `assets/templates/package-review-report.md.template`: durable review report structure.
- `scripts/inventory_skill_package.py`: optional structural inventory. Treat output as mechanical evidence, not architectural judgment.

## Workflow

1. **Resolve target and mode.** Identify the target folder or extracted zip. If the user does not specify a mode, infer one from the ask; use `review-report` when they ask for a complete architecture review.
2. **Inspect `SKILL.md` first.** Capture activation description, modes, routing rules, resource map, output contract, and stop conditions before judging supporting files.
3. **Build mechanical evidence.** Inventory package files manually or run `scripts/inventory_skill_package.py`. Separate this structural evidence from reviewer judgment.
4. **Trace resource integration.** For each resource, identify how it is loaded, referenced, script-consumed, template-filled, validated, or intentionally retained as asset-only.
5. **Review architecture.** Apply the relevant rubric or checklist. Distinguish package size from low cohesion: a large skill can be healthy when its domain, ownership, activation, and workflows remain coherent.
6. **Choose recommendations.** Recommend fragmentation, extraction, merging, router creation, or no split only when evidence shows low cohesion, ownership conflict, activation ambiguity, duplicated mode logic, validation burden, or maintenance difficulty.
7. **Validate claims.** Any claim about measured quality, benchmark score, scenario performance, validator pass rate, or package readiness must cite supplied evidence or a command executed during the run.
8. **Report.** Use the report template for durable outputs. Include risks, evidence, recommendations, next steps, and limitations.

## Architectural rules

- Separate mechanical findings from architectural judgment.
- Do not recommend fragmentation only because the package is large.
- Do not delete or deprecate a resource until loading rules, mode routing, scripts, templates, validators, examples, and evals have been checked.
- Prefer integration, clearer routing, or resource relocation before deletion when the resource is useful.
- Prefer keeping a cohesive skill unified when one domain, one activation surface, and one owner model explain the package.
- Prefer extracting a mode when it has separate activation triggers, separate evidence, separate owner, or independent validation lifecycle.
- Prefer a router when several coherent subskills need a shared entry point and explicit dispatch rules.
- Prefer a handoff to consistency repair, hardening, harness, improver, or benchmark when the user asks for repairs, maturity upgrades, experiments, or scoring beyond architectural review.
- Never rewrite the target domain without evidence from the target package, user instructions, repository truth, or supplied sources.

## Output contract

For every review, include:

1. Target and selected mode.
2. Evidence inspected: files, commands, reports, and missing evidence.
3. Mechanical findings: inventory, links, references, resource consumers, packaging shape.
4. Architectural findings: cohesion, loading, boundaries, resource integration, content quality, structure.
5. Decision: keep unified, split, extract mode, merge resource, create router, hand off, or no change.
6. Recommendations with evidence, expected benefit, risk, and validation gate.
7. Measured versus judged claims clearly separated.
8. Limitations and next steps.

## Stop conditions

Stop and report a blocker when:

- the target has zero or multiple candidate root `SKILL.md` files and the correct root cannot be identified;
- the request requires editing target files but no mutation scope or owner approval is present;
- the requested conclusion depends on benchmark, harness, or scenario evidence that is not supplied or executed;
- the requested split, deletion, or domain rewrite lacks evidence;
- package files include secrets, credentials, or blocked paths that should not be opened or repackaged;
- validation fails and the next change would require out-of-scope implementation.
