# Resource Integration

Use for supporting files in `references/`, `scripts/`, `assets/`, `assets/templates/`, `examples/`, and `evals/`.

## Integrated when

- `SKILL.md` links to it with a loading condition.
- A reference links to it in a declared workflow.
- A script reads, writes, validates, or packages it.
- It is an operational template the workflow copies, fills, renders, or validates.
- It is an example/scenario suite referenced by activation, benchmark, hardening, or validation rules.
- It is a runtime asset copied into outputs and documented as asset-only.

## Repair priority

1. Integrate useful resources with precise loading rules.
2. Move misplaced explanatory content from `assets/` to `references/`.
3. Move repeatable output skeletons from prose into `assets/templates/`.
4. Add/improve validators for fragile structures.
5. Delete only placeholders, duplicates, obsolete examples, generated reports, caches, or misleading resources.

## Smells

Generic initializer samples; templates described but not workflow-linked; scenario measured fields filled without evidence; validators present but not mentioned; references duplicating or contradicting `SKILL.md`; scripts with undocumented args or unavailable dependencies.

## Asset vs reference

- `references/`: instructions, policies, rubrics, schemas, decision rules.
- `assets/templates/`: reusable output shapes to copy/fill/render/validate.
- `assets/`: non-reasoning assets such as images, boilerplate, fixtures, static output files.
- `examples/`: human-readable examples or planned scenario records.
- `evals/`: evaluator scenarios/benchmark inputs; modify only when evaluator design is explicit.
