# Evolution Candidate Execution

Use only when a caller supplies a validated candidate request from a multi-candidate search. Skill Improver remains a mutation engine; it does not own population state, Pareto selection, recombination strategy, survivor selection, or final promotion.

## Request

Require: `request_version`, `candidate_id`, `operator`, `base_parent_id`, optional `donor_parent_ids`, `transformation_ids`, and `reason`. A multi-parent request still has one physical `base_parent_id`; donors contribute semantic transformations, not implicit file ancestry.

Validate with `scripts/validate_candidate_request.py`. Resolve transformation definitions from the caller-supplied registry/evidence. Reject unknown/conflicting transformations rather than guessing.

## Execution

Materialize a fresh isolated candidate from the base parent. Apply only the requested compatible transformations and required dependencies. Never import donor diffs wholesale. Preserve evaluator/protected evidence. Emit a receipt containing candidate id/identity, base/donor ids, applied transformation ids, changed files, validation status, and causal limitations.

## Boundary

Return the candidate/receipt to the caller. Do not decide whether the child survives, wins, crosses again, or is promoted.
