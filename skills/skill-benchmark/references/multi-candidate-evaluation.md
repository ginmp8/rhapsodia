# Multi-Candidate Evaluation

Use when a caller is comparing several skill candidates from the same search. Benchmark remains an evaluator, not a population selector.

## Comparability

For strict peer comparison require the same: baseline identity, evaluator identity/version, scenario set/partition, **evaluation/scoring policy identity**, runtime/model settings when material, and metric definitions. Contract v2 enforces identical metric IDs across candidates; `policy_id` is the frozen identity for the scoring policy/metric definitions. Metric-bearing levels (`L2`-`L5`) require at least one metric. Preserve each candidate's direct parent separately.

## Output envelope

For search/evolution integration emit contract v2 (see `assets/templates/multi-candidate-evidence.json.template`): one record per candidate with `candidate_id`, candidate identity, parent id, baseline id, evaluator/scenario/**policy** ids, metric values with uncertainty where available, and highest ladder level actually executed. Validate the set with `scripts/validate_candidate_set.py`. Legacy v1 remains readable outside evolutionary integration, but v2 is required for identity-comparable search evidence.

Do not rank by an invented weighted score. It is acceptable to report pairwise deltas/non-dominance when mechanically derivable, but the search controller owns survivor selection and diversity policy.


This interface is declared as `skill-opt.benchmark-candidate-evidence` v2 in `contracts/integration-manifest.json`. Contract changes require orchestrator impact analysis rather than silent schema drift.
