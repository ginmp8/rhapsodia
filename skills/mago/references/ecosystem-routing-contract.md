# Distributed ecosystem routing contract

Mago, Magia, and Nomia remain separate skills. This contract coordinates activation and multi-intent sequencing without creating a monolithic owner or a fourth writing facade.

## Invariants

1. Resolve exactly one current owner before any mutation.
2. Load only the selected owner control plane plus the compact shared lifecycle/routing context.
3. A multi-intent request is decomposed into ordered owner phases.
4. Each phase writes only artifacts owned by that skill.
5. Transitions use the strict typed handoff directions.
6. Governed work never shortcuts directly from Nomia to Magia.
7. Ambiguous requests preserve unknowns and perform no mutation until the current phase is resolved.
8. Shared contracts remain local byte-equivalent copies; runtime imports or execution of peer packages are forbidden.
9. The shared corpus is structural/planned evidence; it is not live-model precision or recall evidence.

## Lifecycle

`Nomia intake -> Mago planning -> Magia execution -> Mago reconciliation -> Nomia closure`

MAGIA ADHOC remains valid for bounded direct repository work outside a governed board package.

## Live-model evidence contract

The frozen corpus remains structural evidence. Use `scripts/live_routing_harness.py prepare` to produce an immutable execution request and `evaluate` only after an external model host returns one observation for every frozen scenario. Results conform to `references/live-routing-result-schema.json` and record model/provider/version/host, run date, corpus hash, skill tree hashes, selected owner/mode/handoffs, confusion matrix, failures, and claim eligibility. Fixture results validate the harness only and never authorize precision/recall claims. The current release remains `live-model-routing-not-measured` until an attributed `evidence_kind: live-model` result exists.
