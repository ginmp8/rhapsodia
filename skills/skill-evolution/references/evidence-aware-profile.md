# Evidence-Aware Evolution Profile v1

## Purpose

Add stronger research-backed selection and stopping controls without changing the existing search-contract v4, search-state v4, candidate-request v2, or candidate-evaluation v2 public surfaces.

The profile is an additive extension under top-level `evidence_aware`. A profile contract must also remain valid under the canonical v4 validator. This keeps existing orchestrators compatible while allowing callers with richer evaluator evidence to opt in.

Use `assets/templates/search-contract-evidence-aware.json.template` as the coherent example.

## Authority boundary

The profile does not make Skill Evolution an evaluator, benchmark, statistical engine, or mutation owner. External evaluators produce measurements, trials, scenario scores, and behavior labels. The controller validates frozen metadata and applies predeclared mechanics only.

The transformation registry remains frozen for one search identity. Research on self-evolving mutation strategies is intentionally not applied inside a live search because changing the registry would change the search identity and weaken reproducibility. Use a new search/re-baseline for a revised registry.

## Profile contract

`evidence_aware.profile_version` must equal `1`. Optional/required controls in the profile are mapped internally without changing the canonical v4 fields:

- `uncertainty_metadata_required`;
- `required_evaluation_slices`;
- `stability_policy`;
- `frontier_policy`;
- `novelty_policy`;
- `complexity_policy`;
- `stagnation_policy`.

Validate both layers:

```text
<PYTHON> scripts/validate_search_contract.py <SEARCH_CONTRACT.json>
<PYTHON> scripts/validate_evidence_aware_search_contract.py <SEARCH_CONTRACT.json>
```

The first proves compatibility with canonical v4. The second proves the extension semantics.

## Typed stochastic evidence

When `uncertainty_metadata_required=true`, normalized candidate-evaluation v2 evidence must include `statistics` with positive `case_count` and `trial_count`, an explicit `uncertainty_kind`, and any confidence level required by that uncertainty kind. Optional paired-group and scenario-result identities make repeated evidence auditable.

The controller does not calculate intervals or bootstrap results. It only rejects ambiguous/incomplete metadata when the profile requires it.

Use:

```text
<PYTHON> scripts/validate_candidate_evaluation.py --contract <CONTRACT> --evaluation <EVAL>
<PYTHON> scripts/validate_evidence_aware_candidate_evaluation.py --contract <CONTRACT> --evaluation <EVAL>
```

## Evaluation slices

`required_evaluation_slices` protects named regression/capability boundaries from being hidden by aggregate gains. Each required slice must exist in `evaluation.slices`; survivor eligibility requires `pass`.

Slice names and meanings come from the frozen evaluation plan. The controller never invents them after results are observed.

## Stability eligibility

`minimum-win-rate-v1` consumes external stability evidence:

- frozen `method_id`;
- minimum win rate;
- minimum resample count.

Candidate evidence supplies the matching method id, observed win rate, and resample count. The selector filters against the predeclared threshold; it does not perform resampling or best-arm identification itself.

## Aggregate Pareto plus scenario specialists

`aggregate-plus-scenario-elites-v1` preserves aggregate Pareto selection and additionally identifies same-level candidates that are within the frozen `scenario_min_delta` of the best score for individual scenarios.

Scenario elites expand the exploration set only after evidence compatibility and hard eligibility controls. They cannot bypass hard gates, required slices, stability, complexity limits, or finalist policy.

## Behavioral diversity

`behavior-label-jaccard-v1` derives novelty from evaluator-supplied labels bound to a frozen `descriptor_id`. The labels describe behavior; the novelty score itself is deterministic Jaccard distance computed by the controller.

No free-form model-authored novelty score is accepted. Canonical transformation Jaccard remains the v4 compatibility default outside this profile.

## Complexity control

`metric-upper-bounds-v1` applies predeclared upper limits to named objective metrics such as token cost. The external evaluator owns the metric definition. Complexity limits are eligibility constraints, not a license to shorten the skill by deleting required semantics or safety controls.

## Candidate provenance

Evidence-aware candidate request/state validators accept optional:

- `hypothesis_ids`;
- `deficit_ids`.

Every declared deficit must appear in the frozen `addresses` metadata of at least one selected transformation. This creates a deterministic diagnosis-to-transformation link without claiming that the diagnosis or repair is semantically correct.

Run the canonical validator first, then the evidence-profile validator:

```text
<PYTHON> scripts/validate_candidate_request.py --contract <CONTRACT> --state <STATE> --request <REQUEST>
<PYTHON> scripts/validate_evidence_aware_candidate_request.py --contract <CONTRACT> --state <STATE> --request <REQUEST>
```

The same compatibility rule applies to search-state validation.

## Survivor pool

`scripts/select_survivors_evidence_aware.py` may compare fully evaluated candidates in `evaluating`, `active`, or `finalist` states. `max_active_candidates` remains the capacity of the selected survivor set and the canonical active/finalist state limit; it no longer prevents the profile from pruning a larger evaluated pool.

Eligibility order is deterministic:

1. evaluation identity/objective compatibility;
2. evidence type;
3. blind-holdout failure;
4. hard gates;
5. required slices;
6. stability;
7. complexity;
8. aggregate Pareto plus optional scenario specialists;
9. derived diversity and stable tie-breaks.

## Semantic stagnation

Canonical v4 checkpointing remains unchanged. For the profile, `pareto-plus-semantic-signatures-v1` can ignore transformation-only novelty and use configured semantic progress signals:

- new frozen behavior-descriptor signature;
- new transformation-addressed deficit coverage.

`checkpoint_search_state_evidence_aware.py` records transformation signatures, behavior signatures, deficit coverage, the profile stagnation-policy id, and exact contract/state hashes. The first checkpoint requires zero stagnant rounds. Later rounds derive the counter from the previous receipt.

## Profile scripts

- `scripts/validate_evidence_aware_search_contract.py`
- `scripts/validate_evidence_aware_candidate_evaluation.py`
- `scripts/validate_evidence_aware_candidate_request.py`
- `scripts/validate_evidence_aware_search_state.py`
- `scripts/select_survivors_evidence_aware.py`
- `scripts/checkpoint_search_state_evidence_aware.py`
- `scripts/_evidence_common.py` is internal and not a user-facing CLI.

## Compatibility invariant

A valid profile artifact must remain valid under the corresponding canonical v4/v2 validator. If a future enhancement cannot satisfy that rule, create a new major public contract and coordinate consumers rather than smuggling a breaking change through this profile.
