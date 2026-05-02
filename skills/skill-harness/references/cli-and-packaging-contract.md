# CLI and Packaging Contract

Use for deterministic skill-harness commands, exits, and packaging.

## Commands

### `scripts/skill_harness_inventory.py`

Creates deterministic structural inventory.

```bash
python /home/oai/skills/skill-harness/scripts/skill_harness_inventory.py --target <TARGET_SKILL_PATH> --output <report-dir>/inventory.json
```

Output: JSON with target path, `SKILL.md` count, frontmatter, top-level dirs, file metadata, referenced/missing paths, unresolved scaffold hits. Nonzero only for Python/read failure. Written JSON is measured inventory evidence.

### `scripts/skill_harness_audit.py`

Scores structural harness readiness.

```bash
python /home/oai/skills/skill-harness/scripts/skill_harness_audit.py --target <TARGET_SKILL_PATH> --output <report-dir>/harness-audit.md --json-output <report-dir>/harness-audit.json
```

Output: Markdown/JSON score, dimensions, gates, findings, verdict. Zero means report produced. High score does not prove behavioral readiness without executed scenarios or validators.

### `scripts/skill_harness_validate.py`

Validates structure, scenario schema, Python syntax, references, scaffold markers.

```bash
python /home/oai/skills/skill-harness/scripts/skill_harness_validate.py --target <TARGET_SKILL_PATH> --output <report-dir>/validation.json
```

Output: JSON verdict, gates, scenario details, inventory summary. Exit zero for `accept`/`accept with risks`, nonzero for `reject`.

### `scripts/skill_harness_package.py`

Validates and writes an installable zip.

```bash
python /home/oai/skills/skill-harness/scripts/skill_harness_package.py --target <TARGET_SKILL_PATH> --output <artifact-dir>/skill.zip --report <report-dir>/package-validation.json
```

Output: JSON with `packaged`, output path, archive entries, exclusions, embedded validation. Exit zero only when zip is written. Use `--strict` when major risks should block packaging.

## Exclusions and Evidence

Package excludes `.git`, `.hg`, `.svn`, caches, `dist`, `build`, nested zips, `.DS_Store`. Do not package reports, scratch dirs, secrets, external evaluator outputs, or benchmark baselines unless the target owns them as durable resources.

Report as measured only commands run in the current run; scenario metrics only with executed prompts plus evaluator decisions; package success only with successful package script and existing zip. Preserve failures as failures.

Package mode order: inventory, audit, edits, re-inventory, re-audit, validator, Python syntax check, package, zip entry inspection.
