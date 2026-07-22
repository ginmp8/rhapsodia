# Package Validation

Use for structural edits, identity/path changes, golden examples, preservation checks, assurance review, or `skill.zip` delivery.

## Canonical Command

```bash
python <skill-root>/scripts/validate_priority_contract.py --target <skill-root>
python <skill-root>/scripts/validate_all.py --target <skill-root> --json-output <report.json>
```

The ledger runs under an isolated local `PYTHONPATH`, disables bytecode writes, records every gate, and maps executed gate results to the machine-readable assurance claims.

## Gates

The ledger runs in order:

1. `validate_skill_package.py`: required files, frontmatter, templates, scenarios, links, and package hygiene.
2. `validate_activation_scenarios.py`: native activation category and boundary structure; not live model behavior.
3. `validate_governance_scenarios.py`: profile, lifecycle, mode, escalation, and ownership scenario structure.
4. `validate_golden_examples.py`: artifact, path, projection, and contract fixtures; only allowlisted unknown-fact warnings are accepted.
5. `validate_identity_contract.py`: canonical identities, year consistency, package independence, and icon references.
6. `validate_release_contract.py`: current version, historical-contract hash, protected-file hashes, and explicit migrations.
7. `validate_contract_preservation.py`: original files, headings, public script symbols, protected bytes, and authorized migration continuity.
8. `validate_documentation.py`: normalized local Markdown links with root-escape rejection.
9. `validate_assurance_contract.py`: claim schema, evidence labels, validator references, and SDD gate coverage.
10. isolated standard-library tests: `python -S -m unittest discover -s <skill-root>/tests -p 'test_*.py'`.

Do not share, install, or score a release as ready when any applicable gate fails. Structural scenarios remain structural evidence until an independent prompt runner captures and evaluates model outputs.

## Packaging Rules

Run:

```bash
python <skill-root>/scripts/package_skill.py --target <skill-root> --output <output-dir>/skill.zip
```

The package builder reruns the ledger-equivalent gates, excludes `.git`, caches, bytecode, temporary/system files, generated reports/evidence, and nested ZIPs, and fails closed on symlinks, environment or credential files, private-key containers, recognized private-key material, traversal, duplicate entries, or multiple archive roots.

The archive must be named `skill.zip`, contain one top-level `nomia/` directory, use sorted entries, fixed timestamps, and normalized file modes. Two builds from identical source must be byte-identical. A failed gate or archive inspection removes the candidate archive and cannot replace a prior valid package.

## Protected Release Evidence

`tests/original-contract.json` is immutable historical evidence. `tests/current-release-contract.json` locks the selected release, original-contract hash, and current protected-file hashes. `tests/protected-file-migrations.json` is mandatory when historical and current protected hashes differ.

`agents/openai.yaml` remains byte-protected. Validate it before mutation, after mutation, and after archive extraction. Never update the historical contract merely to make a changed protected file pass. The icon remains a required package asset, but its bytes and SHA-256 are not release-protected.

A successful package result includes a release attestation with version, package root, archive SHA-256, size, packaged-file count, protected hashes, original-contract hash, deterministic timestamp, and the explicit statement that live behavioral activation is not measured.

## Readiness Rule

Ready only when:

- every ledger and archive gate passes;
- `skill.zip` contains `nomia/SKILL.md` and no blocked residue;
- the original functional surface and protected release chain validate;
- local documentation links resolve;
- assurance claims are supported or explicitly `planned`;
- scenario categories cover activation, non-activation, ambiguity, edge, regression, and adversarial cases;
- behavioral metrics are claimed only from executed and reviewed prompt results.

## Release Discipline

`VERSION` identifies the package contract version and `CHANGELOG.md` records material behavior, validation, migration, and compatibility changes. `requirements.txt` pins the YAML runtime dependency used by validators. Repository-facing writers, normalizers, adaptation reports, validation reports, the ledger, and package creation use atomic replacement or read-only execution. Interruption tests must show that failed replacement leaves original bytes unchanged and removes temporary files.
