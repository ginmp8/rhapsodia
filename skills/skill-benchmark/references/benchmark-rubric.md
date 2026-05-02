# Skill Benchmark Rubric

Score target skills from 0 to 100.

## Dimensions

### 1. Scope and specialization - 15

- 0-3: unclear purpose, unrelated jobs, or generic assistant behavior.
- 4-7: recognizable but broad, overlapping, or weakly bounded.
- 8-11: clear domain/task family with minor ambiguity.
- 12-15: narrow reusable workflow with clear non-goals and trigger boundaries.
- Evidence: name, description, overview, examples, boundaries, non-goals.

### 2. Trigger description - 15

- 0-3: missing, too short, or generic.
- 4-7: topic only; trigger situations unclear.
- 8-11: common use cases and context.
- 12-15: task, context, concrete triggers, artifacts, exclusions.
- Evidence: frontmatter `description` as primary activation surface. Do not give full credit when trigger guidance appears only in the body.

### 3. Execution workflow - 15

- 0-3: no clear process.
- 4-7: unordered recommendations.
- 8-11: ordered workflow with some decisions.
- 12-15: complete sequential/conditional workflow with inputs, steps, tools, failure handling, finalization.
- Evidence: workflow sections, decision trees, tool rules, sequencing, failure handling.

### 4. Output quality - 15

- 0-3: no defined output.
- 4-7: vague output guidance.
- 8-11: templates or checklists guide output.
- 12-15: strict output contract, examples, evidence requirements, quality criteria.
- Evidence: templates, examples, rubrics, response structure, acceptance criteria.

### 5. Supporting resources - 10

- 0-2: needed resources missing, obsolete scaffold remains, or assets/templates are unreferenced and unexplained.
- 3-5: resources exist but are weakly organized, under-referenced, or role-ambiguous.
- 6-8: useful references, scripts, templates, or assets are present and workflow-referenced.
- 9-10: minimal, scoped resources are loaded, executed, copied, filled, rendered, or validated conditionally.
- Evidence: `references/`, `scripts/`, `assets/`, `assets/templates/`, `agents/`, `SKILL.md` links, script usage, validator coverage.
- Rule: do not reward asset absence over useful integrated assets. Classify assets before recommending removal: operational template, script input/output, explanatory reference, example, obsolete file, or scaffold.

### 6. Validation and acceptance criteria - 10

- 0-2: no validation.
- 3-5: informal checklist only.
- 6-8: explicit acceptance criteria or repeatable review checklist.
- 9-10: deterministic checks, test scenarios, scoring, or integrated scripts.
- Evidence: quality gates, validators, tests, expected metrics, failure criteria.

### 7. Context efficiency - 10

- 0-2: `SKILL.md` is a knowledge dump or includes irrelevant material.
- 3-5: useful but long, repetitive, or poorly separated.
- 6-8: compact `SKILL.md` with details in references.
- 9-10: strong progressive loading, shallow references, no irrelevant content.
- Evidence: `SKILL.md` length, reference structure, duplication, large static data.

### 8. Maintainability - 10

- 0-2: hard to understand, edit, or package.
- 3-5: understandable but inconsistent or fragile.
- 6-8: clean organization and clear update points.
- 9-10: maintainable structure, versionable references, tested scripts, clear evolution path.
- Evidence: naming, layout, script ergonomics, comments, changelog/version notes, lack of placeholders.

## Critical gates and verdict

Critical gates shape the verdict:

- `approve`: score >= 85 and no critical gate fails.
- `approve with reservations`: score >= 70 and no blocker gate fails, or score >= 85 with minor gate failures.
- `reject`: score < 70 or any blocker gate fails.

Blocker gates: missing/invalid `SKILL.md`; missing `name` or `description` frontmatter; unclear expected output; material contradictions; missing required referenced files/scripts.

## Evidence rules

Cite or quote only the minimum necessary evidence. Prefer paraphrase. Do not infer from unavailable files.

## Recommended thresholds

Mature skill target: static score >= 85; activation precision >= 90 percent; activation recall >= 85 percent; output conformance >= 90 percent; robustness >= 75 percent; rework rate <= 10 percent.
