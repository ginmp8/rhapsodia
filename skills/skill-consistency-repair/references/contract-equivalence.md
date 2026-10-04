# Contract Equivalence

Use when the same machine-readable behavior is represented by both a declarative schema and an executable validator/parser.

## Safe differential rule

A differential check is allowed only when both interfaces are explicitly known from target documentation/code or a caller-supplied contract. Never guess how to invoke an arbitrary validator and never execute untrusted target code merely because a schema exists.

1. Identify the schema version/dialect and executable validator interface.
2. Freeze a shared corpus before candidate mutation when it will decide acceptance.
3. Include valid boundary cases and invalid single-constraint mutations relevant to the declared contract.
4. Run the declarative validator and executable validator against the same cases when execution is safe and available.
5. Compare accept/reject outcomes and, when part of the contract, stable diagnostic codes.
6. Any unexplained disagreement is `contradictory` or `blocked`; do not change the corpus or expected outcomes after seeing candidate results merely to obtain agreement.

If the required validator runtime/library is unavailable, record the differential gate `not-run` instead of substituting model judgment.

## Scope boundary

This workflow checks equivalence of already-declared contracts. It does not design domain schemas, install dependencies, or promote a schema/validator as authoritative without the authority rules in `authority-and-conflict-resolution.md`.
