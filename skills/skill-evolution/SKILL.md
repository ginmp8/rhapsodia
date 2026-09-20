---
name: skill-evolution
description: "use when explicitly invoked as the multi-candidate search controller, or when an optimization orchestrator hands off a prepared evolutionary-search contract for an existing Agent Skills-compatible skill; controls champion-challenger search, transformation recombination, backcross, Pareto selection, novelty preservation, lineage, stagnation, and finalist selection. Do not auto-own generic optimize/evolve-this-skill requests, ordinary single-candidate optimization, net-new skill creation, direct target mutation, benchmark ownership, or final promotion/package decisions."
---

# Skill Evolution

## Mission

Control evidence-guided multi-candidate search over an existing skill without becoming a second optimizer, benchmark, harness, or acceptance gate. Treat the caller's frozen baseline, capabilities, transformations, evaluator identities, and hard gates as immutable search inputs. Search over candidate strategies and semantic transformations, preserve lineage, keep useful diversity, and return finalists plus complete evidence for an external promotion decision.

## Authority boundary

This skill owns:

- candidate population/search state;
- lineage and parent relationships;
- candidate roles and search-step identities;
- transformation recombination plans;
- backcross and repair-crossover plans;
- Pareto/non-dominance selection;
- novelty/diversity preservation;
- champion-challenger bookkeeping;
- search budget, stagnation, and termination;
- finalist selection.

This skill does **not** own:

- discovery of the whole specialist catalog;
- editing target skill bytes directly;
- executing a mutation implementation;
- benchmark scoring semantics;
- scenario/harness execution;
- candidate acceptance gates;
- changing frozen evaluators or thresholds;
- promoting a candidate to target baseline;
- promoting a search strategy into another skill's canonical workflow;
- final packaging or installation.

The caller provides mutation and evaluation capabilities. This skill emits requests and selection decisions over their returned evidence.

## Required inputs

Resolve before starting search:

1. `TARGET_IDENTITY`: exact baseline skill identity/hash or immutable snapshot reference.
2. `TARGET_CLASS`: caller-supplied target class when available.
3. `CAPABILITY_MAP`: semantic capabilities/invariants that candidates must preserve when material.
4. `HYPOTHESIS_POOL`: evidence-backed hypotheses or transformation candidates. Empty is allowed only for a canonical/control-only dry run.
5. `TRANSFORMATION_REGISTRY`: stable transformation ids with dependencies/conflicts where available.
6. `EVALUATION_POLICY`: objective metrics with direction, hard gates, evaluator/scenario identities, and ladder levels available.
7. `MUTATION_INTERFACE`: caller contract capable of creating an isolated candidate from one base parent plus zero or more donor/transformation instructions.
8. `EVALUATION_INTERFACE`: caller contract capable of returning identity-bound gates/metrics for a candidate under frozen evidence.
9. `SEARCH_BUDGET`: default values below unless explicitly overridden.

Default budget:

```yaml
initial_variants: 4
max_active_candidates: 4
max_total_candidates: 20
expected_total_candidates: 8-12
finalists: 2
stagnant_rounds: 3
max_recombination_proposals_per_round: 3
```

Twenty candidates is a ceiling, not a target.

## Search modes

- `plan-only`: validate inputs and emit the initial candidate/recombination plan without creating or evaluating candidates.
- `search`: run the full caller-mediated search until termination or finalists are selected.
- `resume`: continue from a validated search state.
- `selection-only`: rank/select from already evaluated candidates without requesting mutation.
- `validation-only`: validate search contract/state/lineage and report defects without changing search state.

Default to `search` only when mutation/evaluation interfaces are actually available. Otherwise use `plan-only` or `selection-only` and state the limitation.

## Progressive loading

Load only what the active stage needs:

- [references/search-model.md](references/search-model.md): search lifecycle, initial variants, budget, and stop conditions.
- [references/candidate-and-lineage-contract.md](references/candidate-and-lineage-contract.md): candidate ids, parentage, roles, identities, and lineage invariants.
- [references/recombination-contract.md](references/recombination-contract.md): transformation merge, backcross, repair crossover, compatibility rules, and candidate requests.
- [references/selection-and-pareto.md](references/selection-and-pareto.md): hard-gate filtering, non-dominance, novelty, diversity, and deterministic tie-breaks.
- [references/evaluation-and-promotion.md](references/evaluation-and-promotion.md): evaluation ladder use, parent/baseline comparison, holdout discipline, and promotion boundary.
- [references/host-portability.md](references/host-portability.md): portable-core requirements and runtime capability handling.
- [assets/templates/search-contract.json.template](assets/templates/search-contract.json.template): portable search contract.
- [assets/templates/search-state.json.template](assets/templates/search-state.json.template): portable lineage/population state.
- [assets/templates/search-report.md.template](assets/templates/search-report.md.template): durable report skeleton.
- [scripts/validate_search_contract.py](scripts/validate_search_contract.py): deterministic contract validation.
- [scripts/validate_search_state.py](scripts/validate_search_state.py): deterministic state/lineage validation including cycle and budget checks.
- [scripts/select_survivors.py](scripts/select_survivors.py): hard-gate-first Pareto/novelty selection from supplied evaluation evidence.
- [scripts/plan_recombination.py](scripts/plan_recombination.py): deterministic candidate-request planning from surviving candidates and transformation sets.
- [evals/activation-scenarios.json](evals/activation-scenarios.json): planned activation/boundary coverage; not behavioral proof until executed.

## Workflow

### 1. Freeze and validate search inputs

Record baseline, capability/evaluator identities, transformation/hypothesis inputs, objective directions, hard gates, budget, and caller interfaces. Run:

```text
<PYTHON> scripts/validate_search_contract.py <SEARCH_CONTRACT.json>
```

Do not start multi-candidate search when baseline/evaluator identity is mutable or hard-gate semantics are missing.

### 2. Seed a deliberately small initial population

Default to four roles when evidence supports them:

1. `canonical`: candidate produced by the caller's normal canonical optimization strategy;
2. `evidence-driven`: alternate evidence-backed hypothesis selection;
3. `focused`: strategy centered on the most material diagnosed weakness;
4. `novel-bounded`: materially different but still evidence-backed and contract-safe strategy.

Do not invent transformations merely to fill four slots. Fewer seeds are valid when the evidence only supports fewer distinct strategies. Preserve the original baseline as immutable reference even when it is not an active candidate.

### 3. Request candidate generation, never edit directly

Emit a `candidate_request` containing candidate id, operator, base parent, donor parents if any, transformation ids, capabilities expected to change, and causal intent. The mutation owner returns candidate identity plus transformation receipt. Reject mismatched or untraceable receipts.

### 4. Evaluate cheaply first

Use the caller's staged evaluation ladder. Require lower hard gates before escalation. Typical progression:

`L0 structural -> L1 deterministic -> L2 focused -> optional L3 harness -> optional L4 benchmark -> promotion-only L5 holdout`

Do not send obviously invalid candidates to expensive evaluation.

### 5. Select survivors without collapsing all trade-offs into one score

Apply hard gates first. Then use objective directions to calculate non-dominance. Preserve useful diversity when the Pareto set exceeds active capacity. Never compensate a failed safety/semantic/activation/validation gate with token, cost, or quality gains.

If no frozen scalar weighting policy exists, do not invent an overall numeric winner among non-dominated candidates.

### 6. Recombine only justified complementary evidence

Supported operators:

- `transformation-merge`: combine compatible accepted transformations from different parents;
- `backcross`: retain a novel/high-value transformation while restoring canonical/baseline characteristics through a canonical parent;
- `repair-crossover`: combine a strong candidate with a donor transformation specifically addressing its evidenced deficit;
- `bounded-mutation`: add/remove/replace one evidence-backed transformation or strategy parameter.

Never merge raw file diffs blindly. Resolve transformation dependencies/conflicts before requesting a child. Prefer one causal question per child.

### 7. Preserve lineage and rejected evidence

Every candidate must record parent ids, operator, transformations, evaluation identities, gate outcomes, metric values, novelty evidence, and terminal status. Rejected candidates remain in history; do not rewrite them out of the experiment record.

Validate state after each round:

```text
<PYTHON> scripts/validate_search_state.py --contract <SEARCH_CONTRACT.json> --state <SEARCH_STATE.json>
```

### 8. Stop when additional search is no longer justified

Stop on the first applicable condition:

- requested finalists are selected and promotion-level evidence is sufficient;
- `max_total_candidates` is reached;
- configured consecutive stagnant rounds produce no materially new non-dominated candidate;
- no new evidence-backed mutation/recombination is available;
- all remaining candidates violate hard gates or duplicate existing strategies;
- evaluator sensitivity is insufficient to distinguish candidates reliably;
- further search would require changing frozen evaluators/thresholds.

Do not consume the remaining budget simply because it exists.

### 9. Use holdout only for finalists when needed

When overfitting risk is material, request L5 holdout only for finalists. If holdout details are exposed and used to repair a candidate, that holdout is no longer unseen; require a fresh holdout for a later blind promotion claim.

### 10. Return finalists; never self-promote

Return:

- complete search identity and termination reason;
- baseline/canonical reference identities;
- candidate lineage and transformation history;
- hard-gate eliminations;
- Pareto archive/non-dominated candidates;
- finalists and why they survived;
- unresolved trade-offs;
- evidence level reached per finalist;
- holdout status;
- recommendation to caller: `promote-candidate`, `keep-baseline`, `gather-evidence`, or `no-single-winner`.

The caller owns final acceptance, candidate freeze, package, and target/workflow promotion.

## Selection invariants

- Baseline/evaluator identities never change mid-search without explicit restart/re-baseline.
- Hard-gate failure eliminates a candidate from normal survival.
- Original/canonical references remain available for comparison and backcross even if not active survivors.
- Parent and stable baseline are distinct semantic roles.
- Search state is append-only for historical candidate records except for lifecycle/status fields.
- No candidate may parent itself or create a lineage cycle.
- Candidate ids and transformation ids are unique within their registries.
- A child cannot claim a transformation absent from its generation receipt.
- Non-dominated alternatives may coexist; a single global winner is not mandatory.
- Search strategy success on one target does not automatically become canonical policy for another target/class.

## Output contract

Every substantive run reports:

1. target/baseline identity and target class;
2. mode, search id, budget, capabilities, and runtime limits;
3. frozen evaluator/scenario/hard-gate identities;
4. initial candidate strategy plan;
5. all candidate requests and returned identities;
6. lineage graph/table and transformation provenance;
7. evaluation level reached by each candidate;
8. hard-gate eliminations and reasons;
9. Pareto/non-dominated archive and diversity decisions;
10. recombination/backcross/mutation decisions with evidence;
11. stagnation/budget counters and termination reason;
12. finalists, unresolved trade-offs, and holdout status;
13. explicit statement that final promotion/package is caller-owned;
14. commands actually executed and their outcomes;
15. residual uncertainty and unsupported claims avoided.

Use `measured` only for executed validators/evaluators supplied to the search. Use `derived` for deterministic calculations over measured/supplied evidence, `planned` for requests not yet executed, and `unknown` when evidence is unavailable.

## Stop conditions

Stop or return a bounded result when baseline/evaluator identities are unavailable or drifted; hard-gate semantics are absent; candidate generation/evaluation is required but no caller interface exists; protected/evaluator-only assets would be exposed improperly; candidate lineage is cyclic or identity-inconsistent; the only way to continue is to weaken a gate or mutate evaluator evidence; the search budget is exceeded; or final promotion would require authority this skill does not own.
