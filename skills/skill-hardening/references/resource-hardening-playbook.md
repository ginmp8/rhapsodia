# Resource Hardening Playbook

Use this reference when deciding which supporting files a target skill needs.

## Resource decision table

| Need | Best resource | Add when | Do not add when |
|---|---|---|---|
| Detailed rules or domain conventions | markdown files under `references/` | The rule is too long, conditional, or mode-specific for `SKILL.md` | The rule is obvious, generic, or always needed in every run |
| Deterministic checks or transformations | python or shell scripts under `scripts/` | Correctness depends on repeatability, parsing, schemas, filesystem checks, or generated output | The task is pure judgment or requires context unavailable to a script |
| Reusable output shape | template files under `assets/templates/` | The skill repeatedly creates the same artifact structure, whether rendered by a script or filled/copied by the agent | The output must vary freely, has no stable structure, or is explanatory guidance better suited to `references/` |
| Behavioral validation | `evals/`, `examples/`, or `references/scenario-suite.md` | Activation, output conformance, or robustness must be measured | The user only needs a static structural pass |
| UI metadata | `agents/openai.yaml` | The skill will be packaged for ChatGPT | The skill is an internal draft only |

## Hardening map

For each target skill, create a map with these sections:

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
  validation: "template is referenced, copied/filled or script-consumed by the workflow, and script-validated when strict"
scenarios:
  hypothesis: "which behavior needs measured evidence"
  files: []
  validation: "scenario suite is concrete and frozen before measurement"
packaging:
  hypothesis: "what makes the skill uploadable and maintainable"
  files: ["agents/openai.yaml"]
  validation: "package validator passes"
```

## Script quality checklist

A script added during hardening should have:

- clear CLI help;
- deterministic inputs and outputs;
- nonzero exit status on failure;
- no hidden network dependency unless the skill explicitly owns that connector;
- readable error messages;
- representative test evidence;
- no secrets in arguments, logs, fixtures, or generated reports.

## Reference quality checklist

A reference file should:

- have a narrow purpose;
- be linked from `SKILL.md` with a loading condition;
- avoid repeating the same instructions from `SKILL.md`;
- include concrete schemas, examples, criteria, or branch-specific rules;
- avoid becoming a knowledge dump.

## Asset triage before deletion

When an audit or benchmark flags assets or templates as weakly integrated, do not default to deletion. Classify each file first:

1. operational template: a fillable or copyable artifact skeleton used by the workflow;
2. script input/output: a file read or written by deterministic tooling;
3. explanatory reference: guidance that belongs under `references/`;
4. example: a completed sample that belongs under `examples/` when examples are used;
5. unused scaffold: placeholder, duplicate, obsolete, or unreferenced package weight.

Prefer integration before deletion. For useful assets, add workflow references, usage conditions, placeholder rules, writer/validator coverage, or finalization checks. Remove or migrate only files classified as explanatory references, examples, or unused scaffolds.

## Template quality checklist

A template under `assets/templates/` should:

- represent a stable output artifact;
- use clear placeholders that the skill workflow knows how to fill;
- be referenced from the relevant workflow step, reference file, or writer/validator script;
- be consumed either by deterministic tooling or by an explicit agent-fill/copy step;
- avoid dynamic facts masquerading as defaults;
- have a writer or validator when strict structure matters;
- remain in `assets/templates/` when it is a reusable artifact skeleton, even if the agent fills it manually.

## Common package-level improvements

1. Split a long `SKILL.md` into a compact control plane plus references.
2. Add a mode selection matrix for multi-intent skills.
3. Add a deterministic inventory or validator script.
4. Add output templates for repeated reports or artifacts.
5. Add scenario suites for activation and output conformance.
6. Remove placeholder scaffold files.
7. Add stop conditions and rollback guidance.
8. Add packaging validation and size checks.

## Examples as operational calibration

Use `examples/` for concrete, reusable scenario or artifact samples that help agents apply the skill consistently. Add examples when they calibrate activation, negative boundaries, output conformance, edge cases, or package finalization. Do not treat examples as measured evidence unless the scenarios were actually run and the results were recorded.

Examples should be referenced from `SKILL.md` or a relevant reference file. Remove examples that are generic scaffolds, duplicate templates, or completed outputs that no workflow can use.
