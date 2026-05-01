# Validation and Reporting

## Metrics

Report when available: `estimated_tokens_before`, `estimated_tokens_after`, `token_delta`, `reduction_pct`, `files_changed`, `compression_level`, `semantic_risk`, `protected_region_status`, `local_links_status`, `script_validation_status`, `package_validation_status`.

Counts are estimates unless a declared tokenizer is available.

## Gates

Fail when activation loses triggers/exclusions; stop/safety/validation/package/output rules weaken; links break; protected regions change without explanation; touched scripts fail; expected packaging fails; report cannot explain equivalence.

## Commands

Baseline:

```bash
python -S /home/oai/skills/skill-token-efficient/scripts/token_refactor_audit.py --target <target> --output <report-dir>/baseline.json --markdown <report-dir>/baseline.md
```

Final:

```bash
python -S /home/oai/skills/skill-token-efficient/scripts/token_refactor_audit.py --target <target> --output <report-dir>/final.json --markdown <report-dir>/final.md
```

Compare:

```bash
python -S /home/oai/skills/skill-token-efficient/scripts/token_refactor_audit.py --before <baseline-target> --after <final-target> --output <report-dir>/comparison.json --markdown <report-dir>/comparison.md
```

Syntax check:

```bash
python -S -m py_compile scripts/token_refactor_audit.py
```

## Report Shape

Mode/target; evidence; baseline/final tokens and reduction; changes by file; invariants preserved/moved/changed; protected-region comparison; commands/outcomes; failed gates; rollback; residual risks; next pass.
