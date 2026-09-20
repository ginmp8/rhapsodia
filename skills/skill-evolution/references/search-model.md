# Search Model

## Lifecycle

Use an evidence-guided champion-challenger search rather than an unconstrained genetic algorithm:

`freeze -> seed -> generate -> cheap-evaluate -> select -> recombine -> evaluate -> stop -> finalists`

The search works on semantic candidate plans and transformation ids. It never mutates raw files itself.

## Default population shape

Start with up to four deliberately different seeds:

- canonical;
- evidence-driven alternate;
- focused weakness strategy;
- novel-bounded strategy.

Keep at most four active candidates. Normally expect 8-12 total candidates across the run. Allow up to 20 only as a hard ceiling.

## Search rounds

A round may create 1-3 children. Prefer targeted recombination over all-pairs crossover. Search history is append-only. A rejected child still contributes negative evidence.

## Stagnation

A round is stagnant when it creates no new non-dominated candidate and no materially novel valid strategy. Default stop after three consecutive stagnant rounds.

Reset stagnation only when a candidate materially changes the Pareto archive or introduces a validated novel strategy likely to support a later useful recombination.

## Cost control

Escalate evaluation only when lower levels pass. Do not run L4/L5 on every candidate. L5 is promotion-oriented, not a development loop.
