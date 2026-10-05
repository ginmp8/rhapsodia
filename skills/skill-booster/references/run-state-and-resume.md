# Run State and Resume Contract

## At a Glance

Read this file when the active workflow needs **Run State and Resume Contract**. The decision-critical scope and section map are surfaced here so a partial preview is useful before deeper reading.

Primary topics: Canonical state, Resume rule, Phase ordering, Budget and stop rules.

## Contents

- Canonical state
- Resume rule
- Phase ordering
- Budget and stop rules


Use this contract for long, interrupted, resumed, or multi-context optimization runs. Keep run state outside the target candidate so a candidate cannot rewrite its own history.

## Canonical state

Record one `optimization-run-state` with:

- stable `run_id`, mode, target name, baseline identity, and current candidate identity;
- current canonical phase and per-phase state;
- frozen evaluator/source-set identities;
- candidate-bound evidence and explicit invalidations;
- active transformation id, open/terminal material findings, finite budgets, checkpoint, blockers, and legal next actions.

Use `assets/templates/optimization-run-state.json.template` and validate with `scripts/validate_run_state.py`.

## Resume rule

On resume, verify the stored baseline/candidate/evaluator/source identities before trusting prior evidence. Candidate-bound evidence whose candidate identity differs from the current candidate is stale unless its id is explicitly listed in `invalidated_evidence_ids` or the evidence is marked historical. Never silently refresh a stored identity after drift.

A resumed run may continue only from a legal phase/action with no unresolved blocker and no exhausted budget relevant to the next action. If identity drift is intentional, re-baseline explicitly and invalidate affected downstream evidence.

## Phase ordering

Use only: `establish -> diagnose -> select -> transform -> evaluate -> prove`. A later phase cannot be active while an earlier required phase is `not-started`, `fail`, or `blocked`.

## Budget and stop rules

Track consumed transform cycles, candidates, and expensive evaluations against finite maxima. Exhaustion is a stop condition, not permission to widen the budget silently. A user-approved budget change creates a new checkpoint/evidence record.
