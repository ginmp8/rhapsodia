# Skill Behavior Constraint Coverage

Task success does not prove that the benchmark exercised the skill's material instructions. Use optional constraint-coverage evidence when the question includes semantic breadth, regression safety, or whether the suite actually tests the skill.

Use `scripts/validate_skill_coverage.py` with schema v1 evidence. Each constraint identifies a stable `id`, source span/reference, applicability condition, and expected observable behavior. Each result is exactly one of:

- `not_applicable`;
- `uncovered`;
- `covered_pass`;
- `covered_fail`.

Report two distinct metrics:

- **coverage** = covered applicable constraints / all applicable constraints;
- **covered adherence** = `covered_pass` / all covered constraints.

Do not combine them: high adherence with low coverage means most rules were never exercised. Constraint extraction remains semantic judgment and must be traceable to the frozen skill identity; the validator proves accounting/math, not extraction completeness.
