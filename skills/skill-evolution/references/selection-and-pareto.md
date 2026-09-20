# Selection and Pareto Contract

## Hard gates first

Filter candidates with blocking hard-gate failures before metric comparison. A gain on one metric never compensates a failed safety, semantic, activation, evaluator-integrity, validation, or package gate designated as hard.

## Dominance

For objective metrics with direction:

- candidate A dominates B when A is no worse than B on all comparable objectives and strictly better on at least one;
- missing required metric evidence prevents a strict dominance claim;
- use the Pareto frontier when several trade-offs remain valid.

## Active-capacity reduction

When the non-dominated set exceeds active capacity:

1. preserve required canonical/champion reference roles when configured;
2. prefer candidates with distinct transformation sets/capability effects;
3. use supplied novelty score when valid;
4. prefer lower evaluation uncertainty;
5. use stable candidate id as the final deterministic tie-breaker.

Do not manufacture a weighted global score unless the weighting policy was frozen before candidate results were known.

## Novelty

Novelty is useful only among otherwise valid candidates. It never rescues a hard-gate failure. Acceptable novelty signals include transformation-set distance, workflow-strategy distance, capability-effect difference, or caller-supplied normalized novelty evidence.
