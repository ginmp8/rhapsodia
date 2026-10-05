# Search Candidate Gate

## At a Glance

- **Purpose:** Gate one search/evolution candidate independently of ranking, novelty, or survivor selection.
- **Load when:** The caller supplies a candidate produced by multi-candidate or evolutionary search.
- **Decision impact:** Search lineage never waives blocking regressions; repeated evaluator exposure can invalidate holdout claims, and each finalist still needs candidate-local identity, evidence, portability, safety, and compatibility checks.

## Search-specific evidence rules

A candidate does not pass because peers are worse, it is novel, or it is on a Pareto frontier. Ranking/survivor selection belong to the search controller.

Track evaluator role and exposure separately from evaluator hash. Repeated adaptive selection against the same evaluator makes that evaluator selection evidence, not fresh holdout evidence, even if its bytes remain unchanged. When final promotion requires a holdout, require fresh independent holdout evidence or return gather-evidence/insufficient-evidence for that claim.

Do not let search lineage or novelty waive blocking regressions. Gate each finalist independently against the same applicable quality/safety/portability rules.

For exported-contract changes, an ecosystem-safe claim additionally requires known-consumer evidence; search success never proves consumer compatibility.

Return accept/reject/repair/gather-evidence with candidate-local findings. Do not choose winners, continue generations, promote, or package candidates.

The v3 search input contract remains declared in `contracts/integration-manifest.json`; Gate Context v1 is a separate optional decision-evidence envelope and does not replace search lineage.
