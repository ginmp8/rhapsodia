# Evolutionary Search Routing

Use only for explicit `evolutionary-optimization`. Canonical optimization remains the default and must work without Skill Evolution installed.

## Authority

- **Booster**: target intake, trust, target class, capability/evaluator freeze, specialist routing, mutation/evaluation owner dispatch, final independent change gate, finalist freeze, target promotion, packaging, and any future workflow-policy promotion.
- **Skill Evolution**: population/search state, candidate roles, lineage, recombination/backcross plans, Pareto/non-dominance, novelty/diversity, survivor/finalist selection, stagnation/budget termination.
- **Mutation owner**: materializes one requested candidate; Skill Evolution never edits target bytes.
- **Evaluation owners**: produce identity-bound gates/metrics; Skill Evolution never changes evaluator semantics.

## Entry conditions

Require all of: explicit evolutionary intent; immutable baseline identity; validated pre-evolution artifacts when material; hard gates; objective directions; frozen evaluator/scenario identities; mutation and evaluation capabilities; bounded budget. Default search budget is four initial strategies, at most four active candidates, normally 8-12 total candidates, hard ceiling 20, two finalists, three stagnant rounds.

## Handoff

Create a v4 `evolution-handoff.json` from `assets/templates/evolution-handoff.json.template` and validate it with `scripts/validate_evolution_handoff.py`. Then compile the caller-owned capability map, validated hypothesis pool, transformation registry, and evaluation plan into the Skill Evolution v4 search contract with `scripts/build_evolution_contract.py`. Validate that compiled contract with the Skill Evolution contract validator before search. This adapter keeps Booster-owned schemas out of the search controller while preserving exact artifact identities, including the evaluation-plan identity. The evaluation plan is schema v2 and carries the finalist policy; the v4 handoff repeats that policy, and the compiler rejects any handoff/evaluation-plan drift before producing the v4 search contract.

The canonical strategy/result remains a protected comparator and may be used for backcross. The immutable original baseline remains the cumulative regression reference.

## Search loop

1. invoke Skill Evolution with the validated handoff;
2. receive candidate requests;
3. validate each `candidate-request-v2`, then dispatch it to exactly one mutation owner that declares compatibility with `skill-opt.candidate-request` v2;
4. run required change-gate/evaluation levels;
5. normalize identity-bound evaluator evidence to candidate-evaluation v2 (use `scripts/build_candidate_evaluation.py` when filesystem execution is available), validate it against the frozen search contract, and return it to Skill Evolution;
6. repeat until Skill Evolution returns finalists/termination; a `sufficient-finalists` stop is valid only when the frozen finalist quota and policy are satisfied;
7. Booster independently reruns the final required proof gates;
8. Booster alone freezes/promotes/packages the accepted target candidate.

Never let Skill Evolution directly call the entire specialist catalog or become a second Booster.

## Self-improvement

When Booster itself is the target, freeze the active Booster controller outside candidate mutation. Skill Evolution must also remain outside the Booster candidate worktree. Candidate Booster variants cannot modify the controller, evaluator, or search controller currently judging them.

## Workflow-policy learning

A target-level search win is evidence for that target, not automatic policy. Cross-target search history may be retained as advisory evidence. Promoting a search strategy into Booster canonical policy requires a separate governed comparison across relevant target classes.


## Contract evolution

The v4 handoff/search contract is a public integration surface. Its version and the candidate-request/evaluation interfaces are declared in `contracts/integration-manifest.json`. Before changing any of those surfaces, use `references/integration-impact-contract.md` and gate all known peer consumers. Do not silently upgrade one side of the handoff.
