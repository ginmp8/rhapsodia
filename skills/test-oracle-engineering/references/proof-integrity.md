# Proof Integrity

## What strict verification establishes

`verify_oracle_proof.py` mechanically checks that:

1. both artifacts satisfy the v2 standalone contracts;
2. `oracle_spec_identity` equals the SHA-256 of canonical JSON bytes for the supplied spec;
3. oracle and candidate identities agree across spec, proof, and supplied/recomputed candidate identity;
4. executed argv equals the frozen spec argv;
5. attempts stay within `max_attempts` and satisfy declared repetitions for strong proof;
6. the verdict/outcome contract is valid;
7. contradictory expected/rejecting semantic outcomes are not accepted as stable proof.

## Candidate tree identity

When `--candidate-root` is used, the verifier hashes every regular file or symlink under the root in lexical relative-path order. Each path and its bytes (or symlink target) are length-prefixed before SHA-256. This provides deterministic identity for the supplied tree; it is not a VCS commit signature and does not imply repository cleanliness.

Prefer an immutable VCS identity when that is the project source of truth. Use a tree hash when exact local bytes are the candidate.

## What mechanical verification does not establish

A valid receipt does not prove that:

- the oracle design is semantically adequate;
- a supplied evidence ref actually contains the claimed domain observation unless another verifier checks it;
- a statistical decision rule was calculated correctly;
- external services behaved correctly outside the observed boundary;
- an LLM-generated assertion reflects requirements merely because it compiles.

Keep these as semantic/runtime evidence, not schema claims.

## Evidence freshness

Any material change to spec bytes, candidate identity, evaluator/criteria, protected fixtures, command semantics, or relevant environment invalidates affected proof. Do not silently refresh hashes after a mismatch; re-establish the oracle and rerun affected evidence.
