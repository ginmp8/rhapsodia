# CLI and Packaging Contract

Use this reference when running deterministic skill-harness commands, interpreting exit codes, or packaging a target skill.

## Script Contracts

### `scripts/skill_harness_inventory.py`

Purpose: create deterministic structural inventory for a target skill folder.

Required command shape:

```bash
python /home/oai/skills/skill-harness/scripts/skill_harness_inventory.py --target <TARGET_SKILL_PATH> --output <report-dir>/inventory.json
```

Expected output: JSON with target path, `SKILL.md` count, frontmatter, top-level directory presence, file metadata, referenced paths, missing references, and unresolved scaffold-marker hits.

Exit semantics: nonzero only when Python execution fails or the target cannot be read. Treat a successful JSON write as measured inventory evidence.

### `scripts/skill_harness_audit.py`

Purpose: score harness readiness from structural evidence.

Required command shape:

```bash
python /home/oai/skills/skill-harness/scripts/skill_harness_audit.py --target <TARGET_SKILL_PATH> --output <report-dir>/harness-audit.md --json-output <report-dir>/harness-audit.json
```

Expected output: Markdown and JSON reports with score, dimension scores, gates, findings, and verdict.

Exit semantics: zero when the audit report is produced. A high score is not enough to claim behavioral readiness unless scenarios or validators were actually executed.

### `scripts/skill_harness_validate.py`

Purpose: validate structural readiness, scenario schema, Python script syntax, missing references, and unresolved scaffold markers.

Required command shape:

```bash
python /home/oai/skills/skill-harness/scripts/skill_harness_validate.py --target <TARGET_SKILL_PATH> --output <report-dir>/validation.json
```

Expected output: JSON report with verdict, gates, scenario details, and inventory summary.

Exit semantics: zero for `accept` or `accept with risks`; nonzero for `reject`.

### `scripts/skill_harness_package.py`

Purpose: validate a skill folder and produce an installable zip archive.

Required command shape:

```bash
python /home/oai/skills/skill-harness/scripts/skill_harness_package.py --target <TARGET_SKILL_PATH> --output <artifact-dir>/skill.zip --report <report-dir>/package-validation.json
```

Expected output: JSON package report with `packaged`, output path, archive entries, excluded dirs, excluded suffixes, and embedded validation result.

Exit semantics: zero only when the zip was written. Use `--strict` when major validation risks should block packaging.

## Packaging Exclusions

Packaging must exclude transient or unsafe content:

- version-control directories such as `.git`, `.hg`, and `.svn`;
- Python and tool caches;
- generated build folders such as `dist` and `build`;
- nested zip archives;
- platform metadata files such as `.DS_Store`.

Do not add reports, scratch directories, secrets, external evaluator outputs, or benchmark baselines to the skill package unless the target skill explicitly owns them as durable resources.

## Evidence Rules

- Report a command as measured only when it was executed in the current run.
- Report scenario metrics as measured only when prompts were executed and evaluator decisions were captured.
- Report package success only when the package script returns success and the zip exists at the stated path.
- Preserve command failures as failures; do not relabel them as passing because a related command succeeded.

## Representative Validation Sequence

For package mode, prefer this order:

1. inventory;
2. static audit;
3. bounded edits;
4. re-inventory;
5. re-audit;
6. validator;
7. Python syntax check for scripts;
8. package command;
9. zip entry inspection.
