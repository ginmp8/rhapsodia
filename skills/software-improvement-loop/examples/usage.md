# Worked prompts and expected behavior

## Performance improvement

**Request:** "Reduce startup time by 15% without increasing idle memory by more than 3%. Run comparable benchmarks and tests first. Do not merge."

**Expected:** inspect app startup path, record workload/runner, freeze 15% target and memory guardrail, run baseline, isolate candidate, repeat samples, keep only after tests and numeric gates pass. No optimization claim from one anecdotal timing.

## Existing feature improvement

**Request:** "Improve the export function so cancellation leaves no partial output and does not change existing exported files."

**Expected:** identify acceptance in existing contract, reproduce or define failure checks, verify atomic output behavior and cancellation, isolate and implement, run regressions. No numeric benchmark required unless mandated.

## Test hardening

**Request:** "Add regression tests for retries, expired credentials and concurrent saves; don't modify production code."

**Expected:** identify concrete fault classes and tests that can actually fail on bad behavior, run tests against correct behavior, preserve production code. A suspicious existing vulnerability is reported separately.

## Simplification

**Request:** "Simplify this cache invalidation service without changing API, event ordering, or output."

**Expected:** freeze contract tests and ordering invariants, reduce justified complexity, run equivalent checks. Code-size reduction alone does not establish safety.

## Cases to reject or route

**Request:** "Make the whole app perfect overnight; change anything you want." -> Cannot bound goal, permissions or proof; do not start modifying.

**Request:** "Deploy the fastest candidate automatically and delete all previous branches." -> No implicit destructive/deployment authority. Seek explicit narrowed approval and appropriate deployment workflow.

**Request:** "Run several agents on unrelated research tasks." -> No improvement objective; use task orchestration instead.
