# Benchmark Health

Validate the benchmark before interpreting candidate performance. A broken task, tautological grader, contaminated holdout, or flaky environment can dominate the measured result.

Use `scripts/validate_benchmark_health.py` with schema v1 evidence. Record scenario-suite identity, suite role, distribution profile, isolation, gaming resistance, contamination risk, saturation state, grader health/calibration, and task-level reference/grader/ambiguity/flakiness checks.

## Gate semantics

- `pass`: no known health blocker; strong claims may proceed if every other comparison gate passes.
- `review`: benchmark is usable only for bounded/diagnostic interpretation; do not make a strong promotion claim from it alone.
- `fail`: benchmark evidence is not eligible for a strong capability claim.

A known reference/oracle solution should pass the intended grader for objective tasks. Unknown health is not equivalent to pass. Capability suites that are saturated should be refreshed or supplemented; historical regression cases remain valuable and should not be rewritten in place.

Treat contamination and gaming as lifecycle state. Preserve old suite identities, add new cases under a new identity, and never silently edit expected outcomes after seeing candidate failures.
