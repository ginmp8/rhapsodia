# Evaluation and Gates

Use to define baseline/final evidence, frozen evaluators, acceptance, and claims.

## Evidence layers

Keep separate:

- structural evidence: package shape, references, frontmatter, script syntax, portability/core conformance;
- behavioral evidence: executed scenarios and evaluator decisions;
- runtime evidence: actual tool/browser/application behavior;
- subjective evidence: independent human/model review where quality is inherently judgmental;
- delivery evidence: frozen target identity, package hash, atomic commit/recovery receipt.

One layer does not prove another.

## Freeze before comparison

Before candidate mutation:

1. preserve an immutable target snapshot;
2. declare scenario corpus/evaluator rules and acceptance thresholds;
3. protect evaluator fixtures, expected outputs, baseline evidence, scoring rubrics, and thresholds;
4. record external/VCS source identities when they materially affect results.

If an evaluator is wrong, invalidate that experiment and restart after fixing/freezing it. Never edit evaluators to make the candidate pass.

## Required hard gates

For mutation/package claims, require as applicable:

- unambiguous target identity and writable scope;
- immutable baseline captured safely;
- Agent Skills portable core valid for the selected profile;
- no broken local references/scaffold markers;
- modified deterministic scripts/tests pass;
- target-owned mandatory tests/validators pass;
- protected/evaluator evidence unchanged;
- no blocking activation, semantic, safety, compatibility, or packaging regression;
- package/report outputs pass alias/canonical preflight;
- package receipt corresponds to the final frozen target tree;
- last-good output/recovery behavior is preserved on failure.

## Saturated metrics

A static score of `100` is a gate, not proof that nothing can improve. Add auxiliary metrics tied to the hypothesis, such as:

- portable-core violations;
- host-specific dependencies in core semantics;
- portability/integrity controls present;
- entry-point/scenario coverage;
- deterministic gate coverage;
- baseline/evaluator identity controls;
- package alias/recovery/receipt behavior;
- unresolved risks/unknowns.

Never claim behavioral improvement from a new static metric alone.

## Claim rule

Use `measured` only for executed evidence. Use `derived` for inspected structure, `researched` for current sourced facts, `proposed` for planned checks, and `unknown` when evidence is unavailable. Do not convert missing execution capabilities into pass results.
