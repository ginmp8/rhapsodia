# Skill Improvement Playbook

Use this reference to decide what to change in a target skill after the harness map identifies weaknesses.

## Improvement Areas

### Control Plane

Improve `SKILL.md` when the target has weak activation, unclear scope, missing inputs, missing modes, weak stop conditions, or vague outputs.

Add or refine:

- Specific frontmatter description with triggers and exclusions.
- Required inputs.
- Mode selection matrix.
- Step-by-step workflow.
- Stop conditions.
- Output contracts.
- Finalization checklist.

Keep `SKILL.md` compact. Move detailed rubrics into references.

### References

Add or split `references/` when the target needs detailed rules that are only conditionally relevant.

Good references include:

- Domain rules.
- Evaluation rubrics.
- Scenario schemas.
- Source policies.
- Troubleshooting guides.
- Examples that are too long for `SKILL.md`.

Every reference must be linked from `SKILL.md` with a condition for loading it.

### Scripts

Add scripts when consistency matters more than model judgment.

Good script candidates:

- Inventory and structure checks.
- Schema validation.
- Report generation.
- Template rendering.
- Deterministic transformations.
- Packaging readiness checks.

Scripts must have a clear CLI, deterministic output, helpful errors, and at least one representative test run.

### Templates and Assets

Add or preserve templates when the target produces recurring artifacts such as plans, reports, scenario suites, scorecards, or decision records. A template under `assets/templates/` is valid when it is used by a declared workflow, copied or filled by the agent, rendered by a script, or checked by a validator. It does not need to be read by a script to earn its place.

Templates should include placeholders that are obvious and bounded, but the final delivered target should not contain unresolved TODO scaffolding.

When a benchmark or audit marks supporting resources as weak, do not default to removal. Classify the resource as an operational template, script input/output, explanatory reference, example, scenario, or unused scaffold. Integrate useful resources through `SKILL.md`, references, validators, or explicit workflow instructions. Remove or migrate only placeholders, duplicates, obsolete files, or purely explanatory content better suited to `references/`.

### Scenarios

Add scenario suites when activation or behavior quality matters.

Scenario types:

- `should_activate`
- `should_not_activate`
- `ambiguous`
- `edge_case`
- `regression`
- `adversarial`

Do not mark scenario metrics as measured unless executed.

## Bounded Patch Rules

- Patch one coherent improvement batch at a time.
- Protect evaluator fixtures and expected outputs.
- Preserve target-specific useful behavior.
- Avoid generic resources that do not connect to the workflow.
- Avoid rewriting the entire target unless it is unsalvageable.
- Record changed files and validation commands.

## Common Weakness Patterns

| Weakness | Likely fix |
|---|---|
| Generic description | Rewrite frontmatter with concrete triggers and negative boundaries. |
| Long `SKILL.md` | Move detailed branches to references and link conditionally. |
| No output contract | Add mode-specific output contracts. |
| No validation | Add gates, final checklist, and deterministic validator scripts. |
| No scenarios | Add planned scenario suite and runner/checklist. |
| Placeholder files | Delete or replace scaffolding. |
| Useful asset exists but is weakly integrated | Reference it from the workflow, add copy/fill rules, or validate its path before considering removal. |
| Asset is purely explanatory prose | Move the content to `references/` and remove the asset only after references are updated. |
| Claims without evidence | Add evidence policy and require citations or measured outputs. |
| Saturated benchmark | Keep as gate and add auxiliary metric. |
