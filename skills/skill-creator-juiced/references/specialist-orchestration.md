# Specialist Orchestration

Use this reference to coordinate specialist skills during creation, upgrade, and finalization of a skill package.

## Principle

Specialists are not decorative. Call or apply a specialist only when it owns a real risk, artifact, or gate in the package. When multiple specialists apply, use them in the order below so early design defects do not pollute later validation.

## Specialist Map

| Phase | Specialist | Use when | Output expected |
|---|---|---|---|
| requirement shaping | `prompt-architect` | the user's idea is a rough prompt, reusable instruction set, or ambiguous behavior specification | refined prompt/instruction contract, success criteria, scenarios |
| repository context | `context-architect` | the skill depends on a repo, codebase, package, existing scripts, or implementation patterns | context map, source truth, impacted files, validation plan |
| code discipline | `karpathy-guidelines` | writing or reviewing bundled scripts, validators, examples, or technical implementation guidance | minimal code, evidence labels, validation plan, anti-overengineering checks |
| package architecture | `skill-package-architecture-review` | deciding one skill vs modes vs router vs split, resource layout, progressive loading | architecture decision and resource map |
| activation | `skill-prompt-and-activation-review` | frontmatter description, boundaries, stop conditions, activation/non-activation cases | improved trigger text, negative cases, ambiguity findings |
| documentation | `documentation-quality` | writing or reviewing references, readmes, script docs, examples, templates | clearer docs, verified claims, link/file checks |
| testing | `skill-testing-and-validation` | bundled code, validators, packaging scripts, eval files, command discovery | baseline, commands, pass/fail evidence, minimal fixes |
| security | `security-and-governance-review` | scripts, tool authority, sensitive data, dependencies, governance, compliance, responsible-ai risk | findings, severity, safe remediation plan, residual risk |
| consistency | `skill-consistency-repair` | contradictions, orphaned resources, stale scaffold, broken links, unsupported claims | repaired contract and validation evidence |
| cleanup | `skill-cleanup-and-simplification` | placeholder files, duplicate guidance, caches, old zips, unintegrated resources | classified cleanup and package hygiene |
| token efficiency | `skill-token-efficient` | instructions are bloated or repeated after behavior is stable | reduced token cost with preserved semantics |
| harness | `skill-harness` | repeatable gate, scenario suite, evaluator, package evidence, or audit harness is needed | harness map, scenarios, validators, package gates |
| benchmark | `skill-benchmark` | user wants scorecard, maturity report, comparison, or publish-readiness | benchmark report, score, measured/planned distinction |
| measured improvement | `skill-improver` | an evaluator is frozen and a bounded hypothesis can be tested | baseline/final metric, accepted/rejected hypothesis |
| change acceptance | `skill-change-gate` | a material update, redesign, cleanup, hardening, or token-efficiency candidate must be accepted without regression | pass/pass-with-warnings/fail decision, blocking regressions, accepted trade-offs |
| final hardening | `skill-hardening` | existing generated package needs maturity upgrade, validation, and uploadable delivery | hardening changes, gates, package readiness |

## Default Path

For ordinary new skills, apply:

1. `prompt-architect` if the behavior is under-specified.
2. `skill-package-architecture-review` for cohesion and resource layout.
3. `skill-prompt-and-activation-review` for description and boundaries.
4. `documentation-quality` for references/examples.
5. `skill-testing-and-validation` for scripts and validators.
6. `security-and-governance-review` when scripts, tools, connectors, or sensitive data are involved.
7. `skill-consistency-repair` and `skill-cleanup-and-simplification` before packaging.
8. `skill-token-efficient` after content stabilizes.
9. `skill-change-gate` for existing-skill updates or redesigns before final acceptance; use advisory mode for net-new skills without before/after evidence.

## Full Juiced Path

For production-ready, publish-ready, or high-risk skills, add:

1. `skill-harness` to define scenarios, metrics, gates, and evidence capture.
2. `skill-benchmark` for a maturity score and readiness report.
3. `skill-improver` for one measured improvement loop when a frozen evaluator exists.
4. `skill-change-gate` after material candidate changes and again before final delivery when the package was modified from an existing baseline.
5. `skill-hardening` for final package maturity and delivery validation.

## Handoff Rules

- If a specialist is unavailable, apply the local checklist from this skill and mark the specialist pass as not run.
- If a specialist reports a blocking issue, fix it before proceeding to later gates. Treat `skill-change-gate` `fail` as blocking for existing-skill updates unless the user explicitly narrows the work to advisory review.
- If a requested pass would require fabricated metrics, report planned scenarios instead of measured results.
- Do not let a downstream specialist expand the target skill beyond its original role without evidence and user intent.
