# Mode acceptance and counterexamples

## Shared routing

One improvement objective with a bounded change and falsifiable outcome is the unit of work. Prefer direct execution for one small task. Multiple objectives can share a run only when one set of frozen criteria covers all of them; otherwise separate experiments. Requirements are user/repository-owned, not invented by this skill.

## Performance

- Freeze the primary metric (unit, measurement point, direction, threshold), workloads, environment and guardrails before candidate edits. Record test and benchmark versions.
- Inspect profiles or traces to locate an evidenced bottleneck before changing code. Do not equate fewer lines, extra caching, or a framework upgrade with improvement.
- Require repeated measurements under comparable conditions. Use `compare_metrics.py` for a **conservative heuristic**; it is not a statistical significance or causal inference engine.
- Accept only when target metrics meet the frozen improvement threshold, guardrails have no material regression, and behavior tests pass. If measurements are noisy, mark inconclusive and rerun within the budget or stop.

## Feature

- Obtain acceptance criteria from the user, spec, existing contract, or concrete bug/feature behavior. Do not broaden the product's intent under the label of improvement.
- Define a check that would fail for a materially incorrect feature and execute it on the candidate. Test invalid input, relevant failures, concurrency/idempotency and integration boundaries when applicable.
- Include UI references, accessibility, responsive behavior and perceptual verification only when requested or necessary to prove the feature's intended outcome.
- No performance gain is required unless the objective states one; quantify only genuinely measurable properties.

## Test hardening

- Name the defect class each added test can detect. Observe it fail against a relevant known-bad condition, a controlled mutation, or a verified historical failure whenever feasible; cleanly restore the original afterward.
- Prefer boundary/integration checks when mocks would hide the fault. Prioritize negative input, errors, retry, cancellation, concurrency, compatibility and authorization where relevant.
- Do not equate total test count or coverage with test effectiveness. Verify the new test passes on correct behavior and the whole relevant suite remains green.
- Do not change production implementation unless the user independently authorized bug fixing or a different mode requires it. Distinguish an existing bug found by testing from a new regression.

## Simplification

- Define preserved public contracts, behavior, state, performance constraints and dependency assumptions. Use characterization/integration tests as needed.
- Prefer deleting accidental complexity and narrowing interfaces over speculative architecture or dependency migrations.
- Use meaningful complexity evidence (e.g., fewer independent branches or clearer boundaries); line counts are supporting evidence only.
- If behavioral equivalence is unproven, do not describe the change as a safe refactor. Report the unknown and defer acceptance.

## Non-activation / handoffs

- "Invent an app for my idea" -> product requirements/design, not an improvement loop.
- "The service crashed; find the root cause" -> diagnostic workflow until a fix objective and oracle exist.
- "Orchestrate ten agents for arbitrary tasks" -> runtime orchestration, not software improvement.
- "Review this PR for vulnerabilities" -> security review, not candidate experimentation.
- "Deploy the change" -> release/deployment workflow; no implied deployment permission.
