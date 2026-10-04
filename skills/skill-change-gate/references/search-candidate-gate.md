# Search Candidate Gate

Use when a caller submits one candidate produced by multi-candidate/evolution search. The gate remains stateless and candidate-local.

Require search-candidate-context v3 for current search integrations. Record search/candidate identity, base and donor parents, operator, transformation ids, deterministic request signature, generation receipt, and frozen evaluator/scenario/policy identity. Validate with `scripts/validate_search_candidate_context.py` and verify the actual candidate bytes correspond to the supplied identity.

## Search-specific evidence rules

A candidate does not pass because peers are worse, it is novel, or it is on a Pareto frontier. Ranking/survivor selection belong to the search controller.

Track evaluator role and exposure separately from evaluator hash. Repeated adaptive selection against the same evaluator makes that evaluator selection evidence, not fresh holdout evidence, even if its bytes remain unchanged. When final promotion requires a holdout, require fresh independent holdout evidence or return gather-evidence/insufficient-evidence for that claim.

Do not let search lineage or novelty waive blocking regressions. Gate each finalist independently against the same applicable quality/safety/portability rules.

For exported-contract changes, an ecosystem-safe claim additionally requires known-consumer evidence; search success never proves consumer compatibility.

Return accept/reject/repair/gather-evidence with candidate-local findings. Do not choose winners, continue generations, promote, or package candidates.

The v3 search input contract remains declared in `contracts/integration-manifest.json`; Gate Context v1 is a separate optional decision-evidence envelope and does not replace search lineage.
