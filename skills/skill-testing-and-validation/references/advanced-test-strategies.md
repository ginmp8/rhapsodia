# Advanced test strategy routing

Use this reference only when ordinary example-based tests do not adequately cover the problem. Strategies are capabilities, not mandatory dependencies or universal hard gates.

## Selection by problem shape

| Problem shape | Prefer when evidence supports it | Required guardrail |
|---|---|---|
| Invariants, round trips, broad input spaces | property-based testing | state the invariant/oracle independently of generated examples |
| Stateful protocols/workflows | stateful/model-based testing | define allowed states/transitions and reset/isolation behavior |
| Direct expected output is difficult but relations are known | metamorphic testing | state the metamorphic relation before candidate results are observed |
| Independent implementation/model exists | differential testing | establish reference independence and version identity |
| Parsers, protocols, decoders, untrusted structured input | fuzzing | explicit time/case budget, reproducible seed/corpus identity when useful |
| Consumer/provider APIs or messages | contract testing | validate both consumer expectation and provider compatibility where possible |
| Measure whether an existing green suite detects injected faults | mutation testing | green baseline; record mutation tool/operators; treat score as proxy evidence |

Use example-based tests when they are simpler and sufficient. Do not add an advanced strategy merely because a tool exists.

## Capability rules

- Detect framework/tool availability; do not auto-install a missing dependency.
- Prefer an existing project-owned tool/configuration over introducing another framework.
- If a selected strategy needs unavailable tooling/network/runtime, mark it `blocked` or `not-run`; do not silently substitute an easier metric.
- Keep strategy selection host-neutral. ChatGPT, Codex, Claude, Copilot, Cursor, CI runners, and local shells may expose different execution mechanisms while the semantic choice remains the same.
- Record budgets/seeds/reference versions when they materially affect reproducibility.

## Strategy-specific notes

### Property/stateful

Good candidates include parsers/serializers, normalization, algebraic invariants, round trips, idempotency, monotonicity, and state machines. Shrinking/reduction behavior belongs to the chosen framework, not to this skill's correctness contract.

### Metamorphic/differential

Use when a direct oracle is weak but a trusted relation or independent reference is available. Do not compare two implementations that share the same suspect logic and call that independent evidence.

### Fuzzing

Treat fuzzing as bounded exploration. Preserve failing inputs that are authorized test artifacts; do not write into protected golden/fixture paths without explicit permission. A no-crash fuzz run proves only the explored budget and properties instrumented.

### Contract testing

Use to validate distributed interface compatibility without requiring every dependency to be live. It can reduce some broad end-to-end dependence, but it does not replace system-level scenarios that test behavior outside the contract.

### Mutation testing

Use mutation to identify potentially weak assertions or uncovered fault classes. Mutation score is operator/tool/configuration dependent and must never become a universal correctness threshold.
