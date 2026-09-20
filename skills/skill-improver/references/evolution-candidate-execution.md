# Evolution Candidate Execution

Use only when a caller supplies a validated candidate request from a multi-candidate search. Skill Improver remains a mutation engine; it does not own population state, Pareto selection, recombination strategy, survivor selection, or final promotion.

## Request

Require candidate-request v2: `request_version=2`, `candidate_id`, `operator`, `base_parent_id`, `donor_parent_ids`, `transformation_ids`, `expected_capability_effects`, `reason`, and deterministic `request_signature`. A multi-parent request still has one physical `base_parent_id`; donors contribute semantic transformations, not implicit file ancestry.

Validate with `scripts/validate_candidate_request.py`. Resolve transformation definitions from the caller-supplied registry/evidence. Reject unknown/conflicting transformations rather than guessing.

## Execution

Materialize a fresh isolated candidate from the base parent. Apply only the requested compatible transformations and required dependencies. Never import donor diffs wholesale. Preserve evaluator/protected evidence. Emit generation-receipt v3 containing candidate id/identity, the exact request signature, base/donor ids, operator, applied transformation ids, changed files, validation status, and causal limitations. Validate it with `scripts/validate_generation_receipt.py` before returning it to the caller.

## Boundary

Return the candidate/receipt to the caller. Do not decide whether the child survives, wins, crosses again, or is promoted.


Both interfaces are declared in `contracts/integration-manifest.json`. A request/receipt version change is a public integration change and must be impact-gated by the orchestrator; do not silently accept an unknown version.
