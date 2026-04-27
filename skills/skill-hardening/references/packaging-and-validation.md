# Packaging and Validation

Use this reference when the hardening run must produce or verify an installable `skill.zip`.

## Packaging contract

A packaged skill must contain exactly one skill root with:

- `SKILL.md` at the root;
- frontmatter with only `name` and `description`;
- lowercase `name` and lowercase `description` values;
- all referenced local paths present inside the package;
- no `.git`, caches, temporary evidence folders, benchmark outputs, secrets, credentials, or generated report directories;
- no unresolved scaffold markers in non-template text files;
- package contents rooted under the skill folder name, not loose files at archive root.

## Recommended command sequence

```text
python3 -S scripts/inventory_skill.py --target <TARGET_SKILL_PATH> --output <REPORT_DIR>/inventory.json
python3 -S scripts/hardening_audit.py --target <TARGET_SKILL_PATH> --output <REPORT_DIR>/hardening-audit.md --json-output <REPORT_DIR>/hardening-audit.json
python3 -S scripts/validate_hardened_skill.py --target <TARGET_SKILL_PATH> --min-score 85
python3 -S scripts/package_skill.py --target <TARGET_SKILL_PATH> --output <OUTPUT_DIR>/skill.zip --validate
python3 -S scripts/validate_hardened_skill.py --target <TARGET_SKILL_PATH> --package-output <OUTPUT_DIR>/skill.zip
```

Use `python3 -S` in environments where site initialization is slow or unavailable. The scripts use only the Python standard library.

## Exclusion policy

The package builder must skip:

- `.git/`;
- `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`;
- `.DS_Store` and editor swap files;
- temporary output directories such as `tmp/`, `.tmp/`, `reports/`, `test-results/`, `benchmark-reports/`;
- generated evidence files named test-results.json or hardening-audit.json when they are evidence outputs rather than package resources;
- files whose names imply secrets, credentials, private keys, tokens, or local environment data.

Do not exclude real operational resources such as `references/`, `scripts/`, `assets/`, `examples/`, or `agents/`.

## Validation gates

Treat these gates as blocking for package delivery:

1. The folder validator passes.
2. The package builder creates the exact requested zip path.
3. The package validator can read the archive.
4. The archive contains exactly one top-level skill directory.
5. The archived `SKILL.md` frontmatter is valid and minimal.
6. Referenced local paths resolve inside the archive.
7. No blocked, cache, report, secret, or credential path is included.
8. No residual scaffold marker appears in non-template text resources.

## Evidence to report

When packaging is requested, report:

- exact package path;
- package size;
- number of archived files;
- validation command outcomes;
- excluded path categories, if any were present;
- residual risks, especially unmeasured behavioral scenario metrics.
