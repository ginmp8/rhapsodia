# Frozen scoring contract (v1.1.0)

All numerical values are derived from canonical JSON `source.json`, `requirements.json`, `checks.json`, `evidence.json` and the algorithm. SHA-pinned Git objects and frozen genuine test receipts are the only supported direct pass/fail inputs. Deterministic replay does **not** independently certify semantic completeness.

A requirement is `PASS` only when every declared check passes and the proof policy is fulfilled; `PARTIAL` when some checks pass but others failed or are unobserved (including runtime criteria lacking an actual passing test); `FAIL` when all observed checks fail; `UNVERIFIED` when no check result was observed; or `NOT_APPLICABLE` with a documented rationale.

`completion_verified_pct = 100 * PASS_weight / applicable_weight`, rounded half-up to two decimal places, only when a complete plan has actual observed checks and at least one conclusive PASS/FAIL criterion. Otherwise it is `null` and MUST NOT be represented as 0% implementation. The report also includes `assessment_state` (`NOT_ASSESSED`, `INCOMPLETE_PLAN`, `PARTIALLY_ASSESSED`, `EVALUATED_KNOWN_SCOPE`), check coverage, separate AC and REQ groups, and an arithmetic possible upper bound (never a forecast).

`preflight` is mandatory before presenting a numeric result. It rejects no checks, unmapped requirements, stale source or inadequate pinned evidence. `audit_bundle.py` is the default **artifact generator**, including diagnostic cases where preflight cannot pass; it does not waive preflight for numeric claims. Unexecuted checks and stale/foreign receipts cannot become proof. Parent REQs and child ACs overlap and must never be combined into a misleading completion denominator.

Byte-for-byte replay applies to identical inputs and algorithm; new tests or code observations generate a new evidence version. Live GitHub capture, semantic mapping, test quality and source completeness require separate verification. Compare reports only with matching frozen requirements/checks/algorithm; unassessed candidates are not valid completion comparisons.
