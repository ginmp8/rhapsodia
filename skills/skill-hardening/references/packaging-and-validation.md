# Packaging and Validation

Use when a hardening run must produce or verify installable `skill.zip`.

## Contract

A package must contain exactly one skill root with `SKILL.md`; frontmatter limited to lowercase `name` and `description`; all referenced local paths present; no `.git`, caches, temporary evidence, benchmark outputs, secrets, credentials, or generated report dirs; no unresolved scaffold markers in non-template text; archive contents rooted under the skill folder name, not loose files.

## Commands

```text
python3 -S scripts/inventory_skill.py --target <TARGET_SKILL_PATH> --output <REPORT_DIR>/inventory.json
python3 -S scripts/hardening_audit.py --target <TARGET_SKILL_PATH> --output <REPORT_DIR>/hardening-audit.md --json-output <REPORT_DIR>/hardening-audit.json
python3 -S scripts/validate_hardened_skill.py --target <TARGET_SKILL_PATH> --min-score 85
python3 -S scripts/package_skill.py --target <TARGET_SKILL_PATH> --output <OUTPUT_DIR>/skill.zip --validate
python3 -S scripts/validate_hardened_skill.py --target <TARGET_SKILL_PATH> --package-output <OUTPUT_DIR>/skill.zip
```

Use `python3 -S`; scripts use only the standard library.

## Exclusions

Package builder must skip `.git/`; `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`; `.DS_Store` and editor swap files; temp dirs such as `tmp/`, `.tmp/`, `reports/`, `test-results/`, `benchmark-reports/`; evidence outputs named `test-results.json` or `hardening-audit.json`; and filenames implying secrets, credentials, private keys, tokens, or local env data.

Do not exclude real resources: `references/`, `scripts/`, `assets/`, `examples/`, `agents/`.

## Blocking gates

1. Folder validator passes.
2. Builder creates the requested zip path.
3. Archive validator reads the zip.
4. Archive has exactly one top-level skill directory.
5. Archived `SKILL.md` frontmatter is valid/minimal.
6. Referenced paths resolve inside the archive.
7. No blocked/cache/report/secret/credential path is included.
8. No residual scaffold marker appears in non-template text.

## Report

State package path, size, archived file count, validation outcomes, excluded path categories if present, and residual risks, especially unmeasured behavioral metrics.
