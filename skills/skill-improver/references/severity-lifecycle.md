# Severity and Lifecycle Contract

Use this reference for deterministic triage, iteration state, completion, and cancellation semantics.

## Finding taxonomy

Classify each confirmed finding before mutation:

| Severity | Meaning | Acceptance effect |
|---|---|---|
| `critical` | Can invalidate target identity, safety, evaluator integrity, package loading, protected evidence, or recovery guarantees. | Blocks mutation/acceptance until resolved or explicitly out of scope. |
| `major` | Material regression or defect in activation, scope, semantics, compatibility, validation, portability, delivery, or a required workflow contract. | Blocks final acceptance. |
| `minor` | Bounded polish or maintainability issue that does not change a hard contract. | Non-blocking; fix only when evidence justifies the complexity. |
| `needs-verification` | Evidence is insufficient to classify reliably. | Do not auto-fix or count as resolved. Gather evidence or defer explicitly. |

Tie-breakers:

1. Prefer direct observable failure evidence over inferred severity.
2. If one defect affects multiple areas, use the highest supported severity and record the impacted areas instead of duplicating the finding.
3. Do not promote a finding merely because it sounds risky; use `needs-verification` when the failure mode is plausible but unconfirmed.
4. Process `critical` before `major`, and `major` before `minor`. Within a severity, order by stable diagnostic code or canonical subject path when available.
5. A numeric score never overrides a blocking `critical` or `major` finding.

## Iteration state

The canonical runner owns improvement state under `.skill-improver/`:

- `runs.jsonl`: append-only iteration decisions;
- `stop`: graceful cancellation request;
- final report file; the default filename is improvement-report.md;
- benchmark/source evidence under the same state root when configured.

Do not create a second session-state implementation. `scripts/skill_improver_status.py` derives status from these canonical artifacts.

Default autonomous budget is **3** iterations. A user-supplied finite budget overrides it. Unbounded execution requires explicit `--infinite` plus `--max-iterations 0`.

## Completion and stop semantics

Use these final states consistently:

- `accepted`: a candidate passed the frozen evaluator, required gates, and change-gate policy and was retained as the last-good state;
- `completed`: the configured workflow completed without a blocking failure;
- `max-iterations-reached`: the finite budget ended before another iteration could start;
- `patience-reached`: repeated rejected hypotheses reached the configured patience limit;
- `cancelled`: a graceful stop request was observed before the next candidate;
- `blocked`: a hard precondition or required gate could not be satisfied;
- `failed`: execution/validation failed and no safe accepted state can be claimed.

Cancellation preserves the last accepted state and never converts an in-flight or rejected candidate into completion.


## Review-fix-review loop

For each bounded candidate:

1. review and classify findings;
2. select one evidence-backed causal hypothesis;
3. apply the smallest coherent fix;
4. rerun the same narrow gate;
5. run adjacent gates only after it passes;
6. accept or revert;
7. append the decision evidence;
8. stop according to the state rules above.

Stop a repair branch after two consecutive non-improving rounds on the same objective failure set unless new evidence materially changes the diagnosis.
