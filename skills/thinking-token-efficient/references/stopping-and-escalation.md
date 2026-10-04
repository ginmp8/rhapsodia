# Stopping and Escalation

## Purpose

Stop when the current answer/decision is sufficiently supported, not merely because a token budget is low or confidence feels high. Continue only when additional work can satisfy an unmet obligation or plausibly change a material conclusion.

## Sufficiency gate

After each material reasoning or tool step, check the applicable signals:

1. **Obligations:** required constraints, evidence, citations, safety, compatibility, and output fields are satisfied.
2. **Stability:** the answer/decision is not changing without new evidence.
3. **Evidence:** material claims have adequate provenance/freshness for the task.
4. **Contradictions:** no unresolved conflict can materially alter the result.
5. **Validation:** required checks are executed or honestly labeled not-run/blocked.
6. **Completion:** no truncation, incomplete tool result, partial file read, or missing required section remains.
7. **Information gain:** another branch/tool/read has a plausible path to change correctness, safety, validation, or the decision.

Stop only when the applicable obligations are satisfied and further expected information gain is negligible.

## Do not stop on one signal

Confidence alone is not sufficient. High confidence, answer repetition, or a stable draft alone is not sufficient when a required citation, validation, constraint, or contradiction remains unresolved. Use multiple applicable signals and the frozen obligations.

## Continue or escalate when

- evidence conflicts or source authority is unclear;
- a required current fact is unverified;
- a command/test/validator failed or was not run when required;
- the output is truncated/incomplete;
- a new tool result changes assumptions;
- a security, privacy, legal, financial, medical, or irreversible-risk issue appears;
- the selected approach no longer satisfies the acceptance criteria.

When continuation is needed because the problem became harder, increase reasoning effort rather than merely making the private representation longer.

## Reopening resolved branches

Do not reconsider a resolved alternative without new evidence or a failed acceptance check. Reopen it only when a named fact, constraint, dependency, or evaluator result changes.

## Bounded stop

If further progress requires unavailable evidence/capability, would cross scope/authority, or two diagnostic repairs fail to improve the same objective problem, stop with a bounded limitation. Do not random-search for token savings or weaken a gate to continue.
