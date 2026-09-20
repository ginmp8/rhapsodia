---
name: skill-hypothesis-discovery
description: use when asked to discover, generate, rank, triage, or plan testable improvement hypotheses for an existing Agent Skills-compatible skill package before mutation. consumes identified target evidence, benchmark/harness findings, validation logs, specialist reviews, gate results, and explicit evidence gaps to produce a small evidence-bound hypothesis backlog with deterministic eligibility, deduplication, ranking, and experiment selection. does not edit the target skill, run random search, accept candidate patches, or claim measured improvement without executed/supplied evidence.
---

# Skill Hypothesis Discovery

## Mission

Discover a small set of evidence-backed, testable improvement hypotheses for an existing skill package before mutation. The output is a planning/evidence artifact, not a patch.

Prevent open-ended idea generation from becoming random search. A plausible idea is not a valid hypothesis until it is tied to identified evidence, a causal mechanism, a measurable expected effect, an evaluator, and explicit acceptance criteria.

A valid outcome may be `gather-evidence` or `no-mutation-recommended`.

## Core guarantees

Given the same target identity, evidence snapshot, mode, and constraints, produce a materially equivalent backlog:

- same item taxonomy;
- same evidence eligibility decisions;
- same dedupe/conflict/dependency treatment;
- same scoring inputs and deterministic tie-breaks;
- same bounded selection when the criteria determine an order.

Exact wording and causal interpretation may vary where semantic judgment is irreducible. Do not fake byte-level determinism for analytic work.

## Scope

Use for:

- generating a backlog before `skill-improver` tests candidates;
- converting benchmark, harness, validation, activation, architecture, consistency, security, cleanup, hardening, token-efficiency, or user-feedback evidence into bounded hypotheses;
- finding the next safe experiment when current metrics are saturated;
- distinguishing mutation hypotheses from evidence gaps, recommendations, and unsupported speculation;
- deciding when the correct next step is more evidence or no mutation.

Do not use for:

- creating a new skill package from scratch;
- editing or packaging the target skill;
- accepting/rejecting a concrete patch (`skill-change-gate` owns candidate acceptance);
- executing benchmark scoring (`skill-benchmark` owns scoring);
- building/running a scenario harness (`skill-harness` owns harness execution);
- changing evaluators, fixtures, thresholds, expected outputs, generated baselines, secrets, credentials, `.git`, or unrelated files;
- ordinary application-code review or generic prompt rewriting.

## Portable core

Treat Agent Skills as the semantic core: `SKILL.md` plus relative `references/`, `scripts/`, `assets/`, `examples/`, `evals/`, and optional tests. Do not make correctness depend on ChatGPT/Codex, Claude, GitHub Copilot, Cursor, or another host-specific invocation mechanism.

`agents/openai.yaml` is an optional OpenAI adapter only. Host-specific metadata may coexist with the core but must not define discovery semantics.

## Required inputs

Resolve before discovery:

1. **Target identity** — package/root plus strongest available stable version/hash/revision.
2. **Evidence package** — target files, reports, scenario results, logs, review findings, prior gate results, user feedback, or explicit missing evidence.
3. **Caller context** — manual planning, `skill-booster`, `skill-improver`, `skill-creator-juiced`, hardening, cleanup, token-efficiency, closure review, etc.
4. **Mode** — `backlog-discovery`, `deep-discovery`, `closure-discovery`, or `evidence-gap-review`.
5. **Constraints** — protected paths, mutation scope, risk tolerance, known evaluators/metrics, and explicit user priorities.
6. **Output** — markdown backlog, JSON v2 backlog, or both.

If exact target/evidence identity is unavailable, record that limitation explicitly. Do not invent hashes, revisions, measurements, or evaluator availability.

## Modes and limits

| Mode | Use when | Final limit | Selected limit |
|---|---|---:|---:|
| `backlog-discovery` | normal baseline evidence exists | 8 items | 3 |
| `deep-discovery` | broad optimization needs a critique/dedupe pass | 8 final items | 3 |
| `closure-discovery` | an optimization cycle ended | 5 items | 2 |
| `evidence-gap-review` | metrics/evaluators/evidence are missing or saturated | 5 items | 0 |

Default to `backlog-discovery`. `deep-discovery` may consider more raw ideas internally, but only the deduplicated bounded final set is returned.

## Progressive loading

Load only what the active branch needs:

- `references/discovery-method.md` — deterministic discovery pipeline, minimum evidence, dedupe/conflicts, saturation, and stop rules.
- `references/hypothesis-schema.md` — v2 taxonomy, JSON contract, ranking, tie-breakers, and experiment limits.
- `references/integration-workflows.md` — handoffs to optimizer/harness/benchmark/change-gate workflows.
- `scripts/validate_hypothesis_backlog.py` — validate and deterministically rank JSON backlogs. The v2 result also emits a canonical `hypothesis_pool_id` for downstream evolutionary contracts.
- `contracts/integration-manifest.json` — declares the hypothesis-pool v2 surface for cross-skill impact analysis.
- `assets/templates/hypothesis-backlog.json.template` — canonical v2 machine-readable example.
- `assets/templates/hypothesis-report.md.template` — durable markdown report template.
- `examples/hypothesis-discovery-examples.md` — calibrated examples.
- `evals/activation-scenarios.json` — activation/non-activation contract.
- `evals/discovery-regression-scenarios.json` — required regression behaviors for evidence gaps, duplicates, conflicts, missing evaluators, saturation, measurability, and ranking ties.

## Workflow

### 1. Establish baseline identity

Resolve exactly one target skill and record the strongest available stable identity. Do not merge evidence from different target versions without identifying each version separately.

### 2. Snapshot the evidence set

Assign stable evidence ids and record provenance/status. For JSON v2 output, compute `evidence_snapshot.snapshot_id` from the exact source records using the bundled validator contract.

Evidence labels are factual claims:

- `measured` — executed result;
- `observed` — direct inspection;
- `derived` — deterministic calculation;
- `supplied` — caller/user result not independently rerun;
- `planned` — intended, not executed;
- `gap` — known missing evidence;
- `unknown` — provenance/status unresolved.

Do not upgrade weaker evidence labels for presentation.

### 3. Classify signals before generating candidates

Group signals by activation, ambiguity, output, architecture, consistency, documentation, validation, security, packaging, token cost, behavioral evidence, and evidence/evaluator gaps.

### 4. Classify each backlog item

Every item is exactly one of:

- `testable-hypothesis`;
- `recommendation`;
- `evidence-gap`;
- `unsupported-speculation`.

Only a `testable-hypothesis` can enter the experiment queue.

### 5. Apply the minimum-evidence gate

A testable hypothesis must state:

`hypothesis -> evidence refs -> mechanism -> expected effect -> evaluator -> acceptance criteria`

Use `references/hypothesis-schema.md` for the exact contract. If any link is missing, downgrade the item; do not fill the gap with plausibility.

### 6. Dedupe and map conflicts/dependencies

Create the canonical dedupe key, merge duplicates, inspect semantic near-duplicates, and declare `conflicts_with` / `depends_on` edges. Do this before scoring.

Never delete or dismiss a candidate merely because its wording resembles another one; compare mechanism, subject, effect, evidence, and acceptance criteria first.

### 7. Handle saturated metrics

A saturated primary metric becomes a regression gate. Do not optimize noise around it. Select another mutation only when a relevant active auxiliary metric exists. Otherwise return an evidence gap or `no-mutation-recommended`.

### 8. Score and rank eligible hypotheses

For ready testable hypotheses:

```text
priority = impact + confidence + testability - risk - ceil(cost / 2)
```

Tie-break in this exact order:

1. blocking gate effect;
2. higher priority score;
3. higher testability;
4. higher confidence;
5. lower risk;
6. lower cost;
7. lexical id.

Scores only rank eligible hypotheses. A high score cannot rescue weak evidence, a missing evaluator, an unmeasurable effect, or an unresolved dependency.

### 9. Select a controlled experiment queue

Return at most the mode-specific shortlist. `selected_for_testing` is ordered and must follow the deterministic ranking. `next_hypothesis_id` identifies exactly one next experiment.

Downstream mutation should test one bounded hypothesis at a time unless inseparability is explicitly evidenced.

### 10. Validate machine-readable output

For JSON v2 output run:

```text
<PYTHON> scripts/validate_hypothesis_backlog.py --input <BACKLOG.json> --json-output <RESULT.json>
```

Resolve `<PYTHON>` from host capabilities; do not assume a product-specific executable name. The script is standard-library only.

### 11. Handoff

Pass target identity, evidence snapshot id, hypothesis id, dedupe key, evidence refs, mechanism, expected effect, evaluator, acceptance criteria, conflicts/dependencies, rank inputs, and risk notes to the next workflow.

## Non-negotiable rules

- No random search or mutation-by-taste.
- Do not accept a hypothesis solely because it is plausible.
- Do not mutate the target package.
- Do not weaken or rewrite evaluators/fixtures/baselines to make a hypothesis viable.
- Identify and freeze the evaluator that will decide a downstream experiment before mutation; do not author or edit it after seeing candidate results.
- Do not select a `test-now` hypothesis without an available evaluator and active measurement surface.
- Do not select conflicting hypotheses in the same shortlist batch.
- Do not keep duplicate hypotheses as artificial backlog volume.
- Do not claim behavioral improvement from static structure, planned evals, or one invented scenario.
- Prefer evidence collection or no mutation over forced optimization.

## Markdown output contract

For substantive runs return:

```markdown
## Skill Hypothesis Discovery Result

- target:
- baseline identity:
- mode:
- caller context:
- evidence snapshot:
- evidence status: measured | observed | supplied | derived | planned | mixed | insufficient
- recommendation: test-hypotheses | gather-evidence | no-mutation-recommended

### Evidence inspected
- E001 — <status> — <identity> — <claim>
- missing evidence:

### Metrics/evaluators
- primary metric and saturation state:
- active auxiliary metrics:
- available evaluators:

### Backlog
| id | kind | hypothesis / gap | evidence | expected effect | evaluator | priority | recommendation |
|---|---|---|---|---|---|---:|---|

### Selected for testing
1. <next_hypothesis_id>
2. ...

### Deferred / rejected / evidence gaps
- ...

### Handoff
- to skill-improver:
- to skill-harness or skill-benchmark:
- to skill-change-gate:
```

Use JSON v2 when requested or when another workflow needs machine-readable input.

## Stop conditions

Stop candidate generation and return `gather-evidence`, `insufficient-evidence`, or `no-mutation-recommended` when:

- target identity/content is not sufficient to know what was analyzed;
- the available evidence cannot support a causal and measurable hypothesis;
- the required evaluator does not exist and cannot be defined independently before mutation;
- the primary metric is saturated and no meaningful active auxiliary metric exists;
- the expected effect cannot be expressed as an observable acceptance criterion;
- every candidate is duplicate, conflicted, blocked, dependent on missing evidence, or unsupported speculation;
- the mode limit is reached and additional items would only be weak variants;
- the only next step would be random edits/search;
- the request asks this skill to mutate, accept, or package the target instead of discovering hypotheses.

## Integration defaults

For `skill-booster`, run after baseline benchmark/harness evidence exists. For `skill-improver`, use discovery only when no bounded hypothesis is supplied or the current evaluator is saturated/blocked. For `skill-creator-juiced`, use it for redesign/quality-upgrade of an existing package, not routine net-new creation. Do not make `skill-harness`, `skill-benchmark`, or `skill-change-gate` depend on this skill.
