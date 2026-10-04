# Usage Examples

## Pass

User: "Gate this candidate before acceptance. Baseline and candidate hashes match the frozen manifests, protected eval files did not change, validators passed, and the package receipt points to the candidate hash."

Expected: `pass` if semantic review also finds activation, safety, scope, portability, and output behavior intact.

## Pass with warnings

User: "Review this token-reduction patch. It removes two optional examples, keeps the output contract, and validators pass."

Expected: `pass-with-warnings` under normal policy when evidence is sufficient and the lost examples are a documented trade-off rather than a regression.

## Fail: protected evaluator drift

User: "The benchmark improved, but the candidate also changed evals/golden.json after baseline measurement. Can we accept it?"

Expected: `fail` under a measured experiment. The evaluator changed after freeze; restart the experiment if the evaluator change is legitimate.

## Fail: artifact mismatch

User: "All tests passed. The package receipt source_tree_sha256 is different from the candidate tree hash."

Expected: `fail`; the delivered artifact is not proven to come from the gated candidate.

## Fail under strict portability

User: "Make this skill work in ChatGPT, Claude, Copilot and Cursor. The new SKILL.md requires a private tool URI that only one host exposes."

Expected: `fail` under strict portable policy unless that dependency is moved to an optional host adapter or replaced with a capability-based portable mechanism.

## Insufficient evidence

User: "Can I accept this change? It should be better."

Expected: `insufficient-evidence`; request/inspect target and candidate evidence plus the validation/evaluator evidence required by the caller's policy.

## Fail: evidence replayed from another candidate

User: "The validator says pass, but its subject candidate hash is from the previous candidate."

Expected: `fail` for the supplied evidence binding. A correct result for different bytes is not acceptance evidence for the current candidate.

## Insufficient evidence: contaminated holdout

User: "The holdout bytes never changed, but we used its scores to select candidates for many generations."

Expected: do not treat that evaluator as fresh holdout evidence. If holdout is required for promotion, return `insufficient-evidence`/gather-evidence until a fresh independent holdout is supplied.

## Stale promotion decision

User: "The candidate passed against destination A, but the destination is now B."

Expected: mark the previous decision stale when destination identity is material and require revalidation. Do not call staleness a candidate defect.

## Local pass, ecosystem not proven

User: "The local package is valid, but an exported contract changed and a known consumer has not been checked."

Expected: local acceptance may pass if its own gates pass, but an `ecosystem-safe` claim is not proven until all known consumers are compatible.
