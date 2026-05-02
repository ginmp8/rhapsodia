# Repair Workflow

Use for `apply-repair` and `package` modes.

## Baseline first

Before editing:

```bash
python scripts/inventory_skill.py --target <TARGET_SKILL_PATH> --output <REPORT_DIR>/inventory.json
python scripts/consistency_audit.py --target <TARGET_SKILL_PATH> --json-output <REPORT_DIR>/consistency-audit.json --markdown-output <REPORT_DIR>/consistency-audit.md
```

Freeze baseline evidence. Do not alter evaluator scripts, scenario fixtures, expected outputs, or generated baseline reports in the same repair hypothesis.

## Repair hypothesis

Record for each bounded patch: inconsistency id, hypothesis, target files, allowed mutation scope, blocked paths, expected improvement, validation commands, rollback notes.

## Patch rules

- Keep patches small and reviewable.
- Preserve useful target behavior.
- Keep `SKILL.md` as router; move branch detail to references.
- Add templates only with copy/fill/render/validation rules.
- Add scripts only for deterministic checks or fragile transformations.
- Never rewrite evaluator fixtures, expected outputs, generated benchmark evidence, or secrets.

## Final validation

Rerun the same audit and compare blocker/high counts, broken links, placeholders, unintegrated resources, validator failures, and packaging status. Success requires resolved blockers or explicit out-of-scope blockers and no new high-severity inconsistency.

## Packaging

Package after folder validation passes:

```bash
python scripts/package_target_skill.py --target <TARGET_SKILL_PATH> --output <OUTPUT_DIR>/skill.zip --validate
```

Exclude generated reports, caches, old zips, `.git`, secrets, credentials, and local environment files.
