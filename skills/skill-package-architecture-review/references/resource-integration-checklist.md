# Resource Integration Checklist

Use this reference for `resource-integration-review` and whenever recommending addition, relocation, merge, or deletion of bundled files.

## Resource categories

- Control-plane resource: required to choose the workflow or enforce boundaries.
- Reference resource: detailed instructions, rubrics, schemas, checklists, or policies loaded on demand.
- Script resource: executable deterministic operation such as inventory, validation, packaging, transformation, or report generation.
- Template asset: output skeleton copied or filled during a declared workflow.
- Runtime asset: binary, boilerplate, data, image, or other artifact used in outputs.
- Example: demonstration of intended use or expected output style.
- Eval: planned or executed scenario set used for activation or behavior validation.
- Generated evidence: reports, logs, inventories, benchmark outputs, or validation artifacts created by runs. These usually should not be bundled unless the package explicitly owns them.

## Integration signals

A resource is integrated when at least one is true:

- `SKILL.md` or a reference states when to load or run it.
- A script imports, reads, writes, validates, or renders it.
- A report template or output contract explicitly uses it.
- It is linked from a mode, workflow, checklist, or stop condition.
- It is intentionally asset-only and a workflow says how it is copied or filled.
- It is part of an eval suite with planned-vs-measured evidence rules.

Do not call a resource orphaned until these checks are complete.

## Orphan review

For each suspicious resource:

1. Search `SKILL.md` for the path, filename, directory role, or concept name.
2. Search references for the path, filename, or declared mode.
3. Search scripts for file reads, imports, writes, templates, glob patterns, and validators.
4. Search templates for required data fields and writer assumptions.
5. Search examples and evals for scenario or output references.
6. Check package validators or manifest-like files.
7. Classify as integrated, weakly integrated, misplaced, obsolete, duplicate, generated debris, or unknown.

## Duplication review

Duplication is harmful only when it creates drift, contradiction, or maintenance burden. Duplicates may be acceptable when they serve different audiences or execution phases.

Check:

- Are two references always loaded together?
- Do two files define the same severity, scoring, mode, or output contract differently?
- Does a template duplicate prose that belongs in a reference?
- Does an example hardcode obsolete behavior that conflicts with current instructions?
- Do multiple validators check the same gate with different thresholds?

## Excess review

A resource is excessive when it adds maintenance cost or context load without improving reliability. Evidence can include unused files, long link indexes, redundant variants, stale generated reports, or support for abandoned modes.

Do not treat size alone as excess. A long rubric can be healthy if it is loaded only for scoring decisions.

## Deletion discipline

Prefer this order:

1. Integrate useful resources through loading rules or workflow references.
2. Move resources to the correct folder when the role is wrong.
3. Merge duplicates when one canonical owner can preserve all useful content.
4. Deprecate or delete only when evidence shows placeholder, stale, misleading, generated, duplicated, or unowned content.

Deletion recommendation must include evidence and validation gate.
