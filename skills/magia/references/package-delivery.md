# Package Delivery

Load only to validate, export, or package MAGIA itself.

## Archive Shape

- Build `skill.zip` from the final MAGIA folder only.
- Zip must contain exactly one top-level directory named after the skill folder.
- Archived root must contain `SKILL.md`, `agents/`, `references/`, `scripts/`, `assets/`, `examples/`, and `evals/`.
- Exclude `.git`, caches, benchmark reports, test result folders, test-results.json, nested zips, temp outputs, secrets, credentials, private keys, tokens, and local env files.
- Clean stale caches/reports/temp outputs/nested archives/blocked paths from the source folder before packaging; do not rely only on zip exclusions.

## Standard Commands

```text
python scripts/validate_skill_package.py --target <skill-root>
python scripts/validate_execution_scenarios.py evals/execution-scenarios.json
python scripts/validate_run_state.py assets/templates/run-state.json.template
python -m pytest -q
python scripts/package_skill.py --target <skill-root> --output <output-dir>/skill.zip --validate
python scripts/validate_skill_package.py --target <skill-root> --zip <output-dir>/skill.zip
```

Folder and archive validators must pass before readiness is claimed.

## Gates

1. `SKILL.md` has lowercase frontmatter with only `name` and `description`.
2. Every local reference from `SKILL.md` resolves inside the package.
3. Required resources exist: agent metadata, references, scripts, MAGIA-owned templates, examples, evals.
4. Python scripts compile.
5. Activation scenarios remain planned unless prompt outputs were captured; the frozen execution suite passes its deterministic schema/category validator.
6. The canonical run-state template passes structural validation, and package tests pass.
7. Source and zip are readable, cache-free, blocked-path-free, secret-path-free, and have one top-level skill directory.
8. No scaffold markers remain outside templates.

## Evidence to Report

Report package command, validator command, output path, archived file count, size, excluded categories, and residual risk. Never report behavioral scenario metrics as measured unless scenario prompts were executed and evaluator decisions recorded.
