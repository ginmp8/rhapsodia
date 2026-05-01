---
name: skill-token-efficient
description: use when asked to refactor, compress, rewrite, audit, validate, or package a target chatgpt or agent skill so its instructions consume fewer tokens while preserving activation behavior, scope boundaries, workflows, output contracts, validation rules, safety constraints, references, and human readability. especially use for skill.md, frontmatter descriptions, prompt bodies, references, examples, templates, and instruction packages where token economy, context efficiency, semantic deduplication, progressive loading, or concise markdown structure is the primary goal. do not use for ordinary prompt advice, generic code refactoring, benchmark-only scoring, or removing safety/compliance rules to reduce length.
---

# Skill Token Efficient

## Purpose

Refactor target skills for lower token cost without semantic loss. Preserve role, activation, exclusions, mutation authority, workflow, tool rules, safety, validation, packaging, and output contracts while keeping instructions human-readable.

## Inputs

Resolve or infer:

1. `TARGET`: folder, zip, installed skill, or supplied text.
2. Mode: `audit`, `plan`, `apply`, `validate`, `package`.
3. Level: `readable` default, `dense`, `max-safe`.
4. Writable scope: target skill only.
5. Blocked: `.git`, secrets, credentials, fixtures, expected outputs, benchmark baselines, generated evidence, old zips, read-only files, unrelated repos.
6. Goal: reduce `SKILL.md` plus referenced instruction cost while preserving behavior.
7. Gates: lower estimated tokens, equivalent semantic map, valid links, preserved protected regions, touched scripts run, package validates when requested.

Proceed with conservative assumptions unless target identity or writable scope is ambiguous.

## Modes

- `audit`: measure cost, find waste; no edits.
- `plan`: propose safe compression; no edits.
- `apply`: refactor allowed target files.
- `validate`: check refactor; no edits except reports.
- `package`: validate and deliver `skill.zip`.

Broad requests run: inspect -> baseline -> semantic map -> plan -> refactor -> validate -> package.

## Load When Needed

- `references/compression-playbook.md`: tactics, levels, protected regions, anti-patterns.
- `references/semantic-preservation.md`: invariants, equivalence, risk, deletion rules.
- `references/validation-and-reporting.md`: metrics, gates, commands, report contract.
- `scripts/token_refactor_audit.py`: counts, compares, protected-region check.
- `assets/templates/refactor-report.md.template`: durable report.
- `examples/refactor-examples.md`: compact transformations.

## Workflow

1. **Inspect**: read target `SKILL.md`; confirm one root; inventory `agents/`, `references/`, `scripts/`, `assets/templates/`, `examples/`, `evals/`, validators, packages.
2. **Baseline**: run audit:
   ```bash
   python -S /home/oai/skills/skill-token-efficient/scripts/token_refactor_audit.py --target <TARGET> --output <REPORT_DIR>/baseline.json --markdown <REPORT_DIR>/baseline.md
   ```
3. **Map semantics**: capture purpose, owner, triggers/non-triggers, inputs/defaults, modes, workflow order, tool/filesystem rules, blocked paths, safety, validation, packaging, output contract, stop conditions, resource loading.
4. **Pick level**: `readable` for durable docs; `dense` for low-risk refs/examples; `max-safe` only after semantic and readability gates pass. Do not use max-safe for activation descriptions unless requested.
5. **Compress in order**: remove scaffold/filler/duplicates; consolidate rules; use imperative bullets/key-value lines; replace tables with lists unless matrix value is clear; move branch detail from `SKILL.md` to references; shorten examples; compress frontmatter last.
6. **Protect exact regions**: code blocks, inline code, commands, URLs, links, paths, env vars, proper nouns, versions/dates/numbers, schemas, JSON/YAML keys, CLI flags, required output sections.
7. **Patch only broken spans**: if validation fails, fix targeted regions. Do not recompress whole target unless first pass is semantically invalid.
8. **Validate**: re-run audit, compare before/after when available, check semantic map, links, protected regions, touched scripts, target validators, package validation. Reject changes that weaken safety, boundaries, validation, or output contracts.
9. **Report**: separate measured facts, judgment, and assumptions. Include reduction %, changed files, preserved/moved invariants, protected-region status, failed gates, rollback, risks, and package path only for a validated `skill.zip`.

## Compression Rules

- Default style: concise professional English, not comedic caveman-speak.
- Prefer imperative verbs and precise nouns.
- Merge negatives: `Do not edit secrets, fixtures, expected outputs, or .git`.
- Replace filler with constraints: `Limit: 500 chars`.
- Drop pleasantries, hedges, throat-clearing, repeated rationale, obvious advice.
- Define abbreviations once; avoid obscure one-letter labels in durable docs.
- Keep negatives that prevent false activation, unsafe edits, fabricated validation, or scope drift.
- Never save tokens by hiding contradictions or deleting safety/compliance/stop rules.

## Gates

Pass only when:

1. estimated tokens decrease, unless a stated clarity exception applies;
2. activation triggers/exclusions remain visible;
3. safety, authority, validation, package, and stop boundaries remain intact;
4. local references resolve;
5. protected regions are preserved or intentional changes are explained;
6. touched scripts run;
7. package validation passes when requested;
8. report states counts, changes, assumptions, risks, rollback.

## Stop

Stop when target root is ambiguous; semantic preservation cannot be assessed; requested edits touch blocked/unrelated paths; reduction requires removing safety, compliance, stop, validation, or output-contract rules; exact token counts are mandatory but unavailable; validation or packaging fails outside scope.

## Output

Include applicable: mode/target; token before/after/delta/%; files inspected/changed; semantic invariants; level/tactics; protected-region validation; commands/status; blocked paths; rollback; risks/next pass; `skill.zip` link/path only when validated.
