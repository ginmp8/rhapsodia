# Measurement and Preservation

## Purpose

Measure what can actually be measured, preserve semantic obligations during compression, and prevent token-efficiency claims from outrunning the evidence.

## Evidence layers

Keep these claims separate:

1. **Host telemetry** - the only direct evidence for hidden reasoning-token or billed-token change when the host exposes it.
2. **Static control-plane footprint** - deterministic size of `SKILL.md` and metadata. This measures package prompt footprint, not private reasoning cost.
3. **Behavioral equivalence** - executed paired scenarios showing that compression preserved required outcomes.
4. **Structural preservation** - validators proving that required rules, references, and protected literals remain present.

Never infer layer 1 from layer 2.

## Tokenization method

`scripts/token_audit.py` defaults to `lexeme-v1`:

```text
unicode word runs OR one non-whitespace punctuation/symbol = one proxy unit
regex: \w+|[^\w\s]
```

The method is deterministic and dependency-free. It is a comparison proxy, not a model tokenizer and not a billing metric. Compare baseline and candidate only with the same method and file grouping.

Report at least:

- bytes;
- characters;
- words;
- `lexeme-v1` proxy units;
- delta for `SKILL.md`;
- delta for `agents/openai.yaml`;
- delta for all text resources.

If exact host/model token counts are available, record the host, model/tokenizer identity, version when known, and measurement source separately.

## Semantic invariants

Compression must preserve, when applicable:

- user intent, language, audience, and requested format;
- safety, privacy, security, legal, medical, and financial boundaries;
- evidence, citation, source, path, line, freshness, and provenance duties;
- executed versus suggested validation status;
- exact commands, APIs, schemas, flags, versions, numeric limits, and file identities that affect correctness;
- output completeness and compatibility commitments;
- the boundary against exposing hidden chain of thought.

The machine-readable contract is `contracts/semantic-contract.json`.

## Protected literal review

`scripts/compare_candidate.py` extracts and compares baseline versus candidate occurrences for these classes:

- URLs;
- local paths and file references;
- shell-like commands;
- environment-variable names;
- schema/file identifiers;
- CLI flags;
- proper-noun candidates;
- versions;
- numbers.

Literal comparison is a guardrail, not semantic proof. A removed literal is a review signal unless the contract marks it hard. Safety, validation, and evidence rules are hard invariants and must not be weakened merely to save tokens.

## Protected maintenance scope

During package updates, mutate only the candidate skill tree. Keep the immutable baseline, frozen evaluators, `.git`, secrets, credentials, caches, old archives, generated evidence, fixtures, expected outputs, and unrelated files outside the mutation surface. Never edit protected evidence merely to make a candidate pass.

## Progressive-loading preservation

Keep `SKILL.md` as the compact control plane. Put branch-specific mechanics, measurement rules, package-maintenance detail, scenarios, and validators in one-level supporting files. Do not make ordinary runtime activation load maintenance-only resources.

A candidate is not better merely because the total package is smaller. Prefer a smaller always-loaded control plane plus stronger on-demand validation when semantic coverage is preserved.

## Acceptance and claim rules

For a package update:

1. preserve an immutable baseline;
2. freeze the evaluator used for comparison outside the candidate mutation surface;
3. run the same baseline validator against both baseline and candidate;
4. run `token_audit.py` with the same method on both;
5. run `compare_candidate.py` and resolve hard failures;
6. run the candidate-owned validator and package validator;
7. freeze the final candidate identity before packaging;
8. emit a receipt tied to the exact packaged bytes.

Do not claim hidden reasoning-token savings without host telemetry. Do not claim behavioral equivalence or improvement from planned scenarios, static package checks, or one successful example.
