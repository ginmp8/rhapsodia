# Multi-Candidate Evaluation

Use when a caller is comparing several skill candidates from the same search. Benchmark remains an evaluator, not a population selector.

## Comparability

For strict peer comparison require the same: baseline identity, evaluator identity/version, scenario set/partition, scoring contract, runtime/model settings when material, and metric definitions. Preserve each candidate's direct parent separately.

## Output envelope

Return one record per candidate with `candidate_id`, candidate identity, parent id, baseline id, evaluator/scenario ids, hard-gate evidence, metric values, uncertainty/missing evidence, and highest ladder level actually executed.

Do not rank by an invented weighted score. It is acceptable to report pairwise deltas/non-dominance when mechanically derivable, but the search controller owns survivor selection and diversity policy.
