# Prompt Architecture Workflow

Use this reference for creation and improvement work when the prompt needs more than a small wording change.

## 1. Intent Frame

Capture these facts before drafting:

- task: what the model must do;
- actor: who the model is acting as, if any;
- audience: who will consume the output;
- inputs: files, text, URLs, repositories, data, forms, messages, or examples;
- constraints: style, policy, tools, latency, format, length, citations, language, and exclusions;
- success criteria: what a correct answer must satisfy;
- failure cases: what the prompt must avoid.

Proceed with explicit assumptions when a gap is low-risk. Ask only when the missing fact changes the prompt materially.

## 2. Prompt Audit Pattern

For an existing prompt, inspect in this order:

1. Objective clarity: is the first instruction concrete and actionable?
2. Role fit: does the role improve execution, or is it decorative?
3. Context completeness: are facts, definitions, and constraints available before they are needed?
4. Tool rules: are tool triggers and prohibitions explicit?
5. Workflow order: does analysis happen before conclusions and final answers?
6. Output contract: is the final format precise enough to test?
7. Examples: are examples representative, consistent, and placed after the rules they illustrate?
8. Conflict scan: do any MUST, NEVER, default, and exception rules contradict each other?
9. Safety and privacy: does the prompt avoid secrets, hidden reasoning disclosure, unsafe actions, and unverifiable claims?
10. Validation readiness: can a tester decide pass or fail from the written criteria?

## 3. Creation Pattern

Create prompts with this default structure. Remove sections that do not add execution value.

1. One-line task instruction.
2. Context and role, if helpful.
3. Inputs and assumptions.
4. Workflow or decision tree.
5. Tool and source rules.
6. Constraints and prohibited behaviors.
7. Output format.
8. Examples.
9. Notes, edge cases, and stop conditions.

Prefer a clear first line over a title. The first line should tell the model exactly what to do.

## 4. Improvement Pattern

When rewriting an existing prompt:

- preserve original intent, domain vocabulary, constants, examples, and required constraints;
- preserve structure when it is already usable, especially for long or highly governed prompts;
- replace vague directions with testable actions;
- move conclusions, classifications, or recommendations after analysis steps;
- convert implicit expectations into explicit output-format rules;
- remove duplication and conflicting instructions;
- add examples only for unstable or high-variance outputs;
- document any intentional behavior change.

## 5. Minimal vs Structural Rewrite

Use a minimal rewrite when:

- the prompt has a clear structure;
- the user's requested change is narrow;
- only wording, output format, or one rule is defective.

Use a structural rewrite when:

- the prompt mixes role, task, examples, and output rules in a confusing order;
- the output format cannot be tested;
- requirements conflict;
- examples contradict the instructions;
- the prompt asks for conclusions before evidence or reasoning.

## 6. Prompt Tester Loop

After drafting, test with one or more realistic scenarios:

1. State the scenario and inputs.
2. Execute the draft literally as a model would.
3. Identify ambiguity, missing context, conflicts, and output-format drift.
4. Revise the prompt only where a defect is linked to a concrete failure.
5. Repeat up to three cycles when material defects remain.

A validation cycle is successful when no critical ambiguity remains, the output format is enforceable, and the tester can identify a clear path to completion.
