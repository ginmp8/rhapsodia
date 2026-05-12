---
name: skill-token-efficient
description: use when asked to audit, refactor, compress, validate, compare, or package target skill instructions for lower token cost while preserving activation, scope, workflow, safety, validation, outputs, evidence/citation traceability, refs, and readability. covers skill.md, descriptions, prompts, refs, examples, templates, and instruction packages. do not use for ordinary writing, generic code refactors, benchmark-only scoring, or deleting safety/validation/evidence/citation rules.
---

# Skill Token Efficient

## Purpose

Reduce skill/instruction tokens without semantic loss. Preserve role, triggers/exclusions, authority, workflow, tool rules, safety, validation, packaging, outputs, readability, and evidence/citation traceability.

## Inputs

Resolve before edits:

1. `TARGET`: folder, zip, installed skill, or supplied text.
2. Mode: `audit`, `plan`, `apply`, `validate`, `package`.
3. Level: `readable` default, `dense`, `max-safe`.
4. Scope: target skill only.
5. Blocked: `.git`, secrets, credentials, fixtures, expected outputs, benchmark baselines, generated evidence, old zips, read-only files, unrelated repos.
6. Goal: lower `SKILL.md` plus referenced-instruction cost without loss.
7. Gates: lower total tokens; no unjustified file/section growth; equivalent semantics; links, evidence/citation rules, protected regions, touched scripts, and package validation pass.

Proceed unless target identity, write scope, or semantic authority is unclear.

## Modes

- `audit`: measure cost/waste; no edits.
- `plan`: propose compression; no edits.
- `apply`: refactor allowed files.
- `validate`: verify refactor; no edits except reports.
- `package`: validate and deliver `skill.zip`.

Broad runs: inspect -> baseline -> semantic map -> plan -> refactor -> validate -> package.

## Load When Needed

- `references/compression-playbook.md`: tactics, levels, protected regions, anti-patterns.
- `references/semantic-preservation.md`: invariants, equivalence, deletion rules, evidence/citation guardrails, risk.
- `references/validation-and-reporting.md`: metrics, gates, commands, report contract.
- `scripts/refactor_audit.py`: count/compare/link/protected/traceability audit.
- `scripts/package_skill.py`: deterministic `skill.zip` creation/validation.
- `assets/templates/refactor-report.md.template`: report skeleton.
- `examples/refactor-examples.md`: compact transformations.
- `evals/activation-scenarios.json`: planned activation, negative, ambiguous, edge, regression, output-contract coverage.

## Workflow

1. **Inspect**: read target `SKILL.md`; confirm one root; inventory support dirs, validators, packages.
2. **Baseline**:
   ```bash
   python -S ./skills/skill-token-efficient/scripts/refactor_audit.py --target <TARGET> --output <REPORT_DIR>/baseline.json --markdown <REPORT_DIR>/baseline.md
   ```
3. **Map semantics**: purpose, owner, triggers/non-triggers, inputs/defaults, modes, order, tool/filesystem rules, blocked paths, safety, validation, packaging, output, stop, resources, and evidence/citation/source/path/line duties as separate invariants.
4. **Choose level**: `readable` for `SKILL.md`/activation; `dense` for low-risk refs/examples; `max-safe` only after semantic/readability gates pass. Do not max-compress activation or evidence/citation rules unless equivalent.
5. **Refactor**: remove filler/duplicates; consolidate rules; use imperative bullets/key-values; keep useful matrices; shorten examples; move branch detail to refs; compress frontmatter last.
6. **Protect exact regions**: code blocks, inline code, commands, URLs, links, paths, env vars, proper nouns, versions/dates/numbers, schemas, JSON/YAML keys, CLI flags, required output sections, and paired terms encoding separate duties such as `evidence/citation`.
7. **Repair narrowly**: on failure, patch only broken spans. Do not recompress all files unless the first pass is semantically invalid.
8. **Validate**: rerun audit; compare total, file, and Markdown-section deltas; check semantics, links, protected regions, evidence/citation traceability, scripts, validators, packaging. Reject unjustified local growth or weakened safety, boundaries, validation, citations/references, or outputs.
9. **Package**: only after gates pass; report counts, reduction, changed files, invariants, protected-region/traceability status, commands, failed gates, rollback, risks, package path.

## Preservation Rules

Use concise professional English. Merge repeated negatives, but keep negatives preventing false activation, unsafe edits, fabricated validation, lost citations/references, or scope drift. Never delete safety, compliance, stop, validation, authority, evidence/citation, or output-contract rules for brevity.

Do not collapse traceability concepts into one generic word. If the source requires `evidence/citation`, `citation`, `source`, `file path`, `line range`, command output, or report reference, preserve the obligation or use an explicitly equivalent phrase.

## Gates

Pass only when total tokens decrease and changed prose files/sections shrink or have an explicit semantic trade-off. Triggers/exclusions stay visible; safety, authority, validation, package, stop, output, and evidence/citation boundaries remain; refs resolve; protected regions and traceability losses are preserved, explained, or reverted; touched scripts and package validation pass; report counts, local regressions, assumptions, risks, rollback.

## Stop Conditions

Stop when target root is ambiguous; semantic preservation cannot be assessed; requested edits touch blocked/unrelated paths; reduction requires removing safety, compliance, stop, validation, evidence/citation, or output-contract rules; exact token counts are mandatory but unavailable; validation or packaging fails outside scope.

## Output Contract

Include: mode/target; total/local token deltas; changed files/sections; invariants; level/tactics; protected-region and evidence/citation validation; commands/status; blocked paths; accepted local trade-offs; rollback; risks; `skill.zip` only when validated.
