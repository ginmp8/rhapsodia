# Package Validation

Use for structural edits, identity/path changes, golden examples, preservation checks, or `skill.zip` delivery.

## Gates

Run in order:

1. `scripts/validate_skill_package.py --target <skill-root>`: required files, frontmatter, links, templates, harness scenarios, scaffold hygiene, blocked generated/package artifacts.
2. `scripts/validate_activation_scenarios.py <skill-root>/examples/activation-scenarios.json`: native scenario schema, category coverage, activation labels, boundary coverage. This is structural scenario evidence, not live behavioral measurement.
3. `scripts/validate_golden_examples.py --skill-root <skill-root>`: golden examples satisfy artifact, path, and contract validators; warnings are allowed only for intentional unknown or missing facts.
4. `scripts/validate_identity_contract.py --target <skill-root>`: canonical board/spec identities, year/cycle consistency, independence from other skill packages, and retained icon references.
5. `scripts/validate_contract_preservation.py --target <skill-root>`: every original file, Markdown heading, public script symbol, and the exact hashes and bytes of all protected files remain present unless an explicitly recorded symbol replacement applies.
6. `python -S -m unittest discover -s <skill-root>/tests -p 'test_*.py'`: canonical identity, path, ownership, and negative compatibility tests.
7. `scripts/package_skill.py --target <skill-root> --output <output-dir>/skill.zip`: reruns gates 1-6, then writes the archive.

Do not share or install a zip from a failed gate.

## Packaging Rules

`package_skill.py` excludes `.git`, caches, bytecode, temp/system files, generated evidence/report folders, and nested `.zip` files. Package/golden runners set `PYTHONPATH` to local `scripts/` plus interpreter package paths so validators can run under `python -S` without writing bytecode.

The archive must be named exactly `skill.zip` and contain one top-level `nomia/` directory. `assets/icon.svg` and `agents/openai.yaml` are protected byte-for-byte: packaging, identity changes, metadata updates, and formatting tools must not alter, normalize, reserialize, or regenerate either file. Validate SHA-256 for both before and after mutation and again after ZIP extraction.

## Readiness Rule

Ready only when all gates pass, `skill.zip` contains `nomia/SKILL.md`, no non-template scaffold markers remain, links resolve, generated evidence/reports/caches/secrets/credentials/old zips are excluded, the original functional surface and all protected-file hashes and bytes are preserved, harness scenarios cover activation/non-activation/ambiguous/edge/regression/adversarial criteria, and behavioral metrics are claimed only after prompt execution and review.
