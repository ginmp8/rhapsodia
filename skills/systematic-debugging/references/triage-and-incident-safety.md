# Triage and Incident Safety

## At a Glance

- **Purpose:** Decide whether diagnosis can proceed normally or active impact requires mitigation first, and bound diagnostic risk.
- **Load when:** Users are affected now; availability, integrity, safety, or data loss is at risk; or proposed diagnostics touch production/sensitive data.
- **Decision impact:** Determines mitigation-before-RCA ordering, evidence preservation, authorization needs, and what diagnostic data may be collected.

## Contents

- Incident versus normal debugging
- Safe mitigation contract
- Evidence preservation
- Diagnostic safety gate
- Returning to diagnosis

## Incident versus normal debugging

Use the normal debugging workflow when delay does not materially worsen user impact, integrity, or safety. Use the incident path when continued failure creates meaningful harm.

Incident path:

`assess impact -> preserve cheap evidence -> apply reversible mitigation -> verify stabilization -> resume diagnosis -> permanent correction`

A mitigation is allowed before full causal proof. It must not be presented as the permanent fix or root-cause evidence by itself.

## Safe mitigation contract

Prefer actions that are:

- already tested or operationally understood;
- reversible;
- narrowly scoped;
- observable;
- unlikely to destroy forensic evidence;
- authorized for the environment.

Examples include rollback to known-good, traffic drain, feature disablement, failover, or load shedding when those controls are already safe in that system. Do not invent a risky recovery mechanism during an emergency.

## Evidence preservation

Before mitigation, when feasible without delaying safety-critical recovery, capture exact errors, relevant logs/traces, version/deploy/config identity, timestamps/ordering, affected scope, and current metrics/state. Record the mitigation itself so post-mitigation evidence is not confused with the original state.

## Diagnostic safety gate

Before adding instrumentation or running an experiment, ask:

- Could it expose credentials, tokens, PII, customer payloads, or proprietary data?
- Could it increase CPU, memory, I/O, network load, or outage severity?
- Could it perturb timing/scheduling and hide a race?
- Could it write/delete/migrate/rotate production state?
- Does it require explicit authorization?
- Is existing telemetry sufficient?

Collect the minimum evidence needed. Redact at collection time when possible; do not log full secrets or arbitrary environment dumps.

## Returning to diagnosis

After stabilization, reset the problem statement using the pre-mitigation evidence. Investigate why the failure occurred, whether the mitigation only masked it, and what permanent change prevents recurrence. Verify the permanent correction independently from the emergency mitigation.
