# Search Candidate Gate

Use when a caller submits a candidate produced inside a multi-candidate/evolution search. The gate remains stateless and candidate-local.

Record `search_id`, `candidate_id`, direct parent/base parent, donor parent ids when relevant, operator, transformation ids, and lineage/generation receipt identity when supplied. Verify that the candidate bytes correspond to the supplied candidate identity and that the claimed transformations/parent identities are not contradicted by the receipt.

Apply the normal hard-gate policy independently. A candidate does not pass because its peers are worse, because it is novel, or because it is on a Pareto frontier. Novelty and survivor selection belong to the search controller.

Return accept/reject/repair/gather-evidence to the caller with candidate-local findings. Do not select the winner or promote/package the candidate.
