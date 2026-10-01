# Gated Checkpoint Execution

Use this branch only when a parent controller has already accepted a bounded `workflow-plan/v2` gated-convergence plan or an equivalent explicit checkpoint contract.

This is an **execution adapter**, not a second planning system. Magia remains the sole producer/repair owner for production repository changes inside the active checkpoint. The controller owns checkpoint orchestration and promotion; an independent verifier/reviewer owns its own evidence.

## Entry contract

A checkpoint-candidate delegation must identify:

- workflow/plan identity and `checkpoint_id`;
- bounded checkpoint objective and authorized write scope;
- current source/reference and candidate identities when available;
- success criteria already frozen by planning/orchestration;
- expected gate classes and proving checks;
- protected paths/evidence;
- remaining repair budget.

If the packet asks Magia to change the checkpoint acceptance criteria, evaluator, gate requirements, domain ownership, or promotion policy, stop and return to the controller/Mago as appropriate.

## Candidate execution

1. Inspect only the context needed for this checkpoint.
2. Make the smallest sufficient production change inside the authorized scope.
3. Run Magia-owned targeted checks needed to catch immediate implementation defects. These checks are supporting execution evidence; they do not replace an independently required verifier gate.
4. Produce a candidate identity/fingerprint suitable for binding downstream gate evidence.
5. Return a `checkpoint-candidate` result and stop. Do **not** mark the canonical task/phase complete solely because the checkpoint candidate compiles or its local checks pass.

## Repair re-entry

When a controller returns failed gate evidence:

- require the same workflow/checkpoint identity plus the failed gate evidence identity;
- confirm the candidate or state materially changed before repeating work;
- repair production code only inside the checkpoint scope;
- preserve failed evidence rather than rewriting it as success;
- return a new candidate identity;
- assume every affected required gate must rerun for the new candidate.

Do not edit verifier tests, reviewer rubrics, frozen expected outputs, or gate criteria merely to obtain a pass.

## Promotion and closure

Checkpoint promotion is not a Magia self-approval. Magia may consume controller evidence stating that all required gates for the exact candidate passed and the checkpoint was promoted.

For a multi-checkpoint task:

- keep canonical task completion open until the controller reports all required checkpoints promoted;
- do not toggle a final task checkbox, emit completion handoff, or close the governed execution phase for an intermediate checkpoint;
- final Magia closure still requires the normal Magia validation/closure rules and current execution evidence.

If promotion evidence is stale, bound to another candidate, incomplete, or fabricated, stop as `blocked`.

## Output shape

Return at least:

- `execution_unit: checkpoint-candidate | checkpoint-repair | checkpoint-finalization`;
- workflow/plan identity;
- checkpoint id;
- candidate identity;
- production changes and scope;
- Magia-local checks with exact status;
- verifier/reviewer feedback consumed, if this was a repair;
- remaining unknowns/repair budget;
- `canonical_phase_completed: false` for non-final candidates/repairs.
