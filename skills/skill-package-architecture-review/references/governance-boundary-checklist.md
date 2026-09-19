# Governance Boundary Checklist

**Contract version:** 2.0.0

Use for `governance-boundary-review` and whenever architecture depends on authority, ownership, or adjacent-skill handoffs.

## Ownership evidence

Determine the package role before recommending structure:

- reviewer;
- implementer;
- benchmarker;
- hardener;
- harness runner;
- domain specialist;
- router.

Check whether modes/resources preserve one coherent role. Deterministic folder-role ownership from the inventory is only a starting taxonomy; do not infer people or teams from names.

## Authority evidence

Record whether the package may:

- read target files;
- edit target files;
- execute scripts;
- package artifacts;
- run/score scenarios;
- rewrite domain rules;
- publish measured claims.

Different authority levels across modes are a separation signal only when they cannot be made explicit and safely governed within one package.

## Adjacent-skill boundaries

Architecture review owns structural/dependency judgment. Typical next-action handoffs:

- consistency repair: internal contradictions and bounded repairs;
- hardening: package maturity and reliability upgrades;
- harness: scenario/evaluator execution and evidence scaffolding;
- improver: bounded before/after experiments;
- benchmark: formal comparative scoring;
- implementation/code skills: repository changes;
- security review: secrets/authority/security audit.

A handoff does not change the primary architecture decision.

## Handoff contract

Include:

1. trigger for handoff;
2. exact package identity/evidence already inspected;
3. targeted next action;
4. constraints/protected paths;
5. acceptance gate.

## Stop conditions

Stop before architectural mutation advice when:

- evidence does not satisfy the rubric's minimum decision criteria;
- hidden consumers cannot be checked for a destructive change;
- the change would weaken safety, validation, audit, or governance controls;
- measured-quality claims lack executed evidence;
- the requested change crosses into target-domain design without source truth.
