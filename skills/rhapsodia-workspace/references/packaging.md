# Packaging isolation

Release packaging is data-only. `scripts/package_skill.py` must never execute or import a validator from the tree it packages. It reads externally produced validation evidence bound to the exact tree SHA-256, snapshots packageable bytes, validates the staged archive and replaces the destination atomically only if all checks pass. A stale receipt, unsafe source, path alias, archive failure or changed tree preserves the previous archive.

The repository provides `scripts/validate_and_attest.py` as an explicit trusted execution boundary. Inspect the target before using `--trust-target-code`; this command executes its structural validator, full tests and native/domain contract gates. The packager never calls this runner itself.

```text
<PYTHON> <RHAPSODIA>/scripts/validate_and_attest.py --target <SKILL> --output <OUTSIDE_SKILL>/validation.json --trust-target-code
<PYTHON> <SKILL>/scripts/package_skill.py --target <SKILL> --output <OUTSIDE_SKILL>/skill.zip --validation-evidence <OUTSIDE_SKILL>/validation.json --validate
```

The receipt contains `schema_version: 1.0.0`, `evidence_kind: executed`, exact `target_tree_sha256`, runner SHA-256, and exactly three successful gates: `structure`, `tests`, `contracts`. Each has argv, actual integer zero exit status and output SHA-256. The contracts gate includes the original domain release/ownership/privacy/routing/provenance validations, not just new schema parsing. Individual installed packages can use their own trusted host runner to issue the same documented receipt; no peer package is required.

Unsigned JSON is audit evidence, not authentication. Never accept an untrusted target's self-written receipt as proof. The caller must control the trusted runner and receipt channel. Hash binding detects stale content; it does not establish who authored a receipt. Tests use clearly synthetic receipts only to test rejection/packaging mechanics, never as release proof.

Known caches and generated validation evidence are excluded from the source digest. Included files have sorted paths, fixed archive timestamps and 0644 permissions. Sensitive/unsafe file names, symlinks, hardlinks and case-colliding paths fail closed. The archive and evidence/report paths must be outside the target and must not alias each other. A low-level data-only ZIP helper is not a release validation gate.

The optional `--validate` flag remains accepted for caller migration, but evidence is required with or without it. `--validate-only` inspects an existing archive and never executes target code. Read-only structure validation and executable test proof are separate: moving tests out of a structural validator prevents recursive target execution, while release still requires a passing full test gate.
