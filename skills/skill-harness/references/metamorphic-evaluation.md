# Metamorphic Evaluation

Use when exact expected outputs are weak or expensive but semantically related inputs should preserve a necessary relation. Metamorphic testing complements ordinary scenarios; it does not replace direct oracles when those exist.

Validate suite structure with:

```text
<PYTHON> scripts/validate_metamorphic_suite.py <METAMORPHIC.json>
```

Useful relations for skills include:

- `same-routing`: semantic paraphrases should activate/non-activate consistently;
- `same-hard-gates`: irrelevant context or equivalent path spellings must not change safety/acceptance gates;
- `same-core-semantics`: changing host wording should preserve portable-core behavior while allowing adapter differences;
- `equivalent-outcome`: semantically equivalent inputs should satisfy the same output contract;
- `monotonic`: adding clearly relevant evidence should not reduce required coverage without justification.

Declare the transformation, base case, evaluator identity, and expected relation before execution. `status: measured` requires a result and evidence identity for every variant. Metamorphic relations must be semantically justified; do not invent invariance where the input change legitimately changes the answer.
