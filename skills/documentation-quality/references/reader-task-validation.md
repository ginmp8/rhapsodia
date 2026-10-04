# Reader and task validation

Load this reference when the review claims task success, usability, reader efficiency, or reduced confusion. This layer is optional for ordinary documentation edits and must remain separate from mechanical, source-fidelity, runtime-command, and editorial evidence.

## Evidence boundary

Do not infer reader success because:

- Markdown lint passed;
- local links resolve;
- technical claims match source code;
- a documented command executed successfully;
- the reviewer believes the prose is clear.

Those are useful evidence in other layers, not reader/task-outcome proof.

## Before/after task comparison

When comparing baseline and candidate:

1. define the reader profile, goal, starting state, and task scenario before candidate results are inspected;
2. preserve the same scenario, inputs, success condition, and material environment across both arms;
3. freeze or hash evaluator/task artifacts when feasible;
4. record deviations instead of silently adapting the task to the candidate;
5. do not claim improvement from a single subjective impression when stronger evidence is required.

If the scenario or evaluator changes materially, invalidate or re-baseline the comparison.

## Useful observations

Use only metrics that the execution actually produces. Examples include:

- task completion or failure;
- blocking points;
- wrong turns caused by the documentation;
- unnecessary steps;
- lookup effort or repeated navigation;
- time-on-task when actually measured;
- reader-reported confusion or satisfaction when actually collected.

Do not invent numeric thresholds or usability scores for a target that does not define them.

## Evidence labels

- `measured`: a task run, study, instrument, or tool produced the result in the current run.
- `observed`: the reviewer directly observed a concrete reader/task interaction without a formal measurement.
- `supplied`: the user provided study/support/feedback evidence that was not independently rerun.
- `inferred`: a bounded editorial inference about likely task impact.
- `planned`: a task/usability check was defined but not executed.
- `blocked`: a required task/usability check could not be run.

Use `not-run` in command/gate tables when no task execution occurred. Never upgrade `inferred` usability to `measured` for presentation quality.

## Completion rule

Reader/task validation is complete only for the claim it actually tested. A successful quickstart task does not establish that all reference material is discoverable, and one reader profile does not prove success for all audiences.
