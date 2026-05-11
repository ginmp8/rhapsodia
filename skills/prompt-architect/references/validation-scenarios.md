# Validation Scenarios

Use this reference when testing prompt behavior or building a scenario suite.

## Scenario Types

Create a balanced set when validation matters:

- activation scenario: normal request the prompt should handle;
- edge scenario: unusual but supported input;
- ambiguity scenario: missing information that should trigger assumptions or a question;
- conflict scenario: competing requirements that must be prioritized;
- negative scenario: request outside scope that should be refused or redirected;
- regression scenario: behavior the old prompt handled well and the new prompt must preserve.

## Scenario Record

Each scenario should include:

- id;
- type;
- user input;
- required behavior;
- expected output traits;
- failure signals;
- priority.

## Prompt Tester Procedure

For each scenario:

1. Read the draft prompt literally.
2. Identify the first action the model would take.
3. Check whether required inputs are available.
4. Produce or outline the expected output shape.
5. Mark defects: ambiguity, conflict, missing context, wrong tool trigger, output drift, unsafe behavior, over-broad scope, or untestable criterion.
6. Decide pass, pass with reservations, fail, or blocked.

## Defect Severity

- critical: causes unsafe behavior, wrong task execution, impossible output, or contradiction.
- major: likely causes inconsistent output or repeated clarification.
- minor: wording, ordering, or style issue that does not block completion.

## Iteration Rule

Revise the prompt only for defects linked to a scenario failure. Do not expand scope merely because the tester imagined a possible future use case.
