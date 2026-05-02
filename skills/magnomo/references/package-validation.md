# Package Validation

Use for structural edits, golden examples, or `skill.zip` delivery.

## Gates

Run in order:

1. `scripts/validate_skill_package.py --target <skill-root>`: required files, frontmatter, links, templates, harness scenarios, scaffold hygiene, blocked generated/package artifacts.
2. `scripts/validate_activation_scenarios.py <skill-root>/examples/activation-scenarios.json`: native scenario schema, category coverage, activation labels, boundary coverage. This is not behavioral measurement.
3. `scripts/validate_golden_examples.py --skill-root <skill-root>`: golden examples satisfy validators; warnings are allowed only for intentional unknown/missing facts.
4. `scripts/package_skill.py --target <skill-root> --output <output-dir>/skill.zip`: reruns gates 1-3, then writes the archive.

Do not share or install a zip from a failed gate.

## Packaging Rules

`package_skill.py` excludes `.git`, caches, bytecode, temp/system files, generated evidence/report folders, and nested `.zip` files. Package/golden runners set `PYTHONPATH` to local `scripts/` plus interpreter package paths so validators can run under `python -S`.

## Readiness Rule

Ready only when all gates pass, `skill.zip` has `SKILL.md` at archive root, no non-template scaffold markers remain, links resolve, generated evidence/reports/caches/secrets/credentials/old zips are excluded, harness scenarios cover activation/non-activation/ambiguous/edge/regression/adversarial criteria, and behavioral metrics are claimed only after prompt execution and review.
