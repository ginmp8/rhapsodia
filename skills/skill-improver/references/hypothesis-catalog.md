# Hypothesis Catalog

Use one hypothesis per iteration. Prefer specific hypotheses tied to observed benchmark weaknesses.

## Trigger and activation hypotheses

### H001 - Improve frontmatter trigger specificity

Expected mechanism: a clearer description improves activation precision and recall.

Candidate changes:
- Make the description action-oriented.
- Include concrete task triggers.
- Include target inputs and outputs.
- Include explicit negative boundaries.

Acceptance evidence:
- Better activation prompt score.
- No increase in false positives.

### H002 - Add negative activation boundaries

Expected mechanism: explicit exclusions reduce accidental activation.

Candidate changes:
- Add non-goals to the description when they affect routing.
- Add body-level refusal or delegation rules.

Acceptance evidence:
- Negative prompts no longer activate or are correctly redirected.

## Workflow hypotheses

### H010 - Add deterministic step order

Expected mechanism: a clearer sequential workflow improves output conformance.

Candidate changes:
- Add numbered workflow steps.
- Add decision points for branching modes.
- Add finalization criteria.

Acceptance evidence:
- Output follows required structure more often.

### H011 - Add mode selection matrix

Expected mechanism: explicit mode selection reduces ambiguity in multi-mode skills.

Candidate changes:
- Add a table mapping user intent to mode, inputs, outputs, and validators.

Acceptance evidence:
- Ambiguous prompt handling improves.

## Output hypotheses

### H020 - Add output contract

Expected mechanism: strict required sections reduce incomplete or inconsistent responses.

Candidate changes:
- Add mandatory final response structure.
- Add artifact naming and path rules.
- Add evidence and citation requirements when applicable.

Acceptance evidence:
- Output conformance improves.

### H021 - Add examples

Expected mechanism: examples teach style, granularity, and expected decisions.

Candidate changes:
- Add one positive example.
- Add one negative example.
- Add one ambiguous example.

Acceptance evidence:
- Qualitative conformance and edge-case handling improve.

## Validation hypotheses

### H030 - Add validation checklist

Expected mechanism: explicit gates catch invalid outputs before final answer.

Candidate changes:
- Add a closing checklist.
- Add pass/fail criteria.
- Require script execution when available.

Acceptance evidence:
- Fewer failed gates.

### H031 - Add deterministic validator script

Expected mechanism: fragile manual validation becomes repeatable.

Candidate changes:
- Add a script that checks frontmatter, required files, schema, or report structure.

Acceptance evidence:
- Evaluator confirms validation support.

## Context efficiency hypotheses

### H040 - Move long details to references

Expected mechanism: compact SKILL.md improves context efficiency while preserving capability.

Candidate changes:
- Move detailed rubrics or examples to `references/`.
- Keep SKILL.md as a control plane.

Acceptance evidence:
- Static context-efficiency score improves.

### H041 - Integrate or remove unused resources

Expected mechanism: supporting resources become easier to trust because useful resources are connected to the workflow and truly unused resources are removed.

Diagnosis rule:
- Do not treat a weakly integrated resource as disposable by default. First classify it as an operational template, script input/output, explanatory reference, example, fixture, or unused scaffold.

Candidate changes:
- Integrate useful templates, references, examples, or scripts by adding explicit workflow references, loading conditions, writer/validator coverage, or package checks.
- Preserve `assets/templates/` when the files are repeatable artifact skeletons rendered, copied, or filled by a declared workflow, even if no script reads them directly.
- Move content to `references/` only when it is explanatory guidance rather than a reusable artifact skeleton.
- Delete placeholder files, duplicated resources, obsolete resources, unreferenced assets, or stale examples only after confirming they are not useful target behavior.

Acceptance evidence:
- Supporting-resource, maintainability, or validation score improves without reducing output quality, workflow clarity, or reusable artifact coverage.
- Any removed resource has an explicit removal rationale, and any preserved resource has a stated consumer or validation path.

## Safety and robustness hypotheses

### H050 - Add safety boundaries

Expected mechanism: the skill better handles unsafe, out-of-scope, or unsupported requests.

Candidate changes:
- Add non-goals.
- Add escalation or clarification rules.
- Add unknown-preservation rules.

Acceptance evidence:
- Edge-case prompts improve.

### H051 - Add rollback or failure handling

Expected mechanism: the workflow becomes safer under partial failures.

Candidate changes:
- Add stop conditions.
- Add recovery rules.
- Add explicit no-fabrication rules.

Acceptance evidence:
- Robustness score improves.
