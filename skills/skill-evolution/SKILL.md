---
name: skill-evolution
description: "use when explicitly invoked to control bounded multi-candidate/evolutionary search for one existing Agent Skills-compatible skill, or when an optimizer hands off a frozen search contract; owns search state, lineage/provenance, validated semantic recombination/backcross, hard-gate-first Pareto/scenario-specialist selection, derived diversity/stagnation, checkpoints, and finalist recommendation. do not use for single-candidate optimization, skill creation, target mutation, evaluator/benchmark/harness design, acceptance gates, or final promotion, packaging, or installation."
---

# Skill Evolution

## Mission and activation boundary

Control evidence-guided multi-candidate search for one existing skill without becoming a second optimizer, evaluator, benchmark, harness, mutation owner, acceptance gate, or promotion authority.

Use only when evolutionary search is explicitly selected or a caller hands off a valid frozen search contract. Operate on search metadata/state, candidate/evaluation envelopes, lineage, selection, semantic recombination plans, checkpoints, termination, and finalist recommendations.

Do not use for ordinary single-candidate optimization, net-new skill creation, direct target edits, evaluator/scenario/threshold design, benchmark/harness semantics, final acceptance, freeze, packaging, installation, or workflow-policy promotion.

## Authority boundary

Own only:
- population/search state, candidate lifecycle, lineage, receipt consistency, and checkpoint chain;
- dependency/conflict/invariant-aware recombination/backcross/repair-crossover planning;
- hard-gate-first Pareto/non-dominance selection, scenario specialists, and derived diversity;
- bounded budgets, deterministic stagnation/termination, finalist selection, and caller-facing recommendation.

Do not own:
- broad specialist orchestration, hypothesis/transformation-registry invention, or target-byte mutation;
- evaluator/benchmark/scenario/statistical semantics, threshold changes, or acceptance-gate decisions;
- final target/workflow promotion, freeze, package, install, or delivery.

The caller supplies frozen mutation/evaluation interfaces, performs candidate generation/evaluation, and remains final promotion owner.

## Search modes

- `plan-only`: validate inputs and emit bounded candidate/recombination requests; no mutation/evaluation claims.
- `search`: caller-mediated multi-candidate search with validated requests and identity-compatible evidence.
- `resume`: continue only after the latest checkpoint and frozen identities verify.
- `selection-only`: select from already evaluated, identity-compatible candidates.
- `validation-only`: validate contract/state/request/checkpoint/package integrity without advancing search.

Default to `search` only when caller mutation and evaluation interfaces are available; otherwise choose the narrowest safe mode and state the limitation.

## Quick-start workflow

1. Freeze the v4 search contract, baseline/target, capability/hypothesis/transformation registries, mutation/evaluation interfaces, evaluator/scenario/policy, hard gates, objectives, finalist policy, and finite budget; validate before any request.
2. Seed a deliberately small evidence-backed population; keep immutable baseline and configured canonical comparator distinct from active candidates.
3. Validate every candidate request before mutation; reject unknown/rejected transformations, dependency/conflict/invariant violations, effect/provenance mismatches, duplicates, parent errors, and budget overflow.
4. Bind generated candidate bytes to immutable identity plus generation receipt; changed bytes create a new candidate and never rewrite lineage/history.
5. Evaluate with the caller's frozen ladder and identity; compare only compatible evidence and never upgrade `supplied` evidence to `measured`.
6. Validate state, apply hard gates before Pareto/scenario-specialist/diversity selection, and recombine only validated semantic transformations — never raw file diffs.
7. Checkpoint each completed round, derive stagnation deterministically, and stop on finalist sufficiency, budget, stagnation, no admissible experiment, indistinguishable evidence, or required policy/evaluator drift.
8. Enforce the frozen finalist policy, return finalists plus lineage/evidence/trade-offs and `promote-candidate|keep-baseline|gather-evidence|no-single-winner`; never self-promote.

## Critical invariants

- Frozen search, evaluator/scenario/policy, transformation-registry, interface, gate, objective, and finalist identities never drift mid-search; drift requires explicit re-baseline.
- Hard-gate failure cannot be compensated by another metric, scenario-specialist status, diversity, or aggregate score.
- Finalist membership and sufficient-finalist termination are valid only when the frozen finalist policy is satisfied at the required evaluation/holdout level.
- Baseline, canonical comparator, and direct parent remain distinct roles; preserve configured comparator roles when eligible.
- State/history is append-only except declared lifecycle/status fields; candidate ids are never reused and lineage is acyclic.
- Generation receipts must match candidate identity, base parent, donors, operator, and transformation set.
- Transformation dependencies/conflicts/capability invariants and declared deficit-address coverage are mechanically enforced before mutation.
- Selection compares only compatible evidence at the same frozen evaluation level; never invent a weighted global winner after observing results.
- Novelty/diversity is derived from frozen behavior descriptors when configured, otherwise deterministic transformation-set distance; never accept model-authored novelty scores.
- Optional uncertainty, slices, stability, scenario-frontier, complexity, and semantic-stagnation policies are frozen before results and never inferred post-hoc.
- Checkpoint/request hashes and semantic signatures are deterministic over canonical data; transformation-only novelty cannot reset semantic stagnation when the profile forbids it.
- Holdout exposure changes evidence status; revealed holdout feedback cannot satisfy a blind-pass requirement without a fresh unseen holdout.
- Preserve negative/rejected evidence, gate eliminations, and lineage history needed to explain search decisions; do not erase failed candidates to make the search look cleaner.
- Budget is a ceiling, not a target; target-level search success never auto-promotes workflow policy.
- Public integration-surface changes require an explicit version decision and caller-side impact gate; local tests alone do not prove ecosystem compatibility.

## Required search contract

Before search, require a valid **search-contract v4** with immutable target/baseline and target class; stable capability/hypothesis/transformation/evaluation/interface identities; finite budget; hard gates; objective directions and predeclared `min_delta`; allowed levels/operators; preserved roles; selection/novelty/finalist policies; capability invariants; and transformation status/dependencies/conflicts/effects/violations/optional deficit addresses.

Use the compatibility profile by default. Enable `evidence_aware` extension profile v1 only when the caller already supplies its frozen uncertainty, required-slice, stability, scenario-frontier, behavior-descriptor, complexity, and optional semantic-stagnation semantics; the extension must remain valid under canonical v4/v2 validators.

Validate canonical compatibility first, then the evidence-aware validator when active. Never reinterpret v1/v2/v3 state as v4 or silently make extension controls mandatory for a legacy v4 caller.

## Direct resource map

- [references/search-model.md](references/search-model.md): lifecycle, v4 freeze/re-baseline, population, budgets, and stagnation.
- [references/candidate-and-lineage-contract.md](references/candidate-and-lineage-contract.md): candidate identity, parent/donor semantics, receipts, and lineage invariants.
- [references/recombination-contract.md](references/recombination-contract.md): transformation compatibility and candidate-request v2.
- [references/selection-and-pareto.md](references/selection-and-pareto.md): evidence eligibility, Pareto/scenario-specialist selection, uncertainty/stability/complexity, and diversity.
- [references/evaluation-and-promotion.md](references/evaluation-and-promotion.md): evaluation identity/ladder, stochastic metadata, slices, holdouts, and external promotion boundary.
- [references/state-integrity-and-resume.md](references/state-integrity-and-resume.md): checkpoint hashes/chain, resume, stagnation signatures, and deficit coverage.
- [references/host-portability.md](references/host-portability.md): portable-core capability/runtime behavior across Agent Skills-compatible hosts.
- [references/evidence-aware-profile.md](references/evidence-aware-profile.md): extension profile v1 and its compatibility-preserving evidence/stagnation rules.

## Detailed search-contract fields

The v4 contract contains:

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

Use [assets/templates/search-contract.json.template](assets/templates/search-contract.json.template) for compatibility and [assets/templates/search-contract-evidence-aware.json.template](assets/templates/search-contract-evidence-aware.json.template) only when the richer evidence is available.

Canonical validation:

```text
<PYTHON> scripts/validate_search_contract.py <SEARCH_CONTRACT.json>
```

When `evidence_aware` is present, additionally run:

```text
<PYTHON> scripts/validate_evidence_aware_search_contract.py <SEARCH_CONTRACT.json>
```

Do not silently continue a v1/v2/v3 search as v4. Read [references/search-model.md](references/search-model.md) for re-baseline rules.

## Package self-validation

Run during preflight when package integrity is material, for every `validation-only` request, and after any edit before claiming integration readiness:

```text
<PYTHON> scripts/validate_skill_evolution.py --target <SKILL_EVOLUTION_ROOT>
```

This gate validates package/context structure, the integration manifest, and declared public surfaces including v4 search/state and v2 candidate-request/evaluation. Missing/invalid declared surfaces block readiness.

## Operational resources

Load only what the active stage needs. Templates: `assets/templates/search-state.json.template`, `candidate-evaluation.json.template`, `search-report.md.template`, and evidence-aware variants when that profile is active. Validators/planners/selectors: `validate_candidate_request.py`, `validate_candidate_evaluation.py`, `validate_search_state.py`, `select_survivors.py`, `plan_recombination.py`, `checkpoint_search_state.py`, plus `*_evidence_aware.py` counterparts under the extension profile. `scripts/_common.py` and `_evidence_common.py` are import-only helpers, not user-facing CLIs. `contracts/integration-manifest.json` declares versioned exports/imports. `evals/activation-scenarios.json` is planned activation coverage, never behavioral proof until executed.

## Detailed workflow

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
