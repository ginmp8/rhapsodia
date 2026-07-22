# Assurance And Release

Use this reference for readiness, package, audit, benchmark, release-contract, or SDD-review work. It does not replace the mode-specific governance references.

## Architecture Decision

Keep Nomia unified. Its modes share one activation surface, one board/spec governance ownership model, one canonical path contract, one evidence policy, and one validation lifecycle. Split or route only if a future mode gains a different owner, activation trigger, source of truth, or independent release lifecycle.

`SKILL.md` is the control plane. Mode rules, artifact schemas, contracts, examples, and validation details remain progressively loaded. Scripts perform deterministic writes, validation, projections, metrics, and packaging; they do not choose product or technical facts.

## Assurance Model

The machine-readable assurance source is [assurance-contract.json](assurance-contract.json). Each claim states:

- the capability or boundary being asserted;
- its evidence status: `observed`, `measured`, or `planned`;
- affected SDD critical gates;
- supporting artifacts and validators;
- canonical ledger gates;
- explicit limitations.

Validate it with:

```bash
python scripts/validate_assurance_contract.py --target <skill-root> --json-output <report.json>
```

The complete ledger adds gate outcomes to every assurance claim. A structural scenario pass proves schema and category coverage only. Live activation precision, recall, output conformance, and adversarial robustness remain `planned` until an independent prompt runner captures and evaluates outputs.

## Critical-Gate Evidence

| SDD gate | Nomia evidence |
|---|---|
| G1 evidence integrity | release contract, immutable historical contract, projection provenance, unknown/stale/conflict visibility |
| G2 requirement completeness | schema-v2 validators, mode/profile/lifecycle contracts, scenario and golden-example gates |
| G3 traceability | assurance contract, material-change provenance, typed handoffs, projection source metadata |
| G4 validation adequacy | canonical ledger, specialized validators, golden examples, unit tests, explicit not-measured behavior |
| G5 security/privacy/compliance | fail-closed package hygiene, authority boundaries, governed escalation, no technical-state invention |
| G6 authority/source of truth | Nomia/Mago/Magia ownership contract, canonical paths, externally sourced identities |
| G7 compatibility/migration/rollback | original surface contract, protected-file migration, strict-v2 semantic lint, migration-only legacy adaptation, atomic package replacement |
| G8 interruption/recovery | atomic writers, interruption regression tests, deterministic rerunnable ledger |

## Protected-File Release Contract

`tests/original-contract.json` remains the immutable historical functional-surface contract. It is never rewritten to hide a mismatch.

`tests/current-release-contract.json` locks the current release version, package root, original-contract hash, and current protected-file hashes. `tests/protected-file-migrations.json` is required when a current protected hash differs from the historical contract. Each migration records the old and new hashes, version, date, authority, and rationale.

Validation fails when:

- the original contract changes without updating its recorded hash;
- `VERSION` and the current release contract disagree;
- current protected bytes differ from their release hashes;
- a historical-to-current change lacks exactly one valid migration;
- a migration references an unchanged or unknown protected file.

Run both gates:

```bash
python scripts/validate_release_contract.py --target <skill-root>
python scripts/validate_contract_preservation.py --target <skill-root>
```

## Documentation And Package Evidence

`validate_documentation.py` checks Markdown links relative to each source file, normalizes parent traversal, rejects escape from the skill root, and verifies local targets. Inline code spans are not treated as hyperlinks.

`package_skill.py` runs the same readiness gates, creates deterministic archive metadata, validates the completed archive, and writes package evidence outside the skill folder. The evidence includes gate results, protected hashes, archive SHA-256, file count, size, and release version. Generated reports and evidence are excluded from the archive.

## Validation Order

1. `validate_skill_package.py` — structure, required resources, scenarios, hygiene.
2. Activation and governance scenario validators — structural coverage only.
3. Golden examples — artifact, path, projection, and contract behavior.
4. Identity, strict-v2 contract semantics, release, preservation, documentation, and assurance contracts.
5. Isolated unit tests — state, handoff, adaptation, projection, atomicity, package security, and negative release cases.
6. `validate_all.py` — canonical combined ledger and assurance support map.
7. `package_skill.py` — rerun gates, build, inspect, attest, and hash the archive.

## Change And Rollback Discipline

- Freeze evaluator inputs before optimization. Do not edit scenarios, expected outputs, or benchmark baselines to improve a score.
- Add stronger auxiliary gates separately and identify evaluator changes in the report.
- Apply one bounded hypothesis at a time; record files, expected effect, validation, gate decision, and rollback.
- Reject or revert changes that weaken activation, ownership, unknown preservation, validation, security, packaging, or evidence honesty.
- A failed critical gate overrides aggregate scores and blocks package readiness.
