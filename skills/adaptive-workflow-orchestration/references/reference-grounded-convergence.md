# Reference-grounded convergence

Use this profile when a task has a high-fidelity source of truth (existing implementation, design, product document, protocol, failing behavior, or live system state) and correctness is better achieved through repeated proof than through one large speculative generation.

## Core model

1. **Reference before synthesis.** Read the smallest source slice that can answer the checkpoint. A synthesized spec is a convenience, not a replacement for a stronger primary reference.
2. **Reviewable checkpoints.** Split work into small ordered slices that can be understood quickly. Early checkpoints should be deliberately small; later slices may grow only after earlier architecture/behavior decisions have passed their gates.
3. **Freeze the oracle before the candidate.** A read-only analyst may derive acceptance cases, edge cases, or an executable-oracle identity from the reference before production begins. Do not move acceptance criteria after seeing the candidate.
4. **Ordered gates are control flow.** The checkpoint's `gate_ids` order is binding when `promotion.gate_order_is_binding=true`. Stop at the first failed required gate, repair through the canonical producer, then rerun every affected required gate.
5. **Fresh context for iterative roles.** Prefer a fresh producer/repair/reviewer context that reads current code, the bounded reference slice, the frozen oracle, and the latest accepted feedback. Source artifacts hold state; the context window should not become the state store.
6. **Memory is evidence, not truth.** Carry forward only accepted/proven feedback with source/checkpoint identity. Revalidate mutable source state when the plan declares a freshness policy.
7. **Autonomy does not relax proof.** Human approval may be required, defaulted, or explicitly omitted by policy, but executable/perceptual/adversarial gates do not become weaker in autonomous mode.
8. **Materialize promoted state.** When `materialize_promoted_checkpoint=true`, record an immutable candidate/checkpoint identity plus gate evidence before dependent work starts.
9. **Verify closure, not motion.** A passing intermediate candidate is not final closure when the authoritative source can change after handoff. Reconcile the authoritative end state before declaring completion.
10. **Move guarantees into code.** Deterministic validators should own identities, budgets, ordering, deduplication, current-state checks, packaging, and other mechanically enforceable invariants. Agents own bounded judgment.

## Recommended v2 fields

- `evidence.reference_identity`: stable identity of the reference set.
- `evidence.freshness_policy`: `frozen-input`, `revalidate-before-mutation`, or `revalidate-before-promotion`.
- checkpoint `reference_scope`: exact source slice(s) relevant to that checkpoint.
- checkpoint `oracle_identity`: frozen acceptance/test/rubric identity derived before production.
- checkpoint `context_mode`: prefer `fresh-context` for repair/review loops.
- `promotion.gate_order_is_binding=true`.
- `promotion.materialize_promoted_checkpoint=true` when a durable checkpoint identity can be recorded.
- `promotion.autonomy_policy`: `human-required`, `human-default`, or `policy-autonomous`.

## Gate guidance

A common order is executable behavior/proof → perceptual equivalence when applicable → adversarial review → human/policy approval. This is a useful default, not a universal taxonomy. The accepted plan owns the exact order.

Perceptual comparison is `invalid`, not `fail`, when reference and candidate are in different states. Recapture comparable states before judging fidelity.

Independent reviewers should not inherit the producer's hidden rationale. Give them the candidate, bounded reference/rubric, and required evidence.

## Parallelism

Parallelize independent checkpoints only when their read/write sets and authoritative state are isolated. Each branch converges through its own gates. Shared mutable state or one canonical writer remains serialized.

## Source basis and adaptation boundary

The pattern is informed by public engineering reports from Shopify:

- Helix: small ordered checkpoints, reference-as-spec, generated integration-style cases, ordered gates, context-isolated reviews, accepted feedback, optional autonomy, and checkpoint commits: https://shopify.engineering/helix
- Agentic harness/Dispatch: partitioned context, cross-model verification, test oracles, and deterministic code for credentials/Git/storage: https://shopify.engineering/building-an-agentic-harness-that-outlasts-the-model
- River: live-state revalidation, evidence bound to current code identity, deliberate handoffs, closure verification, and moving guarantees from prompts into code: https://shopify.engineering/river-vulnerability-remediation
- ShopGym: fresh execution agents that read current code + relevant spec + latest feedback, with deterministic and visual verification loops: https://shopify.engineering/shopgym
- Roast: declarative structured workflows that interleave deterministic and agentic steps: https://shopify.engineering/introducing-roast

These are evidence sources, not normative dependencies. RhapsodIA remains host-neutral and does not require Shopify tooling, models, mobile architecture, or proprietary runtimes.
