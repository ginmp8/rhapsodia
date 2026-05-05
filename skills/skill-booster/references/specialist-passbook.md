# Specialist Passbook

Every complete Skill Booster run must execute, apply by checklist, or classify each pass below. Status values: `pass`, `fail`, `blocked`, `not-run`, `not-applicable`, `applied-by-checklist`, `planned`.

## Ordered pass ledger

| # | Pass | Purpose | Minimum evidence/checklist |
|---:|---|---|---|
| 1 | `skill-creator-juiced` | design governance and escalation | decide optimization vs redesign/router/split; preserve purpose; require package gates; no fabricated readiness |
| 2 | `skill-improver` | objective, freeze, hypotheses, decisions | baseline before mutation; one bounded hypothesis; accept/reject with gates; proposals marked untested |
| 3 | `skill-change-gate` | candidate acceptance gate | classify candidate regressions as blocking, material, trade-off, or follow-up; reject or repair before accept when blocking regressions exist |
| 4 | `skill-benchmark` | initial maturity score/report | structural vs behavioral evidence separated; no precision/recall without results; saturated score gets auxiliary metric |
| 5 | `skill-harness` | repeatable scenarios and gates | activation, non-activation, ambiguous, edge, regression, output-contract coverage; freeze suite; planned vs executed marked |
| 6 | `skill-package-architecture-review` | package structure decision | unified/modes/router/split/stop decision; `SKILL.md` control plane; resources have declared use |
| 7 | `context-architect` | cross-file impact map | affected files, imports/consumers, ripple effects, safe sequence, unrelated paths avoided |
| 8 | `skill-prompt-and-activation-review` | activation and boundaries | specific frontmatter, visible non-triggers, ambiguous rules, auditable output, stop conditions |
| 9 | `prompt-architect` | complex prompts/instructions | preserve intent; state success criteria; remove vague wording; examples only when calibrating |
| 10 | `skill-consistency-repair` | contradictions and integration gaps | compare `SKILL.md`, refs, scripts, templates, evals; links resolve; unsupported claims removed/marked |
| 11 | `documentation-quality` | references, examples, templates, script docs | docs have clear purpose, verified commands/artifacts, minimal duplication, source-backed claims |
| 12 | `karpathy-guidelines` | scripts and technical artifacts | scripts do one thing; explicit CLI; useful errors; no overbuilt framework; smoke/syntax check modified code |
| 13 | `security-and-governance-review` | secrets, unsafe commands, authority | no secrets/logging leaks; scoped writes; safe archive handling; tool authority and residual risks recorded |
| 14 | `skill-testing-and-validation` | validators, lint, smoke, package checks | structure validation, link checks, modified scripts run/syntax-check, package validation recorded |
| 15 | `skill-cleanup-and-simplification` | hygiene and simplification | classify before deletion; remove only caches, old zips, generated noise, duplicates, scaffold; validate after cleanup |
| 16 | `skill-token-efficient` | main compression after stability | preserve triggers, exclusions, routing, safety, validation, output, stop; reduce conservatively; revalidate immediately |
| 17 | `skill-testing-and-validation` | post-compression validation | rerun affected validators/package checks; reject compression that weakens contract or fails gates |
| 18 | `skill-hardening` | final readiness and package maturity | inventory passes; support files integrated; no generated noise; validators/package checks pass; scope exact |
| 19 | final `skill-change-gate` | final acceptance gate | rerun or apply gate checklist after hardening/compression; no blocking regression may remain before final acceptance |
| 20 | final `skill-benchmark` | final score and delta | compare against baseline; measured vs judged evidence separated; residual risks and next hypothesis listed |
| 21 | final `skill-improver` closure | final decisions | accept/reject hypotheses; record files; gates; rollback; package only when validated |
| 22 | final `skill-token-efficient` closure | no avoidable waste after closure | prefer audit/validate mode; if mutating, rerun affected validation/package checks; preserve activation, safety, validation, output, stop, routing, and evidence duties |

## Pass rules

- Do not skip silently; mark unavailable specialists as `applied-by-checklist` using this passbook.
- Mark a pass `not-applicable` only with artifact evidence.
- A failed nonblocking specialist can still be reported, but readiness claims require explicit gate rationale. A `skill-change-gate` failure with blocking regression prevents acceptance until repaired, reverted, or explicitly narrowed out of scope with user approval.
- Never alter fixtures, expected outputs, frozen benchmark baselines, secrets, generated evidence, old zips, or unrelated files to make a pass look successful.
