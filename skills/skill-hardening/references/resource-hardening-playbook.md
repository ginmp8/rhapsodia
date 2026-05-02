# Resource Hardening Playbook

Use when deciding which support files a target skill needs.

## Resource choices

- `references/`: long, conditional, domain, or mode-specific rules. Do not add for obvious/generic rules or always-needed control-plane text.
- `scripts/`: deterministic checks or transformations needing repeatability, parsing, schemas, filesystem checks, or generated output. Do not add for pure judgment or missing context.
- `assets/templates/`: reusable output skeletons that the agent or scripts fill/copy. Do not add for free-form or explanatory guidance.
- `evals/`, `examples/`, `references/scenario-suite.md`: behavioral validation for activation, output conformance, robustness. Do not add for static-only structural passes.
- `agents/openai.yaml`: package UI metadata for ChatGPT. Skip for internal drafts.

## Hardening map shape

```yaml
control_plane:
  hypothesis: "why SKILL.md needs to change"
  files: ["SKILL.md"]
  validation: "frontmatter and workflow review"
references:
  hypothesis: "what detailed rules should move out of SKILL.md"
  files: []
  validation: "all referenced files exist and are conditionally loaded"
scripts:
  hypothesis: "what repetitive or fragile work should be deterministic"
  files: []
  validation: "script ran successfully on representative input"
templates_assets:
  hypothesis: "what outputs need reusable structure"
  files: []
  validation: "template is referenced, copied/filled or script-consumed, and script-validated when strict"
scenarios:
  hypothesis: "which behavior needs measured evidence"
  files: []
  validation: "scenario suite is concrete and frozen before measurement"
packaging:
  hypothesis: "what makes the skill uploadable and maintainable"
  files: ["agents/openai.yaml"]
  validation: "package validator passes"
```

## Script quality

Added scripts need CLI help, deterministic inputs/outputs, nonzero failure exit, no hidden network dependency unless owned, readable errors, representative test evidence, and no secrets in args/logs/fixtures/reports.

## Reference quality

Each reference needs a narrow purpose, `SKILL.md` loading condition, little duplication, concrete schemas/examples/criteria/branch rules, and no knowledge-dump drift.

## Asset triage before deletion

Classify first: operational template; script input/output; explanatory reference; example; unused scaffold. Prefer integration before deletion. For useful assets, add workflow references, usage conditions, placeholder rules, writer/validator coverage, or finalization checks. Remove or migrate only explanatory references, examples, or unused scaffolds with evidence.

## Template quality

A template should represent a stable artifact, use workflow-fillable placeholders, be referenced by workflow/reference/script, be consumed by tooling or explicit agent fill/copy step, avoid dynamic facts as defaults, have writer/validator coverage when strict, and remain under `assets/templates/` when reusable even if manually filled.

## Common improvements

1. Split long `SKILL.md` into router plus references.
2. Add mode matrix.
3. Add deterministic inventory/validator script.
4. Add report/artifact templates.
5. Add activation/output scenario suites.
6. Remove placeholder scaffold.
7. Add stop and rollback rules.
8. Add packaging validation and size checks.

## Examples

Use `examples/` for concrete reusable scenario/artifact samples that calibrate activation, negative boundaries, output conformance, edge cases, or finalization. Reference examples from `SKILL.md` or a relevant reference. They are not measured evidence unless executed and recorded. Remove generic scaffolds, duplicate templates, or completed outputs no workflow uses.
