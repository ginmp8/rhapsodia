# Package Validation

Use for structural edits, identity/path changes, golden examples, preservation checks, or `skill.zip` delivery.

## Gates

Run these commands in an isolated, unprivileged environment with no repository or deployment secrets:

1. `scripts/validate_skill_package.py --target <skill-root>`: required files, frontmatter, links, templates, harness scenarios, scaffold hygiene, symlinks, and blocked generated/package artifacts.
2. `scripts/validate_activation_scenarios.py <skill-root>/examples/activation-scenarios.json`: native scenario schema, category coverage, activation labels, and boundary coverage. This is structural scenario evidence, not live behavioral measurement.
3. `scripts/validate_golden_examples.py --skill-root <skill-root>`: golden examples satisfy artifact, path, and contract validators; warnings are allowed only for intentional unknown or missing facts.
4. `scripts/validate_identity_contract.py --target <skill-root>`: canonical board/spec identities, semantic calendar dates, year/cycle consistency, independence from other skill packages, and retained icon references.
5. `scripts/validate_contract_preservation.py --target <skill-root>`: every original file, Markdown heading, public script symbol, and the exact hashes and bytes of all protected files remain present unless an explicitly recorded replacement applies.
6. `python -S -m unittest discover -s <skill-root>/tests -p 'test_*.py'`: canonical identity, path, packaging authority, ownership, and negative compatibility tests.
7. From a trusted protected copy of `scripts/package_skill.py`, run `--print-tree-digest --target <skill-root>` and create external JSON evidence containing that digest plus the exact result of gates 1-6.
8. Run `scripts/package_skill.py --target <skill-root> --validation-evidence <evidence.json> --output <output-dir>/skill.zip` from the same trusted protected source. The packager validates the evidence/digest and writes the archive without importing, invoking, or executing validator code from `<skill-root>`.

Do not share or install a zip from a failed gate, stale digest, missing evidence, or target-tree symlink.

## External Evidence Schema

The evidence file stays outside `<skill-root>` and uses:

```json
{
  "schema_version": 1,
  "target_tree_sha256": "<digest printed by the trusted packager>",
  "gates": [
    {
      "name": "package-structure",
      "command": ["python", "..."],
      "returncode": 0,
      "stdout": "exact captured output",
      "stderr": "exact captured output"
    }
  ]
}
```

Include exactly one passing entry for each required gate: `package-structure`, `activation-scenarios`, `golden-examples`, `identity-contract`, `contract-preservation`, and `unit-tests`. The digest binds the evidence to the exact bytes that will be archived; any mutation after validation invalidates the evidence.

## Packaging Authority Boundary

Packaging an untrusted pull request is an authority-boundary operation. CI must obtain `package_skill.py` from a protected base revision, immutable tool image, or equivalent trusted location. Do not execute the target branch's packager or validators in a privileged job. The trusted packager consumes evidence produced by an isolated runner and does not execute code from the target tree.

The package-local script is suitable for local release work only when its own revision is already trusted. No script contained in an untrusted change can establish its own trustworthiness.

## Packaging Rules

`package_skill.py` excludes `.git`, caches, bytecode, temp/system files, generated evidence/report folders, and nested `.zip` files. It rejects every symbolic link rather than following or archiving link targets.

The archive must be named exactly `skill.zip` and contain one top-level `nomia/` directory. `assets/icon.svg` and `agents/openai.yaml` are protected byte-for-byte. Validate SHA-256 for both before mutation, before packaging, and after ZIP extraction.

## Readiness Rule

Ready only when all gates pass in the isolated runner, external evidence matches the exact target-tree digest, `skill.zip` contains `nomia/SKILL.md`, no non-template scaffold markers remain, links resolve, symlinks and generated evidence/reports/caches/secrets/credentials/old zips are excluded, the original functional surface and all protected-file hashes and bytes are preserved, harness scenarios cover activation/non-activation/ambiguous/edge/regression/adversarial criteria, and behavioral metrics are claimed only after prompt execution and review.
