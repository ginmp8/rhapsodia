# Skill Benchmark Rubric

Score reusable Agent Skills packages from 0 to 100. Score the semantic portable core; report host adapters separately.

## Dimensions

### 1. Scope and specialization — 15

- 0-3: unclear purpose or unrelated jobs.
- 4-7: recognizable but broad/overlapping.
- 8-11: clear task family with minor ambiguity.
- 12-15: reusable workflow with explicit boundaries/non-goals.
- Evidence: `name`, `description`, purpose/scope/boundaries.

### 2. Trigger description — 15

- 0-3: missing/generic.
- 4-7: topic only; trigger situations unclear.
- 8-11: task plus common use contexts.
- 12-15: task, concrete triggers, artifacts, and exclusions in frontmatter description.
- Do not award points for trigger rules that exist only in the body.

### 3. Execution workflow — 15

- 0-3: no process.
- 4-7: unordered recommendations.
- 8-11: ordered flow with some decisions.
- 12-15: sequential/conditional workflow with inputs, decisions, validation, failure handling, and finalization.

### 4. Output quality — 15

- 0-3: output undefined.
- 4-7: vague guidance.
- 8-11: templates/examples/checklists guide output.
- 12-15: explicit output contract, evidence requirements, and quality/acceptance criteria.

### 5. Supporting resources — 10

- 0-2: required resources missing or obsolete scaffold remains.
- 3-5: resources exist but are weakly organized/integrated.
- 6-8: useful references/scripts/templates/assets support the workflow.
- 9-10: resources are minimal, referenced, conditionally loaded/executed, and validated where appropriate.
- Absence of optional resources is not automatically a defect. Do not reward deleting useful resources to inflate score.
- Vendor adapters such as `agents/openai.yaml` do not add score merely by existing.

### 6. Validation and acceptance criteria — 10

- 0-2: no validation.
- 3-5: informal checklist only.
- 6-8: explicit acceptance criteria/repeatable checks.
- 9-10: deterministic validators, regression scenarios, gates, or identity-bound evidence.

### 7. Context efficiency — 10

- 0-2: `SKILL.md` is a knowledge dump.
- 3-5: useful but repetitive/poorly separated.
- 6-8: compact control plane with branch detail in shallow references.
- 9-10: strong progressive loading with little duplicated context.

### 8. Maintainability and portability — 10

- 0-2: fragile structure or host-private core dependency.
- 3-5: understandable but inconsistent or tightly coupled to one host/runtime.
- 6-8: clean organization, relative refs, clear update/test path, portable core.
- 9-10: host-neutral core, optional adapters, tested self-contained helpers, stable evidence/version evolution path.

## Critical gates and verdict

Blocker gates:

- missing/invalid root `SKILL.md`;
- missing `name`/`description`;
- unclear expected output;
- material contradiction confirmed by semantic review;
- required referenced resource missing;
- unresolved scaffold in operational files;
- core behavior requires a vendor-private API/tool while claiming portable Agent Skills behavior.

Verdict rules:

- `approve`: score >= 85, no blocker fails, and required qualitative gates are resolved.
- `approve with reservations`: score >= 70 with no blocker fail, or high static score with unresolved qualitative/runtime evidence.
- `reject`: score < 70 or any blocker fails.

Static generation may leave semantic contradiction/staleness checks as `review`. Do not auto-pass what static analysis cannot prove.

## Evidence identity rules

For a strict version comparison, all compared arms must share:

- same evaluator identity;
- same scenario suite/evidence contract;
- separately frozen target identities.

If evaluator/scenario identities differ, present standalone results but mark score/metric deltas `not comparable` unless a justified normalization exists.

## Behavioral target thresholds

Recommended mature targets when valid scenario evidence exists:

- activation precision >= 90%;
- activation recall >= 85%;
- output conformance >= 90%;
- robustness >= 75%;
- rework rate <= 10%.

These are guidance, not measured facts until scenario evidence is executed/supplied and validated.
