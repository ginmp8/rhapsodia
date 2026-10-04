# Decision Evidence Contract

Use this reference when acceptance depends on supplied or executed validation, benchmark, scenario, runtime, review, packaging, or promotion evidence.

## Principle

A gate decision is valid only for the subject and decision context it actually evaluated. Keep these identities distinct:

- baseline and direct parent;
- candidate tree;
- policy id/version/digest;
- verifier id/version/implementation identity;
- evaluator/scenario identity and exposure role;
- destination/current state when promotion depends on it;
- individual evidence producer and subject identity;
- delivered artifact and receipt.

A correct result for different bytes is stale or unrelated evidence, not a pass for the current candidate.

## Gate Context v1

When automation, strict measured acceptance, promotion, evaluator exposure, waivers, authority expansion, or ecosystem compatibility is material, use `contracts/gate-context.schema.json` and `assets/templates/gate-context.json.template`.

Validate mechanically when Python is available:

```text
<PYTHON> scripts/validate_gate_context.py \
  <GATE_CONTEXT_JSON> \
  --policy <normal|strict|advisory> \
  --expected-candidate-sha256 <FROZEN_CANDIDATE_HASH> \
  --json <REPORT_OUTSIDE_TARGET>
```

The schema is an interchange contract. The validator owns semantic cross-field checks that JSON Schema cannot express conveniently.

## Evidence subject binding

Every evidence record that influences acceptance should identify the exact candidate tree it describes. Candidate mismatch is blocking and cannot be repaired by refreshing the expected candidate after the mismatch is observed.

Required evidence whose state is `fail`, `blocked`, or `not-run` cannot be silently converted into a pass. Reduce the claim or gather the missing evidence.

## Policy and verifier identity

`strict` measured gates require stable policy and verifier implementation identities. A label such as `strict` is a mode, not sufficient identity for reproducible acceptance when the concrete rules can change.

Keep policy/verifier identity separate from candidate identity. Do not let a candidate authorize its own acceptance by mutating the deciding policy, verifier, evaluator, thresholds, or receipts.

## Evaluator role and exposure

Classify an evaluator as `development`, `selection`, or `holdout`.

A holdout is contaminated when candidate construction or selection had access to its private content/results. Byte-identical evaluator files do not restore blindness after adaptive reuse. If holdout evidence is required and the declared holdout is contaminated, gather fresh independent evidence or narrow the claim.

The gate does not invent statistical thresholds. It verifies the caller's declared evaluation contract: required trials, completed trials, holdout requirement, and independent replication requirement.

## Freshness and destination state

A pass is scoped to the destination/parent state used by the decision when that state is material. If expected and observed destination identities differ before promotion, classify the prior decision as stale and revalidate. Stale evidence is not negative evidence; it is no longer sufficient for the current promotion claim.

## Authority expansion

Treat new or broader tool permissions, executable scripts, network/filesystem mutation, secret/credential access, and new runtime dependencies as authority-surface changes. Static detection is only a signal. Under strict policy, a material expansion requires explicit authorization evidence in Gate Context.

## Consumer compatibility

Keep local acceptance separate from an `ecosystem-safe` claim. When exported contracts changed, an ecosystem-safe claim requires a complete known-consumer inventory and compatibility evidence for every known consumer. `unverified` is not equivalent to compatible.

## Rule origin and differential status

For material findings, report both:

- `rule_origin`: `agent-skills-spec`, `portable-package-policy`, `security-policy`, `experiment-policy`, `delivery-integrity-policy`, or another explicit local source;
- `regression_delta`: `introduced`, `worsened`, `preexisting-unchanged`, `improved`, `resolved`, or `unknown`.

Do not call an internal packaging convention a requirement of the Agent Skills specification unless the specification actually establishes it.
