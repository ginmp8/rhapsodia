# Package Delivery

Load only to validate, export, or package MAGIA itself.

## Archive Shape

- Build `skill.zip` from the final MAGIA folder only.
- Zip must contain exactly one top-level directory named after the skill folder.
- Archived root must contain `SKILL.md`, `VERSION`, `CHANGELOG.md`, `agents/`, `references/`, `scripts/`, `assets/`, `examples/`, and `evals/`.
- Exclude `.git`, caches, benchmark reports, test result folders, test-results.json, nested zips, temp outputs, secrets, credentials, private keys, tokens, and local env files.
- Remove stale generated noise when practical. `scripts/package_policy.py` is the single inclusion/exclusion contract: folder validation scans every package-eligible file and the packager archives that same candidate set, so known generated caches may remain after tests without entering or blocking the archive. Unknown or eligible binary/undecodable content still fails closed.

## Standard Commands

```text
python scripts/validate_skill_package.py --target <skill-root>
python scripts/package_skill.py --target <skill-root> --output <output-dir>/skill.zip --validate
python scripts/validate_skill_package.py --target <skill-root> --zip <output-dir>/skill.zip
```

Folder and archive validators must pass before readiness is claimed.

## Gates

1. `SKILL.md` has lowercase frontmatter with only `name` and `description`.
2. Every local reference from `SKILL.md` resolves inside the package.
3. Required resources exist: agent metadata, references, scripts, MAGIA-owned templates, examples, evals.
4. Python scripts compile.
5. Scenario files keep planned fields null unless measured evidence exists.
6. The archive is cache-free, blocked-path-free, symlink-free, scanned for secret-like names and content, and has one top-level skill directory; source validation may ignore only generated paths explicitly excluded by `scripts/package_policy.py`. Oversized, binary, or undecodable members fail closed unless an explicit future allowlist contract defines a safe scanner for that content class.
7. No scaffold markers remain outside templates.

## Evidence to Report

Report package command, validator command, output path, archived file count, size, excluded categories, and residual risk. Never report behavioral scenario metrics as measured unless scenario prompts were executed and evaluator decisions recorded.
