# Package Validation

Use for structural edits, identity/path changes, golden examples, preservation checks, or `skill.zip` delivery.

## Canonical Command

Run the full reproducible ledger with one command:

```bash
python <skill-root>/scripts/validate_all.py --target <skill-root> --json-output <report.json>
```

The ledger isolates dependencies under `python -S`, disables bytecode writes, and records every gate result.

## Gates

The ledger runs in order:

1. `scripts/validate_skill_package.py --target <skill-root>`: required files, frontmatter, links, templates, harness scenarios, scaffold hygiene, blocked generated/package artifacts.
2. `scripts/validate_activation_scenarios.py <skill-root>/examples/activation-scenarios.json`: native scenario schema, category coverage, activation labels, boundary coverage. This is structural scenario evidence, not live behavioral measurement.
3. `scripts/validate_governance_scenarios.py <skill-root>/evals/governance-scenarios.json`: profile, lifecycle, mode, escalation, and boundary scenario structure.
4. `scripts/validate_golden_examples.py --skill-root <skill-root>`: golden examples satisfy artifact, path, and contract validators; warnings are allowed only for intentional unknown or missing facts.
5. `scripts/validate_identity_contract.py --target <skill-root>`: canonical board/spec identities, year/cycle consistency, independence from other skill packages, and retained icon references.
6. `scripts/validate_contract_preservation.py --target <skill-root>`: every original file, Markdown heading, public script symbol, and the exact hashes and bytes of all protected files remain present unless an explicitly recorded symbol replacement applies.
7. isolated unit tests through `scripts/validate_all.py`; do not run the raw `python -S -m unittest` form without the ledger environment because third-party YAML loading is intentionally excluded by `-S`. The ledger executes: `python -S -m unittest discover -s <skill-root>/tests -p 'test_*.py'`: canonical identity, path, ownership, and negative compatibility tests.
8. `scripts/package_skill.py --target <skill-root> --output <output-dir>/skill.zip`: reruns gates 1-7, then writes the archive.

Do not share or install a zip from a failed gate.

## Packaging Rules

`package_skill.py` excludes `.git`, caches and bytecode as reproducible ephemeral exclusions, plus temp/system files, generated evidence/report folders, and nested `.zip` files. Package/golden runners set `PYTHONPATH` to local `scripts/` plus interpreter package paths so validators can run under `python -S` without writing bytecode.

Packaging fails closed when the source tree contains a symlink, `.env` variant, known credential file, private-key/container suffix (`.key`, `.pem`, `.p12`, `.pfx`, `.jks`, `.keystore`), or recognized private-key header. The completed archive is reopened and checked for one `nomia/` root, duplicate or traversal entries, symlink metadata, blocked names/suffixes, and private-key material. A failed content or archive gate deletes the candidate ZIP.

The archive must be named exactly `skill.zip` and contain one top-level `nomia/` directory. `assets/icon.svg` and `agents/openai.yaml` are protected byte-for-byte: packaging, identity changes, metadata updates, and formatting tools must not alter, normalize, reserialize, or regenerate either file. Validate SHA-256 for both before and after mutation and again after ZIP extraction.

## Readiness Rule

Ready only when all gates pass, `skill.zip` contains `nomia/SKILL.md`, no non-template scaffold markers remain, links resolve, generated evidence/reports/caches/secrets/credentials/old zips are excluded, the original functional surface and all protected-file hashes and bytes are preserved, harness scenarios cover activation/non-activation/ambiguous/edge/regression/adversarial criteria, and behavioral metrics are claimed only after prompt execution and review.


## Release Discipline

`VERSION` identifies the package contract version, `CHANGELOG.md` records material behavior and compatibility changes, and `requirements.txt` pins the YAML runtime dependency used by validators. Package creation is atomic: a failed archive build cannot replace a previously valid `skill.zip`. Repository-facing writers, normalizers, adaptation reports, validator reports, and the governance adapter use same-directory temporary files and atomic replacement to avoid partial artifacts. Interruption tests must prove that a failed replace leaves the original bytes unchanged and removes temporary files.
