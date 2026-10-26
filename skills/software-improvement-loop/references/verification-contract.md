# Verification contract and oracle integrity

## Prepare an evaluation contract

Before modifying a candidate, record the claim and its falsifying observation: setup, input, action, expected result, relevant failure signal, test command, environment and scope. Freeze target-specific criteria, test/fixture identities and acceptance thresholds. When evaluation must change for a legitimate scope correction, explicitly start a **new** experiment baseline rather than presenting results as comparable.

## Mandatory review after each attempt

1. Run the focused check that observes the changed behavior; do not accept mocks when a real boundary is material.
2. Run affected regressions (unit/integration/system as relevant), not only the freshly added test.
3. Examine the entire candidate diff, especially altered tests, assertions, expected outputs, timeouts, benchmark harnesses, thresholds, skipped checks and configuration. Compare against the frozen evaluation contract.
4. Check invalid input, failures, retry/cancel, races and security/permission boundaries according to the changed path's risk.
5. If external UI behavior matters, validate interaction, accessibility and visual state against authorized references. Perceptual confidence is distinct from deterministic proof.
6. Keep evidence from a checker/reviewer separate from the implementing agent's own statement; an agent asserting 'passed' without executing commands is not a test result.

## Rules that cannot be optimized away

- Never weaken, delete, skip, mute, or silently rewrite required tests or their expected outputs to get green. Legitimate test changes require documented evidence and evaluation re-baselining if they affect acceptance.
- Never disable a CI check, relax a timeout/threshold, or change benchmark inputs to conceal a regression.
- Candidate passing after fixing a pre-existing failing test is not proof that all related issues are resolved.
- A failed, flaky, inaccessible or unrun required gate is not a pass. Distinguish code failure, harness failure, environment failure and unknown.
- Never claim independent review merely because the same model ran twice. Isolation can help but independence requires clear identity/evidence controls.

## Boundaries

Use specialist or project-specific testing tools when present; never require a particular TDD framework or external service. Respect existing project test runners and package lockfiles. High-risk auth, schema/data, production and destructive changes require their own authorization and review, regardless of a favorable metric.
