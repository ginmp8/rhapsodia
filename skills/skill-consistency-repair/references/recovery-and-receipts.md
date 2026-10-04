# Recovery, Last-Known-Good, and Receipts

## Recovery invariant

A failed repair or package attempt must not destroy the last-known-good state or its evidence.

## Baseline and candidate

- Keep baseline copy/VCS identity outside the target mutation scope.
- Keep evaluator manifests and before/after reports outside the target.
- Prefer staging when the host supports it; otherwise ensure a verified rollback source exists before mutation.
- Never call a state last-known-good merely because it is older. It must have passed the declared gates at the time it was accepted.

## Rollback trigger

Rollback or restore from last-known-good when a repair introduces a blocker/high regression, evaluator integrity fails, candidate/report identity mismatches, package validation fails, or atomic commit cannot complete.

If rollback is incomplete, preserve both recovery backup and failed candidate paths. Do not erase evidence to make the workspace look clean.

## Consistency receipt v2

A durable receipt for consistency repair binds the verification statement to the exact candidate plus the verifier/policy assets used to reach it. It contains at least:

- receipt version, target/mode/status;
- baseline identity;
- `subject` with the final deterministic candidate digest;
- changed/added/removed file list;
- final report hash/path;
- evaluator manifest hash plus verification result;
- verifier file hashes and a canonical verifier identity;
- policy/control-plane file hashes and a canonical policy identity;
- last-known-good identity/path when available;
- explicit claim boundary.

The default verifier set is the inventory, audit, report-validator, and receipt scripts. The default policy set is `SKILL.md`, consistency taxonomy, authority/conflict rules, and report contract. Callers may add explicit package-relative verifier/policy paths.

A receipt is an attestation-like local evidence record, not a cryptographic signature, trusted provenance authority, or behavioral/semantic proof by itself.

## Package delivery receipt

A package-delivery receipt records committed stage, candidate/tree identity, archive SHA-256, normalized ZIP format version, validation status, final archive path, atomic-replace state, last-known-good preservation state, recovery paths, and the candidate subject digest.

Package receipt outputs stay outside the frozen target. `scripts/create_consistency_receipt.py` rejects candidate/report identity drift.
