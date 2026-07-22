# Distributed ecosystem routing contract

Mago, Magia, and Nomia remain separate skills. This contract coordinates activation and multi-intent sequencing without creating a monolithic owner.

## Invariants

1. Resolve exactly one current owner before any mutation.
2. A multi-intent request is decomposed into ordered owner phases.
3. Each phase writes only artifacts owned by that skill.
4. Transitions use the strict typed handoff directions.
5. Governed work never shortcuts directly from Nomia to Magia.
6. Ambiguous requests preserve unknowns and perform no mutation until the current phase is resolved.
7. The shared corpus is structural/planned evidence; it is not live-model precision or recall evidence.

## Lifecycle

`Nomia intake -> Mago planning -> Magia execution -> Mago reconciliation -> Nomia closure`

MAGIA ADHOC remains valid for bounded direct repository work outside a governed board package.
