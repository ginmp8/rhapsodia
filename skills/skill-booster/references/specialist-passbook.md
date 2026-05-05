# Specialist Passbook

Every complete Skill Booster run must execute, apply by checklist, or classify each pass below. Status values: `pass`, `fail`, `blocked`, `not-run`, `not-applicable`, `applied-by-checklist`, `planned`. Also record `execution_type`: `invoked-skill`, `deterministic-script`, `checklist-only`, `blocked`, `unavailable`, `not-applicable`, or `not-run`.

## Ordered pass ledger

| # | Pass | Purpose | Minimum evidence/checklist |
|---:|---|---|---|
| 1 | `skill-creator-juiced` | design governance and escalation | decide optimization vs redesign/router/split; preserve purpose; require package gates; no fabricated readiness |
| 2 | `skill-benchmark` | initial maturity score/report | structural vs behavioral evidence separated; no precision/recall without results; saturated score gets auxiliary metric |
| 3 | `skill-harness` | repeatable scenarios and gates | activation, non-activation, ambiguous, edge, regression, output-contract coverage; run `scripts/run_activation_harness.py` for schema/coverage when compatible; freeze suite; planned vs executed marked |
| 4 | `skill-hypothesis-discovery` | evidence-based improvement backlog | derive 5-10 candidate hypotheses from benchmark, harness, audit, architecture, validation, security, consistency, and token evidence; dedupe; rank; recommend top 1-3 for the current cycle; mark no-mutation when warranted |
| 5 | `skill-improver` | objective, freeze, bounded experiments, decisions | use selected hypothesis or supplied backlog; baseline before mutation; one bounded hypothesis per patch; accept/reject with gates; proposals marked untested |
| 6 | `skill-change-gate` | candidate acceptance gate | classify candidate regressions as blocking, material, trade-off, or follow-up; reject or repair before accept when blocking regressions exist |
| 7 | `skill-package-architecture-review` | package structure decision | unified/modes/router/split/stop decision; `SKILL.md` control plane; resources have declared use |
| 8 | `context-architect` | cross-file impact map | affected files, imports/consumers, ripple effects, safe sequence, unrelated paths avoided |
| 9 | `skill-prompt-and-activation-review` | activation and boundaries | specific frontmatter, visible non-triggers, ambiguous rules, auditable output, stop conditions |
| 10 | `prompt-architect` | complex prompts/instructions | preserve intent; state success criteria; remove vague wording; examples only when calibrating |
| 11 | `skill-consistency-repair` | contradictions and integration gaps | compare `SKILL.md`, refs, scripts, templates, evals; links resolve; unsupported claims removed/marked |
| 12 | `documentation-quality` | references, examples, templates, script docs | docs have clear purpose, verified commands/artifacts, minimal duplication, source-backed claims |
| 13 | `karpathy-guidelines` | scripts and technical artifacts | scripts do one thing; explicit CLI; useful errors; no overbuilt framework; smoke/syntax check modified code |
| 14 | `security-and-governance-review` | secrets, unsafe commands, authority | no secrets/logging leaks; scoped writes; safe archive handling; tool authority and residual risks recorded |
| 15 | `skill-testing-and-validation` | validators, lint, smoke, package checks | structure validation, activation-harness check when compatible, link checks, modified scripts run/syntax-check, package validation recorded |
| 16 | `skill-cleanup-and-simplification` | hygiene and simplification | classify before deletion; remove only caches, old zips, generated noise, duplicates, scaffold; validate after cleanup |
| 17 | `skill-token-efficient` | main compression after stability | preserve triggers, exclusions, routing, safety, validation, output, stop; reduce conservatively; revalidate immediately |
| 18 | `skill-testing-and-validation` | post-compression validation | rerun affected validators, activation-harness check when compatible, and package checks; reject compression that weakens contract or fails gates |
| 19 | `skill-hardening` | final readiness and package maturity | inventory passes; support files integrated; no generated noise; validators/package checks pass; scope exact |
| 20 | final `skill-change-gate` | final acceptance gate | rerun or apply gate checklist after hardening/compression; no blocking regression may remain before final acceptance |
| 21 | final `skill-benchmark` | final score and delta | compare against baseline; measured vs judged evidence separated; residual risks and next hypothesis listed |
| 22 | final `skill-improver` closure | final decisions | accept/reject hypotheses; record files; gates; rollback; package only when validated |
| 23 | final `skill-token-efficient` closure | no avoidable waste after closure | prefer audit/validate mode; if mutating, rerun affected validation/package checks; preserve activation, safety, validation, output, stop, routing, and evidence duties |

## Pass rules

- Do not skip silently; mark unavailable specialists as `applied-by-checklist` using this passbook.
- When the user supplies an explicit required specialist sequence, invoke every available listed specialist. Use checklist-only only for unavailable, blocked, unsafe, or not-applicable specialists, and record why.
- `pass` means the specialist was actually invoked or an equivalent deterministic script/gate ran. Manual checklist review uses `applied-by-checklist` and `execution_type: checklist-only`; it is not specialist execution.
- Mark a pass `not-applicable` only with artifact evidence.
- `skill-hypothesis-discovery` is not a mutator. If it recommends no mutation, record the rationale and skip measured-improvement patches unless the user supplies a concrete hypothesis.
- A failed nonblocking specialist can still be reported, but readiness claims require explicit gate rationale. A `skill-change-gate` failure with blocking regression prevents acceptance until repaired, reverted, or explicitly narrowed out of scope with user approval.
- Never alter fixtures, expected outputs, frozen benchmark baselines, secrets, generated evidence, old zips, or unrelated files to make a pass look successful.


## Required sequence reconciliation gate

Before final readiness, completion, or package claims, reconcile the user-required sequence against actual execution evidence.

Required JSON ledger fields:

```json
{
  "required_specialists": [],
  "available_specialists": [],
  "invoked_specialists": [],
  "checklist_only": [],
  "blocked": [],
  "unavailable": [],
  "not_applicable": [],
  "not_run": [],
  "assume_required_available": false
}
```

Run:

```bash
python scripts/validate_specialist_reconciliation.py --ledger <LEDGER_JSON>
```

Finalization is blocked when a required specialist is unclassified, `not-run`, checklist-only under an explicit sequence, or available but not invoked/blocked/not-applicable. A report may say `full optimization completed` only when this gate passes or no explicit specialist sequence was supplied.
