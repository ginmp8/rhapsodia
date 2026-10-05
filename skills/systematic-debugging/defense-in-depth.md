# Defense-in-Depth After Diagnosis

## At a Glance

- **Purpose:** Add independent safeguards after a failure mechanism is understood, without duplicating the same validation indiscriminately across every layer.
- **Load when:** A confirmed/probable failure exposes a bypassable trust boundary, invariant, dangerous side effect, or operational safety gap.
- **Decision impact:** Determines which layer owns each safeguard and prevents "validate everywhere" from creating duplicated policy and drift.

## Contents

- Placement model
- Trust boundary validation
- Invariant ownership
- Dangerous side effects
- Operational diagnostics
- Verification

## Placement model

Map the failure's data/control path and place each safeguard where information or authority makes it effective:

| Boundary | Safeguard purpose |
|---|---|
| untrusted/trust boundary | reject malformed or semantically invalid external input |
| parser/schema boundary | enforce structure, size, required fields, and decoding rules |
| domain/invariant owner | enforce business/state invariants exactly once at the authoritative owner |
| dangerous side-effect boundary | verify preconditions before irreversible or high-impact operations |
| operational boundary | fail safe, rate/limit, isolate, alert, or preserve evidence |

Independent layers are useful when they protect different failure modes. Repeating the same rule everywhere is not automatically defense-in-depth.

## Trust boundary validation

Validate both syntax and semantics when data crosses an untrusted or separately owned boundary, including internal APIs/queues when the receiver cannot rely on the sender's correctness. Do not confuse validation with authorization, output encoding, or other security controls.

## Invariant ownership

Put invariants at the component/domain owner that can keep state valid across all callers. Entry-point validation may improve errors, but it must not become the only enforcement when alternate callers can bypass it.

## Dangerous side effects

Before writes, deletes, deployments, migrations, filesystem operations, or external mutations, validate the preconditions that prevent the diagnosed failure. Prefer idempotency, dry-run, scope guards, and reversible operations when appropriate.

## Operational diagnostics

Add telemetry that makes recurrence observable when the failure could otherwise be silent. Do not log secrets/PII or add high-cardinality/unbounded data without an operational need.

## Verification

For each safeguard, test the failure class it owns. Where layers are intentionally independent, verify that bypassing one does not silently defeat the others. Do not weaken the original root-cause regression test merely because additional guards now stop the symptom earlier.
