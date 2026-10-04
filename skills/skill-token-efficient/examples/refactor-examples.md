# Refactor Examples

## Safe imperative shortening

Before: `You should make sure that you read the target SKILL.md first before doing any other work.`

After: `Read target SKILL.md first.`

Why safe: ordering and modality remain explicit.

## Merge duplicate negatives

Before: `Do not edit secrets. Do not edit credentials. Do not edit .git. Do not edit benchmark fixtures.`

After: `Do not edit secrets, credentials, .git, or benchmark fixtures.`

Why safe: each prohibition remains independently recoverable.

## Reject authority loss

Bad: `Avoid editing evaluators when possible.`

Original duty: `Never edit frozen evaluators to make a candidate pass.`

Why rejected: the rewrite changes mandatory prohibition into a preference and loses the causal guard.

## Progressive loading with an operational condition

Good entrypoint rule: `When runtime/cost evidence is supplied, read references/runtime-economics.md before interpreting a token win.`

Bad move: link the reference somewhere in `SKILL.md` but remove every instruction that says when it must be loaded.

## Tokenizer portability

Good: count baseline and candidate independently with `estimator-v1`; optionally repeat both arms with `tiktoken:<encoding>` and report a second delta.

Bad: compare an estimator baseline against a tiktoken candidate and calculate one reduction percentage.

## Reject false runtime efficiency

Suppose uncached input drops from 1,000 to 800 tokens, but cache-write/output growth raises total tokens and declared cost.

Correct: report every component and the inversion. Do not call the candidate cheaper merely because the raw prompt is shorter.

## Reject false behavioral equivalence

Bad: `Static preservation passed and semantic similarity is high, therefore behavior is preserved.`

Correct: report structural and semantic-review evidence as passed; mark behavioral equivalence `not-run` unless paired scenarios were actually executed.
