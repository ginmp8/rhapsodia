# Search Candidate Gate

Use when a caller submits a candidate produced inside a multi-candidate/evolution search. The gate remains stateless and candidate-local.

For current evolutionary-search integrations require search-candidate-context v3. Record `search_id`, `candidate_id`, candidate identity, base parent, donor parent ids, operator, transformation ids, deterministic request signature, generation-receipt identity, and frozen evaluator/scenario/policy identity. Validate the envelope with `scripts/validate_search_candidate_context.py` before interpreting candidate-local evidence. Verify that the candidate bytes correspond to the supplied candidate identity and that the claimed transformations/parent identities are not contradicted by the receipt.

Apply the normal hard-gate policy independently. A candidate does not pass because its peers are worse, because it is novel, or because it is on a Pareto frontier. Novelty and survivor selection belong to the search controller.

Return accept/reject/repair/gather-evidence to the caller with candidate-local findings. Do not select the winner or promote/package the candidate.


The v3 input contract is declared in `contracts/integration-manifest.json`. This gate still owns only candidate-local acceptance; it must not absorb population selection or peer orchestration.
