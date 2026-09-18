# Specialist Passbook

Every complete Skill Booster run must execute, apply by checklist, or classify each pass below. Invoke specialists through the active host's native mechanism; the names below identify capabilities, not a specific API or tool syntax. Status values: `pass`, `fail`, `blocked`, `not-run`, `not-applicable`, `applied-by-checklist`, `planned`. Also record `execution_type`: `invoked-skill`, `deterministic-script`, `checklist-only`, `blocked`, `unavailable`, `not-applicable`, or `not-run`.

## Ordered pass ledger

| # | Pass | Purpose | Minimum evidence/checklist |
|---:|---|---|---|
| 1 | `skill-creator-juiced` | design governance and escalation | decide optimization vs redesign/router/split; preserve purpose; require package gates; no fabricated readiness |
| 2 | `skill-benchmark` | initial maturity score/report | structural vs behavioral evidence separated; no precision/recall without results; saturated score gets auxiliary metric |
| 3 | `skill-harness` | repeatable scenarios and gates | activation, non-activation, ambiguous, edge, regression, output-contract coverage; run `scripts/run_activation_harness.py` for schema/coverage when compatible; freeze suite; planned vs executed marked |
| 4 | reproducibility decision + optional `reproducibility-engineer` | identify controllable variance before backlog selection | evaluate `references/reproducibility-routing.md`; validate decision JSON; if applicable and available invoke `reproducibility-engineer` in `audit-only` by default or `apply` only for an explicit/bounded reproducibility transformation; otherwise record `not-applicable`, `blocked`, or `unavailable` with evidence |
| 5 | `skill-hypothesis-discovery` | evidence-based improvement backlog | derive 5-10 candidate hypotheses from benchmark, harness, reproducibility audit when applicable, architecture, validation, security, consistency, and token evidence; dedupe; rank; recommend top 1-3 for current cycle; mark no-mutation when warranted |
| 6 | `skill-improver` | objective, freeze, bounded experiments, decisions | use selected hypothesis or supplied backlog; baseline before mutation; one bounded hypothesis per patch; accept/reject with gates; proposals marked untested; do not re-own a batch explicitly delegated to reproducibility-engineer apply mode |
| 7 | `skill-change-gate` | candidate acceptance gate | classify candidate regressions as blocking, material, trade-off, or follow-up; reject or repair before accept when blocking regressions exist |
| 8 | `skill-package-architecture-review` | package structure decision | unified/modes/router/split/stop decision; `SKILL.md` control plane; resources have declared use |
| 9 | `context-architect` | cross-file impact map | affected files, imports/consumers, ripple effects, safe sequence, unrelated paths avoided |
| 10 | `skill-prompt-and-activation-review` | activation and boundaries | specific frontmatter, visible non-triggers, ambiguous rules, auditable output, stop conditions |
| 11 | `prompt-architect` | complex prompts/instructions | preserve intent; state success criteria; remove vague wording; examples only when calibrating |
| 12 | `skill-consistency-repair` | contradictions and integration gaps | compare `SKILL.md`, refs, scripts, templates, evals; links resolve; unsupported claims removed/marked |
| 13 | `documentation-quality` | references, examples, templates, script docs | docs have clear purpose, verified commands/artifacts, minimal duplication, source-backed claims |
| 14 | `karpathy-guidelines` | scripts and technical artifacts | scripts do one thing; explicit CLI; useful errors; no overbuilt framework; smoke/syntax check modified code |
| 15 | `security-and-governance-review` | secrets, unsafe commands, authority | no secrets/logging leaks; scoped writes; safe archive handling; tool authority and residual risks recorded |
| 16 | `skill-testing-and-validation` | validators, lint, smoke, package checks | structure validation, requested-host portability validation when applicable, activation-harness check when compatible, reproducibility-decision validator, link checks, modified scripts run/syntax-check, package validation recorded |
| 17 | `skill-cleanup-and-simplification` | hygiene and simplification | classify before deletion; remove only caches, old zips, generated noise, duplicates, scaffold; validate after cleanup |
| 18 | `skill-token-efficient` | main compression after stability | preserve triggers, exclusions, routing, safety, validation, output, stop; reduce conservatively; revalidate immediately |
| 19 | `skill-testing-and-validation` | post-compression validation | rerun affected validators, activation-harness check when compatible, reproducibility routing contract, and package checks; reject compression that weakens contract or fails gates |
| 20 | `skill-hardening` | final readiness and package maturity | inventory passes; support files integrated; no generated noise; validators/package checks pass; scope exact |
| 21 | final `skill-change-gate` | final acceptance gate | rerun or apply gate checklist after hardening/compression; no blocking regression may remain before final acceptance |
| 22 | final `skill-benchmark` | final score and delta | compare against baseline; measured vs judged evidence separated; residual risks and next hypothesis listed |
| 23 | final `skill-improver` closure | final decisions | accept/reject hypotheses; record files; gates; rollback; package only when validated |
| 24 | final `skill-token-efficient` closure | no avoidable waste after closure | prefer audit/validate mode; if mutating, rerun affected validation/package checks; preserve activation, safety, validation, output, stop, routing, reproducibility, and evidence duties |

## Reproducibility pass rules

- Always classify pass 4 before `skill-hypothesis-discovery`; never leave it implicit.
- `invoke-audit` requires actual `reproducibility-engineer` invocation in `audit-only`; its variability map becomes evidence for pass 5.
- `invoke-apply` requires actual invocation in `apply`; that specialist owns only the bounded reproducibility batch, followed by pass 7 before acceptance.
- `not-applicable` requires an evidence-based rationale showing no material controllable variance; scripts/evals alone do not make the specialist applicable.
- `blocked` and `unavailable` must preserve the material-signal evidence and must not be reported as specialist execution.
- Validate the routing record with `<PYTHON> scripts/validate_reproducibility_decision.py <DECISION_JSON>`.

## Pass rules

- Never skip passes silently; classify each one.
- For an explicit required sequence, invoke every available specialist. Checklist-only is allowed only when unavailable, blocked, unsafe, or not-applicable; it does not satisfy invocation.
- `pass` requires actual specialist invocation or equivalent deterministic script/gate. Manual review is `applied-by-checklist` with `execution_type: checklist-only`.
- Mark a pass `not-applicable` only with artifact evidence.
- `skill-hypothesis-discovery` is not a mutator. If it recommends no mutation, record the rationale and skip measured-improvement patches unless the user supplies a concrete hypothesis.
- A failed nonblocking specialist can still be reported, but readiness claims require explicit gate rationale. A `skill-change-gate` failure with blocking regression prevents acceptance until repaired, reverted, or explicitly narrowed out of scope with user approval.
- Never alter fixtures, expected outputs, frozen benchmark baselines, secrets, generated evidence, old zips, or unrelated files to make a pass look successful.
- After the final passing gate, freeze the exact candidate. Any target edit invalidates the freeze and requires affected validation plus a new manifest.

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

```text
<PYTHON> scripts/validate_specialist_reconciliation.py --ledger <LEDGER_JSON>
```

Finalization is blocked when a required specialist is unclassified, `not-run`, checklist-only under an explicit sequence, or available but not invoked/blocked/not-applicable. A report may say `full optimization completed` only when this gate passes or no explicit specialist sequence was supplied.
