# Prompt Quality Rubric

Use this rubric for review-only mode, complex rewrites, and quality gates. Score each dimension from 1 to 5.

## Dimensions

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| objective | vague or decorative | task is understandable but broad | first instruction is concrete, testable, and action-oriented |
| context | missing essential facts | enough context with gaps | all necessary facts, definitions, and assumptions are available |
| specificity | generic advice | mixed concrete and vague rules | every critical behavior is explicit and actionable |
| structure | disordered or conflicting | usable but uneven | sections follow execution order and reduce ambiguity |
| reasoning order | conclusions first or unclear | mostly correct | analysis, evidence, and checks precede conclusions |
| examples | absent when needed or misleading | helpful but incomplete | representative, consistent, and placeholder-safe |
| output format | unspecified | partially specified | exact structure, syntax, length, and constraints are defined |
| source handling | unsupported claims | some source rules | authority, recency, conflict resolution, and citation rules are clear |
| tool behavior | tools omitted or ambiguous | some tool rules | triggers, inputs, prohibitions, and fallback paths are explicit |
| safety and privacy | unsafe or secret-leaking | basic safety | avoids hidden reasoning, secrets, unsafe actions, and unverifiable claims |
| validation readiness | cannot be tested | partially testable | pass/fail criteria and scenarios are clear |

## Verdicts

- **approve**: no critical issues; most dimensions are 4 or 5.
- **approve with reservations**: usable, but one or more non-critical dimensions need improvement.
- **reject**: critical ambiguity, conflicting requirements, unsafe instruction, missing output contract, or impossible validation.

## Critical Issues

Flag as critical when any of these are present:

- conflicting MUST and NEVER rules;
- final answer required before required analysis;
- no clear output format for a structured task;
- examples contradict rules;
- source requirements are impossible or unverifiable;
- hidden chain-of-thought disclosure is requested;
- the prompt directs the model to ignore safety, privacy, or tool restrictions;
- the prompt cannot be tested against any observable success criterion.

## Rewrite Prioritization

Prioritize fixes in this order:

1. Safety, privacy, and policy constraints.
2. Objective and success criteria.
3. Output format.
4. Conflict removal.
5. Workflow order.
6. Source and tool rules.
7. Examples and style refinements.

Do not optimize style before the prompt has a clear objective, constraints, and output contract.
