# Usage Examples

## Pass

User asks: "Gate this patch before accepting the skill-improver candidate. The benchmark improved from 88 to 91 and validators passed."

Expected result: status `pass` when the diff keeps activation, references, safety boundaries, validation claims, and output contract intact.

## Pass with warnings

User asks: "Review this token-reduction patch. It removes two examples but keeps the output contract and validators pass."

Expected result: status `pass-with-warnings` if the examples were optional and the report records the trade-off plus a follow-up activation-suite hypothesis.

## Fail

User asks: "The benchmark improved, but the patch removed the non-activation boundaries and deleted a referenced validation file. Can we accept it?"

Expected result: status `fail`; decision `repair-before-accept` or `reject` because benchmark improvement does not override blocking quality regression.

## Insufficient evidence

User asks: "Can I accept the change? It should be better."

Expected result: status `insufficient-evidence`; request target evidence, candidate evidence, and validation or benchmark output. Do not infer success.
