# Scenario Guidelines

Use when designing or repairing scenario suites. Scenario design is evidence planning; measured results require a separate executed-results identity.

## Minimum activation coverage

Maintain at least five prompts each for `should_activate`, `should_not_activate`, `ambiguous`, and `edge_case`. Add `regression` for confirmed failure modes and `adversarial` for unsafe pressure/boundary attempts.

## Required consistency regressions

Coverage should include:

- ownership drift;
- graph-orphaned resource where deletion is not proven safe;
- broken local reference;
- duplicated contract with diverging consumers;
- migration-only behavior reachable from normal flow;
- contradictory authoritative sources;
- validator bound to an older contract;
- unknown resource whose removal would be unsafe.

## Scenario fields

Use stable ids, category/type, prompt, expected activation, expected behavior, explicit acceptance criteria, and status. Keep evaluator design separate from executed observations.

## Freeze policy

Once a scenario suite is selected as an acceptance evaluator, freeze it by hash before evaluating candidate repairs. A needed evaluator correction invalidates that comparison; update evaluator separately, refreeze, and restart acceptance.

## Examples versus evals

`evals/` is the authoritative planned evaluator input when declared by the workflow. `examples/` is illustrative and must identify its authoritative source; examples never override frozen evaluator expectations.
