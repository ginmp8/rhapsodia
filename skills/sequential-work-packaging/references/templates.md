# canonical templates

Use these templates as the default starting point. Adapt values, but do not change the structural rules unless the user explicitly asks to diverge from the convention.

## 1. `spec-catalog.yaml`

```yaml
schema_version: 1
cycle_version: "01.00.00"
cycle_status: active
specs:
  - order: 10
    spec_id: spec001
    feature_key: example-feature
    title: Example Feature
    type: feature
    classification: feature
    depends_on_features: []
    depends_on_specs: []
    status: planned
    feature_version: v0.1.0
```

## 2. `manifest.yaml`

```yaml
schema_version: 1
spec_id: spec001
feature_key: example-feature
title: Example Feature
type: feature
classification: feature
status: planned
phase: define
cycle_version: "01.00.00"
feature_version: v0.1.0
source_of_truth:
  prd: prd.md
  tasks: tasks.md
  validation: validation.md
  notes: notes.md
traceability: {}
```

## 3. PRD metadata block

Place this yaml block at the top of `prd.md` when a metadata preamble is useful.

```yaml
spec_id: spec001
order: 10
feature_key: example-feature
title: Example Feature
type: feature
classification: feature
status: planned
phase: define
cycle_version: "01.00.00"
feature_version: v0.1.0
depends_on_features: []
depends_on_specs: []
```

## 4. `prd.md` section skeleton

```md
# context

# problem statement

# goals

# non-goals

# current state

# proposed outcome

# functional requirements

# non-functional requirements

# constraints

# risks and trade-offs

# acceptance criteria

# open questions
```

## 5. `tasks.md` task template

```md
- [ ] Task 1: <short title>
  - Task ID: task001
  - Objective: ...
  - Affected boundary: ...
  - Task type: ...
  - Reasoning: low|medium|high|xhigh
  - Why this reasoning is sufficient: ...
  - Specialist Support: none
  - Dependencies: none
  - Validation: ...
  - Expected result: ...
```

## 6. `notes.md` minimum headings

```md
# assumptions

# repository findings

# design decisions

# risks

# trade-offs

# open questions

# specialist rationale

# complementary execution context
```

## 7. `validation.md` minimum headings

```md
# validation strategy

# backward compatibility

# runtime behavior

# integration behavior

# edge cases

# regression coverage

# performance or observability validation

# docs consistency validation

# evidence expected
```

## 8. Final review checklist

Use this at the end of each spec package review:

```md
# final review

- manifest is consistent with the catalog and local files
- prd is complete and does not hide tasks
- validation is concrete and testable
- notes separate assumptions from requirements
- architecture impact is checked when relevant
- dependencies are modeled at the correct level
- ids, casing, status, phase, and versions follow the convention
```


## 9. Hash-guarded operation plan

Use this shape when committing generated candidate files with `scripts/apply_transaction.py`:

```json
{
  "plan_version": 1,
  "mode": "refine",
  "cycle_root": "/absolute/path/to/01.00.00",
  "writes": [
    {
      "path": "specs/spec001/tasks.md",
      "source": "/staging/spec001/tasks.md",
      "expected_before_sha256": "<64-hex-sha256>"
    }
  ],
  "post_validate": {"mode": "refine", "spec_id": "spec001"}
}
```

For a new file, use `"expected_before_sha256": "ABSENT"`. Never omit this precondition.
