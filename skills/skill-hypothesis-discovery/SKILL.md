---
name: skill-hypothesis-discovery
description: use when asked to discover, generate, research, rank, triage, or plan testable improvement hypotheses for an existing chatgpt or agent skill package before mutation. analyzes target skill evidence, benchmark or harness findings, validation logs, architecture reviews, activation failures, token audits, security or cleanup findings, and prior gate results to produce a prioritized hypothesis backlog for skill-improver, skill-booster, or manual optimization. does not edit files, run random search, accept candidate patches, or claim measured improvement without executed or supplied evidence.
---

# Skill Hypothesis Discovery

## Mission

Discover and prioritize evidence-backed hypotheses for improving an existing skill package. Act as a no-mutation planning specialist: inspect available evidence, generate candidate hypotheses, rank them by impact, risk, confidence, and testability, and recommend which hypotheses `skill-improver` or an orchestrator should test next.

Do not apply patches, accept candidates, run unbounded random search, change evaluators, or claim measured improvement. A good outcome may be `no mutation recommended` when the target is already strong or evidence is insufficient.

## Scope

Use for:

- generating a hypothesis backlog before `skill-improver` tests candidates;
- finding next useful experiments when benchmark or audit scores are saturated;
- converting benchmark, harness, validation, activation, architecture, consistency, security, cleanup, hardening, or token-efficiency findings into testable hypotheses;
- deciding whether a skill should be mutated, observed with more evidence, or left unchanged;
- producing top hypotheses for `skill-booster` full optimization and `skill-creator-juiced` quality-upgrade/redesign workflows.

Do not use for:

- creating a new skill package from scratch;
- applying code, markdown, or package mutations;
- accepting or rejecting a concrete patch; use `skill-change-gate` for candidate acceptance;
- running benchmark scoring; use `skill-benchmark` for scoring;
- building scenario harnesses; use `skill-harness` for harness design and execution;
- ordinary application-code review or non-skill prompt rewriting;
- editing evaluator fixtures, expected outputs, generated baselines, secrets, credentials, `.git`, generated evidence, old zips, or unrelated files.

## Required Inputs

Proceed with explicit assumptions when some evidence is missing, but mark hypotheses as `gather-evidence` or return `insufficient-evidence` when the next test cannot be justified.

1. Target skill identity: folder, zip, root `SKILL.md`, inspected text, or package name.
2. Evidence package: target files, benchmark report, harness map, scenario results, validation logs, reviewer findings, prior outputs, user feedback, or stated gaps.
3. Caller context: `skill-booster`, `skill-improver`, `skill-creator-juiced`, manual planning, redesign, hardening, cleanup, token-efficiency, or closure review.
4. Discovery mode: `backlog-discovery`, `deep-discovery`, `closure-discovery`, or `evidence-gap-review`.
5. Constraints: blocked paths, protected evaluator assets, allowed mutation scope, desired max hypotheses, risk tolerance, and whether a measurable evaluator already exists.
6. Output target: inline markdown backlog, JSON backlog, or both.

## Modes

| Mode | Use when | Output |
|---|---|---|
| `backlog-discovery` | baseline evidence exists and next hypotheses are needed | 5-10 candidates, top 3-5, next 1-3 tests |
| `deep-discovery` | full optimization needs a stronger search | broad pass plus critique/dedupe pass, top 5-8 |
| `closure-discovery` | an optimization cycle ended and next work is needed | no-mutation decision or follow-up backlog |
| `evidence-gap-review` | metrics are saturated or missing | evidence gaps, auxiliary metrics, safe next checks |

Default to `backlog-discovery`. Use `deep-discovery` only when explicitly requested or when `skill-booster` full optimization needs a wider backlog.

## Resource Loading

Load only the needed branch:

- `references/discovery-method.md` for evidence signals, broad/deep passes, no-mutation rules, and anti-random-search policy.
- `references/hypothesis-schema.md` for hypothesis fields, scoring, ranking, dedupe, and JSON contract.
- `references/integration-workflows.md` when integrating with `skill-booster`, `skill-improver`, `skill-creator-juiced`, `skill-harness`, `skill-benchmark`, or `skill-change-gate`.
- `scripts/validate_hypothesis_backlog.py` when validating a JSON backlog or ranking hypotheses deterministically.
- `assets/templates/hypothesis-backlog.json.template` when a JSON artifact is useful.
- `assets/templates/hypothesis-report.md.template` when a durable markdown report is useful.
- `examples/hypothesis-discovery-examples.md` for calibrated outputs.
- `evals/activation-scenarios.json` for planned activation and non-activation coverage; treat it as planned evidence unless executed.

## Workflow

1. **Resolve target and evidence.** Identify the target skill, caller context, available evidence, missing evidence, blocked paths, and whether there is a frozen evaluator.
2. **Classify evidence signals.** Group findings by activation, non-activation, ambiguity handling, output contract, package architecture, resource integration, documentation, scripts, security, validation, packaging, token cost, behavioral coverage, benchmark saturation, and prior gate failures.
3. **Generate hypotheses from evidence only.** Produce 5-10 candidate hypotheses in `backlog-discovery`. In `deep-discovery`, run a second critique pass that deduplicates, combines, risk-ranks, and finds missing hypothesis classes. Do not invent random mutations.
4. **Define each hypothesis.** State mechanism, target area, likely files, expected effect, required evaluator or gate, risk, cost, confidence, and rollback/gate requirements. Mark non-mutation hypotheses such as adding evidence or holdout scenarios when mutation is premature.
5. **Score and rank.** Use impact, confidence, testability, risk, cost, and gate availability. Prefer hypotheses that are small, measurable, reversible, and tied to observed evidence.
6. **Select next tests.** Recommend top 3-5 hypotheses overall and the next 1-3 for the current optimization cycle. Defer cosmetic or low-evidence ideas.
7. **Return no-mutation when appropriate.** If the skill is already strong, metrics are saturated, or risk exceeds expected benefit, recommend evidence collection or no change rather than forced edits.
8. **Report handoff.** State which hypothesis should go to `skill-improver`, what evidence `skill-harness` or `skill-benchmark` should provide, and what `skill-change-gate` must verify after a candidate patch.

## Hypothesis Rules

- No random search. Every hypothesis must cite an observed signal, missing evidence, or explicit user goal.
- Do not mutate the target. The output is a backlog, not a patch.
- Do not change or weaken evaluator fixtures, expected outputs, scoring weights, benchmark baselines, or generated evidence to make a hypothesis pass.
- Do not recommend cosmetic rewrites unless they address activation, output conformance, validation, maintainability, or token cost with a testable effect.
- Treat saturated scores as gates. Add auxiliary metrics before claiming further improvement.
- Prefer `gather-evidence` over mutation when behavioral coverage, activation prompts, or output conformance results are missing.
- Mark duplicate, overlapping, risky, or low-value hypotheses as deferred or rejected with rationale.

## Output Contract

Return this structure for substantive runs:

```markdown
## Skill Hypothesis Discovery Result

- target:
- mode:
- caller context:
- evidence status: measured | supplied | derived | planned | mixed | insufficient
- recommendation: test-hypotheses | gather-evidence | no-mutation-recommended

### Evidence inspected
- target evidence:
- benchmark/harness/validation evidence:
- reviewer or user feedback:
- missing evidence:

### Hypothesis backlog
| id | hypothesis | evidence signal | expected effect | validation | impact | confidence | testability | risk | recommendation |
|---|---|---|---|---|---:|---:|---:|---:|---|

### Top hypotheses for this cycle
1. 
2. 
3. 

### Deferred or rejected hypotheses
- 

### Handoff
- to `skill-improver`:
- to `skill-harness` or `skill-benchmark`:
- to `skill-change-gate`:
```

Use JSON only when requested or when another workflow needs machine-readable input. Validate JSON with `scripts/validate_hypothesis_backlog.py` when available.

## Stop Conditions

Stop or return `insufficient-evidence` when:

- no target skill content or inspected summary is available;
- the request asks this skill to edit files, accept patches, or package artifacts;
- the target has zero or multiple root `SKILL.md` files and the intended skill cannot be inferred;
- hypotheses would depend on changing blocked paths, evaluator fixtures, expected outputs, generated baselines, secrets, credentials, `.git`, or unrelated files;
- the user requests measured benchmark, precision, recall, robustness, or pass-rate claims without executed or supplied evidence;
- available evidence is too thin to choose a safe next experiment and the user requires mutation.

## Integration Defaults

For `skill-booster`, run once after baseline benchmark/harness evidence exists; use `deep-discovery` for full optimization when no high-confidence hypothesis is already supplied. For `skill-improver`, use this skill only when no bounded hypothesis is provided or the evaluator is saturated. For `skill-creator-juiced`, use it in redesign or quality-upgrade modes, not routine net-new creation. Do not make `skill-harness`, `skill-benchmark`, or `skill-change-gate` depend on this skill.
