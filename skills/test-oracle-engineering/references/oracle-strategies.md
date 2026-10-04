# Oracle Strategies

Choose the strategy that can falsify the claim with the least unsupported inference. Strategy is independent from `claim_type`.

| Strategy | Use when | Required reasoning boundary |
|---|---|---|
| `specified` | source contract directly defines expected behavior | bind expected/failure semantics to that source |
| `invariant` | a state relation must always hold | state the invariant explicitly |
| `property` | many generated inputs share one semantic property | generators create cases; the property remains the oracle |
| `model-based` | an independent state/model predicts legal behavior | freeze the model identity and relevant transition semantics |
| `metamorphic` | direct expected output is unavailable but relations across transformed inputs are known | freeze source/follow-up transformation and relation before execution |
| `differential` | independent implementations/references can be compared | freeze references, normalization, undefined/excluded cases, and decision rule; disagreement alone does not assign correctness |
| `statistical` | correctness is probabilistic or distributional | predeclare sample/repetition rule and decision threshold; report uncertainty |
| `implicit` | crash, invariant violation, sanitizer finding, or impossible state itself is the rejection signal | keep scope narrow; absence of an implicit failure rarely proves full correctness |

## Strategy quality

Record:

- `assumptions`: conditions under which the oracle is sound enough for the claim;
- `blind_spots`: plausible faults the oracle does not observe;
- `quality.soundness_assumptions` and `quality.completeness_limits` when those distinctions affect interpretation;
- optional `strength_check` when a false `proven` result is costly.

Strength checks are not code coverage. Prefer a targeted negative control, oracle-gap check, or mutation analysis only when it materially tests whether the observation would detect the relevant fault class.

## Generated and LLM-assisted oracles

Generation may author verification code, but it cannot become its own source of truth. For `generated`, `inferred`, or `llm-assisted` origins, record an independent validation path such as a requirement, formal/property invariant, independent model/reference, metamorphic relation, or separately frozen evaluator.
