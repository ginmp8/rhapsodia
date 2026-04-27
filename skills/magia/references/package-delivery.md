# Package Delivery

Load this reference only when a run must validate, export, or package the MAGIA skill itself.

## Archive shape

- Build `skill.zip` from the final MAGIA skill folder only.
- The archive must contain exactly one top-level directory named after the skill folder.
- The archived skill root must contain `SKILL.md`, `agents/`, `references/`, `scripts/`, `assets/`, `examples/`, and `evals/` exactly as package resources require.
- Do not include `.git`, caches, benchmark reports, test result folders, `test-results.json`, nested zip files, temporary run outputs, secrets, credentials, private keys, tokens, or local environment files.
- Treat the source folder as part of package readiness: remove stale caches, benchmark outputs, temporary run outputs, nested archives, and other blocked paths from the working skill folder before packaging; do not rely only on archive exclusion rules.

## Standard commands

```text
python scripts/validate_skill_package.py --target <skill-root>
python scripts/package_skill.py --target <skill-root> --output <output-dir>/skill.zip --validate
python scripts/validate_skill_package.py --target <skill-root> --zip <output-dir>/skill.zip
```

Use the local validator before and after packaging. A package is not ready unless both the folder and archive checks pass.

## Package gates

1. `SKILL.md` has minimal lowercase frontmatter with only `name` and `description`.
2. Every local reference from `SKILL.md` resolves inside the package.
3. Required operational resources are present: agent metadata, references, scripts, templates, examples, and eval scenario suite.
4. Python scripts compile.
5. Scenario files keep planned fields null unless measured execution evidence exists.
6. The source folder and zip are readable, have no caches or blocked paths, include no secret-like paths, and the zip has exactly one top-level skill directory.
7. No scaffold markers remain outside templates.

## Evidence to report

Report the exact package command, validator command, output path, archived file count, package size, excluded categories, and any residual risk. Never report behavioral scenario metrics as measured unless the scenario prompts were actually executed and evaluator decisions were recorded.
