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

Create `evolution-handoff.json` from `assets/templates/evolution-handoff.json.template` and validate with `scripts/validate_evolution_handoff.py`. The handoff is capability-based: it describes mutation/evaluation interfaces without requiring vendor-private tool names.

The canonical strategy/result remains a protected comparator and may be used for backcross. The immutable original baseline remains the cumulative regression reference.

## Search loop

1. invoke Skill Evolution with the validated handoff;
2. receive candidate requests;
3. dispatch each request to exactly one mutation owner;
4. run required change-gate/evaluation levels;
5. return identity-bound candidate evidence to Skill Evolution;
6. repeat until Skill Evolution returns finalists/termination;
7. Booster independently reruns the final required proof gates;
8. Booster alone freezes/promotes/packages the accepted target candidate.

Never let Skill Evolution directly call the entire specialist catalog or become a second Booster.

## Self-improvement

When Booster itself is the target, freeze the active Booster controller outside candidate mutation. Skill Evolution must also remain outside the Booster candidate worktree. Candidate Booster variants cannot modify the controller, evaluator, or search controller currently judging them.

## Workflow-policy learning

A target-level search win is evidence for that target, not automatic policy. Cross-target search history may be retained as advisory evidence. Promoting a search strategy into Booster canonical policy requires a separate governed comparison across relevant target classes.
