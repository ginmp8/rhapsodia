# Packaging and Validation

Use when a hardening run must produce or verify installable `skill.zip`.

## Contract

A package must contain exactly one skill root with `SKILL.md`; frontmatter limited to lowercase `name` and `description`; all referenced local paths present; no `.git`, caches, temporary evidence, benchmark outputs, secrets, credentials, symlinks, or generated report dirs; no unresolved scaffold markers in non-template text; archive contents rooted under the skill folder name, not loose files. ZIP metadata and entry ordering must be normalized so the same candidate produces the same bytes in the supported environment.

Build to a private temporary archive, validate it, and atomically replace the requested output only after success. Preserve the last-good output on failure. Reject package/receipt outputs that resolve inside the target tree or alias each other. The JSON receipt must retain the existing packaged-candidate/archive identity fields, expose a top-level `target_tree_sha256` compatible with current cross-skill change gates, and additionally record a committed stage, receipt version, last-good preservation semantics, recovery state, validation status, and final path.

## Commands

```text
<PYTHON> scripts/inventory_skill.py --target <TARGET_SKILL_PATH> --output <REPORT_DIR>/inventory.json
<PYTHON> scripts/hardening_audit.py --target <TARGET_SKILL_PATH> --output <REPORT_DIR>/hardening-audit.md --json-output <REPORT_DIR>/hardening-audit.json
<PYTHON> scripts/validate_hardened_skill.py --target <TARGET_SKILL_PATH> --min-score 85
<PYTHON> scripts/package_skill.py --target <TARGET_SKILL_PATH> --output <OUTPUT_DIR>/skill.zip --validate --json-output <REPORT_DIR>/package-receipt.json
<PYTHON> scripts/validate_hardened_skill.py --target <TARGET_SKILL_PATH> --package-output <OUTPUT_DIR>/skill.zip
```

Resolve `<PYTHON>` to an available Python 3.10+ launcher or equivalent host execution method (for example `python`, `python3`, `py -3`, or an absolute interpreter path). Record the exact launcher used. Bundled scripts use only the standard library.

## Exclusions

Package builder must skip `.git/`; `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`; `.DS_Store` and editor swap files; temp dirs such as `tmp/`, `.tmp/`, `reports/`, `test-results/`, `benchmark-reports/`; generated evidence outputs named test-results.json or hardening-audit.json; old `.zip` artifacts; filenames implying secrets, credentials, private keys, tokens, local env data; and symlink paths that could read outside the target tree.

Do not exclude real resources: `references/`, `scripts/`, `assets/`, `examples/`, `agents/`.

## Blocking gates

1. Folder validator passes.
2. Builder creates the requested zip path.
3. Archive validator reads the zip.
4. Archive has exactly one top-level skill directory.
5. Archived `SKILL.md` frontmatter is valid/minimal.
6. Referenced paths resolve inside the archive.
7. No blocked/cache/report/secret/credential/symlink path is included.
8. No residual scaffold marker appears in non-template text.
9. Packaged-candidate, target-tree, and archive SHA-256 values exist in the receipt; the top-level target-tree identity is consumable by current cross-skill change gates.
10. Package and receipt destinations passed output-alias preflight.
11. The output was replaced atomically only after candidate validation, with rollback to the prior output on a failed committed-archive validation.
12. Receipt evidence reports the committed stage and last-good/recovery semantics while retaining existing receipt identity fields.

After the final pass, freeze the candidate. Any later edit requires rerunning affected validation and regenerating the package/receipt. When the package builder itself changes, build twice from the same candidate and confirm identical archive SHA-256 values.

## Report

State package path, size, archived file count, candidate tree SHA-256, archive SHA-256, atomic replacement result, validation outcomes, excluded path categories if present, and residual risks, especially unmeasured behavioral metrics.
