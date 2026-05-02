# Package Validation

Use when validating structural edits, running golden examples, or producing `skill.zip`.

## Validation Layers

Run in order:

1. Structural: `scripts/validate_skill_package.py --target <skill-root>`; includes harness scenario coverage in `evals/activation-boundary-scenarios.json`.
2. Activation: `scripts/validate_activation_scenarios.py <skill-root>/examples/activation-scenarios.json`.
3. Golden: `scripts/validate_golden_examples.py --skill-root <skill-root>`.
4. Packaging: `scripts/package_skill.py --target <skill-root> --output <output-dir>/skill.zip`.

`package_skill.py` reruns the first three gates before writing the zip. Do not share or install a zip from a failed gate.

## Evidence Semantics

- `validate_skill_package.py`: required files, frontmatter, references, templates, harness scenario schema/category coverage, scaffold-marker hygiene.
- `validate_activation_scenarios.py`: native scenario schema, category coverage, activation labels, boundary coverage; not measured assistant behavior.
- `validate_golden_examples.py`: examples satisfy validators; warnings allowed only for intentionally unknown/missing facts.
- `package_skill.py`: validated `skill.zip` written; excludes caches, bytecode, temp files, `.git`, and nested `skill.zip` files.

## Runtime Notes

Some validators need PyYAML. Package and golden runners set subprocess `PYTHONPATH` to local `scripts/` plus interpreter package paths, so they can run under `python -S` in isolated environments.

## Final Readiness Rule

Ready only when all structural, activation, golden, and packaging gates pass; `skill.zip` has `SKILL.md` at archive root; no scaffold markers remain outside templates; referenced files exist; harness scenarios include acceptance criteria across activation, non-activation, ambiguous, edge, regression, and adversarial cases; no behavioral metrics are claimed unless prompts were executed and reviewed.
