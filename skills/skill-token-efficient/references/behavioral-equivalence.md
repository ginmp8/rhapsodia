# Behavioral Equivalence

Keep equivalence claims separated by evidence layer. A stronger layer may consume weaker evidence, but a weaker layer never proves a stronger claim.

## Evidence layers

| Layer | What it can establish | Minimum evidence |
|---|---|---|
| `structural` | package shape, refs, protected literals, schema/syntax, hashes | deterministic validators |
| `semantic-review` | preserved intent, authority, workflow relations, readability | explicit semantic review against frozen baseline/contract |
| `behavioral` | same required choices/actions for covered scenarios | executed baseline/candidate scenarios with the same frozen evaluator |
| `runtime` | realized host/tool behavior, cost, latency, cache effects | observed execution evidence with comparable environment/profile identity |

Static checks, lexical similarity, embedding similarity, token reduction, or a structurally valid trace cannot establish behavioral or runtime equivalence by themselves.

## Behavioral comparison

When a behavioral claim matters:

1. freeze scenarios, prompts/files, expected behavior, evaluator, thresholds, and material environment identity before candidate mutation;
2. execute the same scenario set against baseline and candidate;
3. retain per-scenario outcomes, not only an aggregate score;
4. treat activation, authority/precedence, safety, workflow/tool protocol, output/evidence duties, and stop behavior as hard regressions even when aggregate quality improves;
5. mark behavioral evidence `not-run` when execution capability is unavailable; do not translate planned scenarios into an executed pass.

For stochastic model behavior, repeated trials may be required for a strong reliability/improvement claim. Do not infer statistical reliability from one run.

## Runtime comparison

Runtime claims require actual runtime evidence. Estimated token/cost profiles may guide planning but must be labeled estimated. Provider/model/tool/cache changes that can alter the outcome must be captured or the pair declared incomparable.

## Claim language

Allowed:

- `token count decreased`; 
- `structural preservation passed`;
- `semantic review passed with stated limitations`;
- `behavioral scenarios were not run; behavioral equivalence is not proven`.

Not allowed without corresponding evidence:

- `behavior preserved` from static/semantic checks alone;
- `runtime cost improved` from raw input-token reduction alone;
- `cross-model equivalent` from one model/tokenizer/host result.
