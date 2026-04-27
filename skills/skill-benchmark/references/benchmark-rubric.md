# Skill Benchmark Rubric

Use this rubric to score a target skill from 0 to 100.

## Score dimensions

### 1. Scope and specialization - 15 points

- 0-3: unclear purpose, multiple unrelated jobs, or mostly generic assistant behavior.
- 4-7: recognizable purpose but broad, overlapping, or weakly bounded.
- 8-11: clear domain and task family with minor ambiguity.
- 12-15: narrow, opinionated, reusable workflow with clear non-goals and trigger boundaries.

Evidence to inspect: skill name, description, overview, examples, explicit boundaries, non-goals.

### 2. Trigger description - 15 points

- 0-3: missing, too short, or generic.
- 4-7: describes topic but not trigger situations.
- 8-11: includes common use cases and context.
- 12-15: includes task, context, concrete triggers, expected artifacts, and exclusion boundaries.

Evidence to inspect: frontmatter `description`. The description is the primary activation surface. Do not give full credit if trigger guidance only appears in the body.

### 3. Execution workflow - 15 points

- 0-3: no clear process.
- 4-7: loose recommendations without step order.
- 8-11: clear workflow with some decision points.
- 12-15: complete sequential or conditional workflow with inputs, steps, tool use, failure handling, and finalization rules.

Evidence to inspect: workflow sections, decision trees, tool instructions, sequencing, failure handling.

### 4. Output quality - 15 points

- 0-3: no defined output.
- 4-7: output guidance is present but vague.
- 8-11: templates or checklists guide final output.
- 12-15: strict output contract, examples, evidence requirements, and quality criteria are present.

Evidence to inspect: templates, examples, rubrics, response structure, acceptance criteria.

### 5. Supporting resources - 10 points

- 0-2: missing resources where they are clearly needed, obsolete scaffold files remain, or assets/templates are unreferenced and unexplained.
- 3-5: resources exist but are weakly organized, under-referenced, or their operational role is unclear.
- 6-8: useful references, scripts, templates, or assets are present and referenced by the workflow.
- 9-10: resources are minimal, well-scoped, directly useful, and loaded, executed, copied, filled, rendered, or validated conditionally.

Evidence to inspect: `references/`, `scripts/`, `assets/`, `assets/templates/`, `agents/`, links from `SKILL.md`, script usage, and validator coverage. Do not reward asset absence over useful integrated assets. When assets exist, classify them before recommending removal: operational template, script input or output, explanatory reference, example, obsolete file, or scaffold.

### 6. Validation and acceptance criteria - 10 points

- 0-2: no validation.
- 3-5: informal checklist only.
- 6-8: explicit acceptance criteria or repeatable review checklist.
- 9-10: deterministic checks, test scenarios, scoring, or scripts exist and are integrated into the workflow.

Evidence to inspect: quality gates, validators, tests, expected metrics, failure criteria.

### 7. Context efficiency - 10 points

- 0-2: `SKILL.md` is a knowledge dump or contains large irrelevant material.
- 3-5: useful but long, repetitive, or poorly separated.
- 6-8: compact `SKILL.md` with references for details.
- 9-10: strong progressive loading design, shallow references, and no irrelevant content.

Evidence to inspect: `SKILL.md` length, reference structure, duplication, large static data.

### 8. Maintainability - 10 points

- 0-2: hard to understand, edit, or package.
- 3-5: understandable but inconsistent or fragile.
- 6-8: clean file organization and clear update points.
- 9-10: maintainable structure, versionable references, tested scripts, and clear evolution path.

Evidence to inspect: naming, folder layout, script ergonomics, comments, changelog or version notes, lack of placeholders.

## Critical gate handling

Critical gates do not directly replace the score, but they affect the final verdict:

- `approve`: score >= 85 and no critical gates fail.
- `approve with reservations`: score >= 70 and no blocker gate fails, or score >= 85 with minor gate failures.
- `reject`: score < 70 or any blocker gate fails.

Blocker gates:

1. Missing or invalid `SKILL.md`.
2. Missing `name` or `description` frontmatter.
3. Expected output is unclear.
4. Instructions are materially contradictory.
5. Required referenced files or scripts are missing.

## Evidence rules

For each score, cite or quote only the minimum necessary evidence from the skill. Prefer paraphrase. Do not infer content from unavailable files.

## Recommended thresholds

A mature skill should target:

- Static benchmark score >= 85.
- Activation precision >= 90 percent.
- Activation recall >= 85 percent.
- Output conformance >= 90 percent.
- Robustness >= 75 percent.
- Rework rate <= 10 percent.
