# Validation and Reporting

## Metrics

Report available: `estimated_tokens_before`, `estimated_tokens_after`, `token_delta`, `reduction_pct`, `per_file_token_deltas`, `per_section_token_deltas`, `local_token_regressions`, `files_changed`, `compression_level`, `semantic_risk`, `protected_region_status`, `traceability_term_status`, `local_links_status`, `script_validation_status`, `package_validation_status`. Counts are estimates unless a tokenizer is declared.

## Gates

Fail when activation loses triggers/exclusions; stop/safety/validation/package/output rules weaken; evidence/citation/reference/source/path/line duties are removed, collapsed, or unverified; links break; protected regions change without explanation; touched scripts or packaging fail; equivalence is unexplained; or changed prose grows without semantic-gain trade-off.

Traceability gate: if before text contains `citation`, `reference`, `source`, `path`, `line`, or `evidence/citation`, final text must retain an equivalent verifiable-reference duty or mark the change intentional and authorized.

## Commands

Baseline:

```bash
python -S .github/skills/skill-token-efficient/scripts/refactor_audit.py --target <target> --output <report-dir>/baseline.json --markdown <report-dir>/baseline.md
```

Final:

```bash
python -S .github/skills/skill-token-efficient/scripts/refactor_audit.py --target <target> --output <report-dir>/final.json --markdown <report-dir>/final.md
```

Compare:

```bash
python -S .github/skills/skill-token-efficient/scripts/refactor_audit.py --before <baseline-target> --after <final-target> --output <report-dir>/comparison.json --markdown <report-dir>/comparison.md
```

Syntax/package:

```bash
python -S -m py_compile scripts/refactor_audit.py scripts/package_skill.py
python -S scripts/package_skill.py --target <target> --output <artifact-dir>/skill.zip --validate
```

## Report Shape

Mode/target; evidence and citations/references used; baseline/final tokens/reduction; per-file and per-section deltas; local regressions and accepted trade-offs; changes by file; invariants preserved/moved/changed; protected-region comparison; traceability-term comparison; commands/outcomes; failed gates; rollback; residual risks; next pass.
