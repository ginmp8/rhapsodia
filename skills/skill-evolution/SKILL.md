---
name: skill-evolution
description: "use when explicitly invoked as the multi-candidate search controller, or when an optimization orchestrator hands off a frozen evolutionary-search contract for an existing Agent Skills-compatible skill; controls reproducible champion-challenger search, identity-bound lineage, validated transformation recombination/backcross, noise-aware Pareto selection, derived novelty/diversity, deterministic stagnation/checkpoints, and finalist selection. Do not auto-own ordinary single-candidate optimization, net-new skill creation, target mutation, benchmark semantics, acceptance gates, or final promotion/package decisions."
---

# Skill Evolution

## Mission

Control evidence-guided multi-candidate search without becoming a second optimizer, benchmark, harness, or promotion gate. Treat baseline, capability/hypothesis/transformation identities, evaluator identities, gates, objectives, interfaces, and budgets as frozen search inputs. Request candidate generation from the caller, compare only identity-compatible evidence, preserve lineage and negative evidence, and return finalists for an external promotion decision.

## Authority boundary

Own only:

- population/search state and candidate lifecycle;
- parent/donor lineage and generation-receipt consistency;
- recombination/backcross/repair-crossover planning;
- hard-gate-first Pareto/non-dominance selection;
- derived novelty/diversity preservation;
- search budget, deterministic stagnation, checkpoint chain, and termination;
- finalist selection and promotion recommendation.

Do not own:

- broad specialist discovery/orchestration;
- direct target-byte mutation;
- mutation implementation;
- evaluator/benchmark/scenario semantics;
- evaluator/threshold edits;
- candidate acceptance gates;
- target or workflow-policy promotion;
- final package/install delivery.

The caller supplies mutation/evaluation interfaces and remains final promotion owner.

## Required inputs

Before search, resolve a **v2 search contract** containing:

1. immutable target/baseline identity and target class;
2. stable ids for capability map, hypothesis pool, and transformation registry;
3. frozen mutation/evaluation interface ids;
4. bounded budget;
5. hard gates;
6. objective directions and predeclared `min_delta` values;
7. frozen evaluator/scenario/evaluation-policy identity;
8. allowed evaluation levels/operators;
9. canonical/preserved roles;
10. derived selection/novelty policy;
11. capability invariants;
12. transformation registry with status, dependencies, conflicts, capability effects, invariant violations, and optional deficit addresses.

Use [assets/templates/search-contract.json.template](assets/templates/search-contract.json.template). Validate before any mutation request:

```text
<PYTHON> scripts/validate_search_contract.py <SEARCH_CONTRACT.json>
```

Do not silently continue a v1 search as v2. Read [references/search-model.md](references/search-model.md) for re-baseline rules.

## Search modes

- `plan-only`: validate inputs and emit bounded candidate/recombination requests; no mutation/evaluation claims.
- `search`: caller-mediated multi-candidate search with validated requests/evidence.
- `resume`: continue only after latest state checkpoint verifies.
- `selection-only`: select from already evaluated identity-compatible candidates.
- `validation-only`: validate contract/state/request/checkpoint integrity without changing search state.

Default to `search` only when caller mutation/evaluation interfaces are actually available. Otherwise use the narrow safe mode and state the limitation.

## Progressive loading

Load only what the active stage needs:

- [references/search-model.md](references/search-model.md): lifecycle, v2 freeze, population, deterministic stagnation, and cost control.
- [references/candidate-and-lineage-contract.md](references/candidate-and-lineage-contract.md): candidate identity, parent/donor semantics, receipt and lineage invariants.
- [references/recombination-contract.md](references/recombination-contract.md): transformation compatibility and candidate-request v2.
- [references/selection-and-pareto.md](references/selection-and-pareto.md): evaluator compatibility, uncertainty/min-delta dominance, canonical preservation, derived novelty.
- [references/evaluation-and-promotion.md](references/evaluation-and-promotion.md): evidence identity, ladder, holdout, and external promotion boundary.
- [references/state-integrity-and-resume.md](references/state-integrity-and-resume.md): checkpoint hashes, receipt chain, resume, and stagnation validation.
- [references/host-portability.md](references/host-portability.md): portable-core runtime handling.
- [assets/templates/search-state.json.template](assets/templates/search-state.json.template): v2 state shape.
- [assets/templates/search-report.md.template](assets/templates/search-report.md.template): durable report skeleton.
- [scripts/validate_search_state.py](scripts/validate_search_state.py): lineage, receipts, transformation sets, evaluation identity, budget, and finalist validation.
- [scripts/validate_candidate_request.py](scripts/validate_candidate_request.py): deterministic pre-mutation request gate.
- [scripts/select_survivors.py](scripts/select_survivors.py): hard-gate-first, min-delta/uncertainty-aware Pareto selection and derived diversity.
- [scripts/plan_recombination.py](scripts/plan_recombination.py): dependency/conflict/invariant-aware deterministic planning.
- [scripts/checkpoint_search_state.py](scripts/checkpoint_search_state.py): state hash-chain receipt and deterministic stagnation/resume checks.
- [evals/activation-scenarios.json](evals/activation-scenarios.json): planned activation/boundary scenarios; never behavioral proof until executed.

## Workflow

### 1. Freeze and validate search inputs

Freeze every required identity before candidate mutation. Validate the v2 contract. If evaluator identity, capability/hypothesis/transformation identity, interface identity, hard gates, or objective policy can drift mid-search, stop and re-baseline rather than pretending results are comparable.

### 2. Seed a deliberately small population

When evidence supports them, use up to four roles:

1. `canonical` — caller's normal canonical optimization result;
2. `evidence-driven` — alternate evidence-backed hypothesis selection;
3. `focused` — most material diagnosed weakness;
4. `novel-bounded` — materially different but contract-safe strategy.

Do not invent transformations to fill slots. Preserve the immutable baseline separately from active candidates.

### 3. Validate every generation request before mutation

A candidate request identifies one physical base, optional donors, exact transformation ids, expected capability effects, causal reason, and deterministic request signature.

For model-authored requests run:

```text
<PYTHON> scripts/validate_candidate_request.py \
  --contract <SEARCH_CONTRACT.json> \
  --state <SEARCH_STATE.json> \
  --request <CANDIDATE_REQUEST.json>
```

Reject unknown/rejected transformations, dependency gaps, conflicts, capability-invariant violations, duplicate base+transformation strategies, parent errors, effect mismatches, or budget overflow before calling the mutation owner.

### 4. Bind generated candidates to receipts

The mutation owner returns immutable candidate identity plus a generation receipt. Record the receipt summary in state and require it to match candidate identity, base, donors, operator, and transformation set. A changed candidate byte identity creates a new candidate; never rewrite history.

### 5. Evaluate cheaply and comparably

Use the caller's ladder:

`L0 structural -> L1 deterministic -> L2 focused -> optional L3 harness -> optional L4 benchmark -> promotion-only L5 holdout`

Record evaluator/scenario/policy identity on every evaluation. Do not compare peers whose deciding evidence identity differs. Keep evidence labels truthful; search cannot upgrade `supplied` evidence to `measured`.

### 6. Select survivors without fake precision

Run:

```text
<PYTHON> scripts/select_survivors.py \
  --contract <SEARCH_CONTRACT.json> \
  --state <SEARCH_STATE.json>
```

The selector:

1. rejects incompatible evaluation identity/evidence;
2. applies hard gates;
3. computes dominance using predeclared `min_delta + uncertainty(A) + uncertainty(B)`;
4. keeps non-dominated alternatives;
5. preserves configured comparator roles when eligible;
6. derives novelty from transformation-set Jaccard distance rather than accepting a model-authored novelty score;
7. uses lower uncertainty then stable candidate id as deterministic tie-breaks.

Never invent a weighted global winner after observing candidate results.

### 7. Recombine only validated semantic transformations

Use `scripts/plan_recombination.py` for deterministic merge/backcross/repair proposals. Recombination must resolve dependency closure and reject conflicts/invariant violations before producing requests. Never merge raw file diffs.

Model judgment may decide **which causal experiment is worth trying**; mechanics decide whether the request is structurally admissible.

### 8. Validate state and checkpoint each completed round

After integrating generation/evaluation results, run:

```text
<PYTHON> scripts/validate_search_state.py \
  --contract <SEARCH_CONTRACT.json> \
  --state <SEARCH_STATE.json>
```

Then create the round checkpoint described in [references/state-integrity-and-resume.md](references/state-integrity-and-resume.md). The receipt hashes exact contract/state content, chains to the previous receipt, and mechanically verifies the stagnation counter.

### 9. Stop when further search is unjustified

Stop on the first applicable condition:

- sufficient finalists have promotion-level evidence;
- total candidate budget is exhausted;
- checkpoint-derived stagnation reaches the configured threshold;
- no new evidence-backed compatible request remains;
- all remaining strategies fail hard gates or duplicate existing strategies;
- evaluator sensitivity cannot distinguish candidates reliably;
- continuation would require evaluator/threshold drift or holdout leakage.

Budget is a ceiling, not a target.

### 10. Use holdout only for finalists when required

If holdout feedback is revealed for repair, mark it `revealed-development`; it is no longer blind evidence. Require a fresh unseen holdout for a later blind promotion claim.

### 11. Return finalists; never self-promote

Return search identity, frozen inputs, complete lineage/receipts, evaluation compatibility, gate eliminations, Pareto archive, derived diversity decisions, recombination decisions, checkpoint chain, termination reason, finalists, unresolved trade-offs, evidence level/holdout status, and one caller-facing recommendation:

- `promote-candidate`;
- `keep-baseline`;
- `gather-evidence`;
- `no-single-winner`.

The caller independently reruns final gates and owns freeze/package/promotion.

## Selection and integrity invariants

- frozen search/evaluator identities never drift mid-search;
- hard-gate failure cannot be compensated by another metric;
- baseline and direct parent remain distinct roles;
- canonical comparator remains available when configured and eligible;
- state/history is append-only except lifecycle/status fields;
- candidate ids are never reused and lineage is acyclic;
- generation receipt matches candidate provenance claims;
- transformation dependencies/conflicts/invariants are mechanically enforced;
- no arbitrary novelty score controls survival;
- request/state checkpoint hashes are deterministic over canonical JSON;
- holdout exposure changes its evidence status;
- target-level search success never auto-promotes a global workflow policy.

## Output contract

Every substantive run reports:

1. target/baseline/canonical identities and target class;
2. mode, search id, contract/state version, budget, and runtime limits;
3. capability/hypothesis/transformation and mutation/evaluation interface identities;
4. frozen evaluator/scenario/policy/hard-gate identities;
5. initial strategies and all validated/rejected candidate requests;
6. candidate identities, generation receipts, lineage, and transformations;
7. evaluation level/evidence identity per candidate;
8. hard-gate eliminations and incompatible evidence;
9. Pareto archive, min-delta/uncertainty treatment, and derived novelty decisions;
10. recombination/backcross/repair decisions and deterministic skips;
11. checkpoint/state hashes, receipt chain, stagnation counter, and termination reason;
12. finalists, unresolved trade-offs, holdout status, and caller recommendation;
13. commands actually executed and outcomes;
14. residual uncertainty and unsupported claims avoided;
15. explicit statement that final acceptance/freeze/package remains caller-owned.

Use `measured` only for executed evaluator/tool evidence. Use `derived` for deterministic calculations over supplied/measured inputs, `supplied` for caller results not rerun here, `planned` for unexecuted work, and `unknown` when unresolved.

## Stop conditions

Stop or return a bounded result when frozen identities are absent/drifted; hard-gate/objective semantics are missing; mutation/evaluation interfaces are unavailable for `search`; v1 state is presented as a v2 resume without explicit re-baseline; a candidate receipt/evaluator identity/lineage is inconsistent; a request requires dependency/conflict/invariant violations; checkpoint verification fails; search budget/stagnation is exhausted; holdout blindness would be violated; the only continuation path weakens a gate; or final promotion would require authority this skill does not own.
