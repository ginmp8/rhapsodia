---
name: skill-evolution
description: "use when explicitly invoked as the multi-candidate search controller, or when an optimization orchestrator hands off a frozen evolutionary-search contract for an existing agent skills-compatible skill; controls reproducible champion-challenger search, identity-bound lineage/provenance, validated semantic recombination/backcross, evidence-aware pareto and scenario-specialist selection, derived diversity, deterministic semantic stagnation/checkpoints, and finalist selection. do not use for ordinary single-candidate optimization, net-new skill creation, direct target mutation, evaluator/benchmark/harness semantics, candidate acceptance gates, or final promotion, packaging, or installation."
---

# Skill Evolution

## Mission

Control evidence-guided multi-candidate search without becoming a second optimizer, benchmark, harness, or promotion gate. Treat baseline, capability/hypothesis/transformation identities, evaluator identities, gates, objectives, interfaces, and budgets as frozen search inputs. Request candidate generation from the caller, compare only identity-compatible evidence, preserve lineage and negative evidence, and return finalists for an external promotion decision.

## Scope

Use only after evolutionary search is explicitly selected for an existing skill and a valid frozen search contract is supplied, or when Skill Evolution is explicitly invoked for that controller role. Operate on search metadata, candidate/evaluation envelopes, lineage, selection, recombination plans, checkpoints, and finalist recommendations. Do not mutate target bytes, design evaluators, own acceptance gates, or perform final package/install delivery.

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

Before search, resolve a **v4 search contract** containing:

1. immutable target/baseline identity and target class;
2. stable ids for capability map, hypothesis pool, and transformation registry;
3. stable ids for the evaluation plan plus frozen mutation/evaluation interface ids;
4. bounded budget;
5. hard gates;
6. objective directions and predeclared `min_delta` values;
7. frozen evaluator/scenario/evaluation-policy identity;
8. allowed evaluation levels/operators;
9. canonical/preserved roles;
10. derived selection/novelty policy;
11. frozen finalist policy with the minimum evaluation level and holdout requirement;
12. capability invariants;
13. transformation registry with status, dependencies, conflicts, capability effects, invariant violations, and optional deficit addresses;
14. when richer evidence is available, frozen uncertainty semantics, required evaluation slices, stability policy, scenario-frontier policy, behavior-descriptor identity, and complexity limits;
15. an optional deterministic stagnation policy.

Use [assets/templates/search-contract.json.template](assets/templates/search-contract.json.template) for the compatibility profile. Prefer [assets/templates/search-contract-evidence-aware.json.template](assets/templates/search-contract-evidence-aware.json.template) when the caller can supply the richer evidence it requires. The evidence-aware profile is an additive **extension profile v1** carried inside an otherwise-valid search-contract v4; it does not redefine the v4/v2 public surfaces.

Always validate canonical compatibility first:

```text
<PYTHON> scripts/validate_search_contract.py <SEARCH_CONTRACT.json>
```

When `evidence_aware` is present, also run:

```text
<PYTHON> scripts/validate_evidence_aware_search_contract.py <SEARCH_CONTRACT.json>
```

Never silently make extension controls mandatory for a legacy v4 caller.

Do not silently continue a v1/v2/v3 search as v4. Read [references/search-model.md](references/search-model.md) for re-baseline rules.

## Search modes

- `plan-only`: validate inputs and emit bounded candidate/recombination requests; no mutation/evaluation claims.
- `search`: caller-mediated multi-candidate search with validated requests/evidence.
- `resume`: continue only after latest state checkpoint verifies.
- `selection-only`: select from already evaluated identity-compatible candidates.
- `validation-only`: validate contract/state/request/checkpoint integrity without changing search state.

Default to `search` only when caller mutation/evaluation interfaces are actually available. Otherwise use the narrow safe mode and state the limitation.

### Package self-validation

Run the package validator during preflight when package integrity is material, for every `validation-only` request, and again after any edit to this skill before claiming it is ready for integration:

```text
<PYTHON> scripts/validate_skill_evolution.py --target <SKILL_EVOLUTION_ROOT>
```

This gate validates the declared integration manifest and all declared public surfaces, including v4 search/state and v2 candidate-request/evaluation. A missing or invalid declared surface blocks readiness; do not substitute generic package validation for this skill-specific gate.

## Progressive loading

Load only what the active stage needs:

- [references/search-model.md](references/search-model.md): lifecycle, v4 freeze, population, deterministic stagnation, and cost control.
- [references/candidate-and-lineage-contract.md](references/candidate-and-lineage-contract.md): candidate identity, parent/donor semantics, receipt and lineage invariants.
- [references/recombination-contract.md](references/recombination-contract.md): transformation compatibility and candidate-request v2.
- [references/selection-and-pareto.md](references/selection-and-pareto.md): evaluator compatibility, evidence eligibility, uncertainty/stability, aggregate Pareto plus scenario specialists, complexity, and derived diversity.
- [references/evaluation-and-promotion.md](references/evaluation-and-promotion.md): evidence identity, repeated/stochastic evidence metadata, evaluation slices, ladder, holdout, and external promotion boundary.
- [references/state-integrity-and-resume.md](references/state-integrity-and-resume.md): checkpoint hashes, receipt chain, resume, legacy/semantic stagnation, behavior signatures, and deficit coverage.
- [references/host-portability.md](references/host-portability.md): capability-first portable-core runtime handling across Agent Skills-compatible hosts.
- [references/evidence-aware-profile.md](references/evidence-aware-profile.md): extension profile v1, typed stochastic evidence, scenario specialists, behavior diversity, provenance, and semantic stagnation without changing canonical v4/v2 surfaces.
- `contracts/integration-manifest.json`: declares the versioned contracts this controller owns plus the external generation-receipt contract it accepts, enabling orchestrator impact analysis without duplicating peer schemas.
- [assets/templates/candidate-evaluation.json.template](assets/templates/candidate-evaluation.json.template): compatibility example for normalized candidate-evaluation v2 envelopes.
- [assets/templates/candidate-evaluation-evidence-aware.json.template](assets/templates/candidate-evaluation-evidence-aware.json.template): v2 evidence-aware example with typed uncertainty metadata, slices, stability, scenario scores, and behavior descriptors.
- [assets/templates/search-state-evidence-aware.json.template](assets/templates/search-state-evidence-aware.json.template): coherent v4 state example for the evidence-aware profile.
- [scripts/validate_candidate_evaluation.py](scripts/validate_candidate_evaluation.py): validates normalized evaluator identity, hard gates, metrics, uncertainty, level, and holdout status against the frozen search contract.
- [scripts/validate_evidence_aware_candidate_evaluation.py](scripts/validate_evidence_aware_candidate_evaluation.py): additive profile validation for typed uncertainty metadata, slices, stability, scenario scores, and behavior descriptors.
- [assets/templates/search-state.json.template](assets/templates/search-state.json.template): v4 state shape.
- [assets/templates/search-report.md.template](assets/templates/search-report.md.template): durable report skeleton.
- [scripts/validate_search_state.py](scripts/validate_search_state.py): lineage, receipts, transformation sets, evaluation identity, budget, and finalist validation.
- [scripts/validate_candidate_request.py](scripts/validate_candidate_request.py): canonical deterministic pre-mutation request gate.
- [scripts/validate_evidence_aware_candidate_request.py](scripts/validate_evidence_aware_candidate_request.py): extension provenance/address validation when the evidence profile is active.
- [scripts/select_survivors.py](scripts/select_survivors.py): canonical v4 survivor selector.
- [scripts/select_survivors_evidence_aware.py](scripts/select_survivors_evidence_aware.py): extension selector for evaluated pools, slices, stability, complexity, scenario specialists, and behavior diversity.
- [scripts/plan_recombination.py](scripts/plan_recombination.py): dependency/conflict/invariant-aware deterministic planning.
- [scripts/checkpoint_search_state.py](scripts/checkpoint_search_state.py): canonical state hash-chain receipt and transformation-signature stagnation checks.
- [scripts/checkpoint_search_state_evidence_aware.py](scripts/checkpoint_search_state_evidence_aware.py): extension checkpoint for deterministic behavior/deficit-aware stagnation.
- `scripts/_common.py`: import-only standard-library helper shared by bundled validators/planners; it is not a user-facing CLI.
- [evals/activation-scenarios.json](evals/activation-scenarios.json): planned activation/boundary scenarios; never behavioral proof until executed.

## Workflow

### 1. Freeze and validate search inputs

Freeze every required identity before candidate mutation. Validate the v4 contract. If evaluator identity, capability/hypothesis/transformation identity, interface identity, hard gates, or objective policy can drift mid-search, stop and re-baseline rather than pretending results are comparable.

### 2. Seed a deliberately small population

When evidence supports them, use up to four roles:

1. `canonical` — caller's normal canonical optimization result;
2. `evidence-driven` — alternate evidence-backed hypothesis selection;
3. `focused` — most material diagnosed weakness;
4. `novel-bounded` — materially different but contract-safe strategy.

Do not invent transformations to fill slots. Preserve the immutable baseline separately from active candidates.

### 3. Validate every generation request before mutation

A candidate request identifies one physical base, optional donors, exact transformation ids, expected capability effects, causal reason, and deterministic request signature. It may also carry `hypothesis_ids` and `deficit_ids`; every declared deficit must be covered by the selected transformations' frozen `addresses` metadata. Provenance fields do not let this controller invent or mutate the hypothesis pool/registry.

For model-authored requests always run the canonical gate:

```text
<PYTHON> scripts/validate_candidate_request.py \
  --contract <SEARCH_CONTRACT.json> \
  --state <SEARCH_STATE.json> \
  --request <CANDIDATE_REQUEST.json>
```

When the evidence-aware profile is active, additionally run `scripts/validate_evidence_aware_candidate_request.py` with the same arguments. Reject unknown/rejected transformations, dependency gaps, conflicts, capability-invariant violations, unsupported deficit provenance, duplicate base+transformation strategies, parent errors, effect mismatches, or budget overflow before calling the mutation owner.

### 4. Bind generated candidates to receipts

The mutation owner returns immutable candidate identity plus a generation receipt. Record the receipt summary in state and require it to match candidate identity, base, donors, operator, and transformation set. A changed candidate byte identity creates a new candidate; never rewrite history.

### 5. Evaluate cheaply and comparably

Use the caller's ladder:

`L0 structural -> L1 deterministic -> L2 focused -> optional L3 harness -> optional L4 benchmark -> promotion-only L5 holdout`

Record evaluator/scenario/policy identity on every evaluation. Do not compare peers whose deciding evidence identity differs. Keep evidence labels truthful; search cannot upgrade `supplied` evidence to `measured`.

When the frozen contract enables extension profile v1, require the evaluator-normalized v2 envelope to carry the configured statistics/uncertainty semantics, required evaluation slices, stability evidence, scenario scores, and behavior descriptor. Validate the envelope with the canonical candidate-evaluation v2 validator and `scripts/validate_evidence_aware_candidate_evaluation.py`. The controller validates/filters those fields but never computes bootstrap trials, calibrates judges, defines scenario semantics, or changes thresholds after seeing results.

### 6. Validate state, then select survivors without fake precision

Before selection, validate the integrated generation/evaluation state with the canonical validator. When extension profile v1 is active, also run `scripts/validate_evidence_aware_search_state.py` with the same inputs.

```text
<PYTHON> scripts/validate_search_state.py \
  --contract <SEARCH_CONTRACT.json> \
  --state <SEARCH_STATE.json>
```

Use `scripts/select_survivors.py` for the compatibility profile. Use `scripts/select_survivors_evidence_aware.py` when extension profile v1 is active.

The selector also validates state defensively, then:

1. builds the comparison pool from evaluated `evaluating`, `active`, and `finalist` candidates;
2. rejects incompatible evaluation identity/evidence and unexecuted/ineligible evidence;
3. eliminates `blind-fail` holdout results;
4. applies hard gates, then configured required-slice, stability, and complexity eligibility controls;
5. compares Pareto dominance only within the same frozen evaluation level;
6. computes dominance using predeclared `min_delta + uncertainty(A) + uncertainty(B)`;
7. optionally augments aggregate Pareto with same-level scenario specialists under the frozen scenario-frontier policy;
8. keeps configured comparator roles when eligible;
9. derives diversity from frozen behavior labels when configured, otherwise transformation-set Jaccard distance; never accept a model-authored novelty score.

Never invent a weighted global winner after observing candidate results. Scenario specialists expand exploration only; they do not bypass gates or finalist policy.

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

Then create the round checkpoint. Use canonical `scripts/checkpoint_search_state.py` for the compatibility profile. When extension profile v1 is active, use `scripts/checkpoint_search_state_evidence_aware.py`; its receipt still hashes the exact original v4 contract/state content, chains to the previous receipt, records transformation/behavior/deficit signatures, and mechanically verifies the stagnation counter. Under semantic stagnation, transformation-only novelty does not reset the counter unless it produces a configured behavior or deficit-coverage signal. See [references/evidence-aware-profile.md](references/evidence-aware-profile.md).

### 9. Stop when further search is unjustified

Stop on the first applicable condition:

- sufficient finalists satisfy the frozen finalist policy and have promotion-level evidence;
- total candidate budget is exhausted;
- checkpoint-derived stagnation reaches the configured threshold;
- no new evidence-backed compatible request remains;
- all remaining strategies fail hard gates or duplicate existing strategies;
- evaluator sensitivity cannot distinguish candidates reliably;
- continuation would require evaluator/threshold drift or holdout leakage.

Budget is a ceiling, not a target.

### 10. Enforce the frozen finalist policy

A candidate may enter `finalists` only when its evaluation level meets or exceeds `finalist_policy.minimum_evaluation_level`, its evidence type is selection-eligible, every hard gate passes, and any configured blind-holdout requirement is satisfied. If holdout feedback is revealed for repair, mark it `revealed-development`; it is no longer blind evidence and cannot satisfy `blind-pass-required`. Require a fresh unseen holdout for a later blind promotion claim.

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
- finalist status/list membership and sufficient-finalist termination are valid only when the frozen finalist policy is satisfied;
- baseline and direct parent remain distinct roles;
- canonical comparator remains available when configured and eligible;
- state/history is append-only except lifecycle/status fields;
- candidate ids are never reused and lineage is acyclic;
- generation receipt matches candidate provenance claims;
- transformation dependencies/conflicts/invariants and declared deficit-address coverage are mechanically enforced;
- transformation-registry identity remains frozen for the search; a registry revision requires re-baseline;
- no arbitrary novelty score controls survival; behavior-based novelty uses a frozen descriptor identity;
- optional uncertainty/stability/scenario/complexity policies are frozen before results and never inferred post-hoc;
- request/state checkpoint hashes and semantic signatures are deterministic over canonical data;
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
7. evaluation level/evidence identity per candidate plus configured statistics/uncertainty semantics;
8. incompatible/ineligible evidence and eliminations by holdout, hard gate, required slice, stability, and complexity;
9. aggregate Pareto archive, scenario specialists when configured, min-delta/uncertainty treatment, and derived diversity decisions;
10. candidate hypothesis/deficit provenance plus recombination/backcross/repair decisions and deterministic skips;
11. checkpoint/state hashes, receipt chain, stagnation policy, behavior/deficit signatures, stagnation counter, and termination reason;
12. finalists, unresolved trade-offs, holdout status, and caller recommendation;
13. commands actually executed and outcomes;
14. residual uncertainty and unsupported claims avoided;
15. explicit statement that final acceptance/freeze/package remains caller-owned.

Use `measured` only for executed evaluator/tool evidence. Use `derived` for deterministic calculations over supplied/measured inputs, `supplied` for caller results not rerun here, `planned` for unexecuted work, and `unknown` when unresolved.

## Stop conditions

Stop or return a bounded result when frozen identities are absent/drifted; hard-gate/objective semantics are missing; mutation/evaluation interfaces are unavailable for `search`; v1/v2/v3 state is presented as a v4 resume without explicit re-baseline; a candidate receipt/evaluator identity/lineage is inconsistent; a request requires dependency/conflict/invariant violations; checkpoint verification fails; search budget/stagnation is exhausted; holdout blindness would be violated; the only continuation path weakens a gate; or final promotion would require authority this skill does not own.


## Integration contract changes

Treat every declared export/import version as public integration surface. A schema, required-input, request, receipt, or state change that affects a declared surface requires an explicit version decision and caller-side impact gate. Do not rely on internal tests alone to claim ecosystem compatibility.
