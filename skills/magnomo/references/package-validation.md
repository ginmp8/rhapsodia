# Package Validation

Use this reference when validating structural edits to Magnomo, running golden examples, or producing `skill.zip`.

## Validation Layers

Run package readiness in this order:

1. Structural package gate: `scripts/validate_skill_package.py --target <skill-root>`, including harness-compatible scenario coverage under `evals/activation-boundary-scenarios.json`.
2. Activation scenario gate: `scripts/validate_activation_scenarios.py <skill-root>/examples/activation-scenarios.json`.
3. Golden example gate: `scripts/validate_golden_examples.py --skill-root <skill-root>`.
4. Packaging gate: `scripts/package_skill.py --target <skill-root> --output <output-dir>/skill.zip`.

The packaging script runs the first three gates before writing the zip. Do not share or install a generated zip if any gate fails.

## Evidence Semantics

- `validate_skill_package.py` proves required files, frontmatter, references, templates, harness scenario schema, harness category coverage, and scaffold-marker hygiene.
- `validate_activation_scenarios.py` proves native scenario-file schema, category coverage, activation labels, and boundary coverage; it does not prove measured assistant behavior.
- `validate_golden_examples.py` proves bundled examples still satisfy their validators; warnings are allowed only when the example intentionally preserves unknown or missing facts.
- `package_skill.py` proves the package was validated and written as `skill.zip`; it excludes caches, bytecode, temporary files, `.git`, and accidental nested `skill.zip` files.

## Runtime Notes

Some validators require PyYAML for YAML artifact parsing. The package and golden runners set a subprocess `PYTHONPATH` that includes the local `scripts/` directory and the interpreter's package paths, so they can run under `python -S` in isolated environments.

## Final Readiness Rule

A hardened Magnomo package is ready only when:

- all structural, activation, golden, and packaging gates pass;
- `skill.zip` exists with `SKILL.md` at the archive root;
- no scaffold markers remain outside templates;
- no referenced file is missing from `SKILL.md` or required package resources;
- harness-compatible scenarios include explicit acceptance criteria across activation, non-activation, ambiguous, edge, regression, and adversarial cases;
- no output from the run claims behavioral scenario metrics unless prompts were actually executed and reviewed.
