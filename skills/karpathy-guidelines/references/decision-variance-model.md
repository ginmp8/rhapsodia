# Decision Variance Model

Use this reference when a coding task contains choices that could be over-constrained in the name of consistency. The goal is to reduce unjustified variance while preserving useful engineering judgment.

## Control classes

Classify each material decision separately. Do not force an entire task into one class when it contains mixed decisions.

| Class | Use when | Primary control | Do not do |
|---|---|---|---|
| Mechanical | correctness can be checked objectively from artifacts or execution | script, parser, schema, type, validator, exact invariant | replace an objective check with prose or model preference |
| Heuristic | a stable default exists but legitimate exceptions remain | defaults, ordered rules, tie-breakers, explicit limits, stop conditions | present the default as universally correct |
| Judgment | the decision requires contextual trade-offs among evidence-backed criteria | rubric, evidence, criteria, uncertainty, independent review when impact is high | fabricate precision or hide disagreement behind a deterministic-looking rule |
| Subjective | multiple behaviorally valid outputs differ mainly by readability, naming, style, ergonomics, or preference | independent evaluation; explicit user preference may define acceptance criteria | let taste override correctness, safety, contracts, or executed evidence |

External nondeterminism such as changing documentation, dependency versions, clocks, services, or repository state is orthogonal to these four classes. Pin, snapshot, version, or record identity when it materially affects the answer.

## Classification test

Use the first matching rule that fits the specific decision:

1. If a command, parser, schema, type system, or validator can decide it without semantic interpretation, treat it as mechanical.
2. If there is a preferred default but evidence can justify exceptions, treat it as heuristic.
3. If competent engineers can disagree because different evidence or trade-offs deserve weight, treat it as judgment.
4. If the remaining difference is mainly taste or preference after behavior and constraints are equivalent, treat it as subjective.

When uncertain between two classes, choose the higher-variance class until stronger evidence justifies a lower one. Do not manufacture determinism.

## Mixed decisions

Split mixed decisions into smaller parts and control each at the lowest reliable layer.

Example: a refactor may contain all four classes:

- build succeeds: mechanical;
- use the existing project pattern before inventing a new abstraction: heuristic;
- decide whether the abstraction materially lowers complexity: judgment;
- choose between two equally clear names: subjective.

The strongest applicable objective constraint wins on its own axis. A subjective preference cannot make a failing test acceptable. A heuristic default can be overridden by concrete evidence. Judgment may select among mechanically valid alternatives but must not rewrite the mechanical result.

## Heuristic defaults and tie-breakers

For coding work, prefer these defaults unless evidence, explicit requirements, or a stricter domain rule overrides them:

1. preserve correctness, safety, and explicit contracts;
2. preserve public behavior unless the requested change requires otherwise;
3. change fewer artifacts;
4. reuse an existing project pattern;
5. add fewer new dependencies or abstractions;
6. prefer the narrower reversible change;
7. prefer the strongest feasible validation with the smallest relevant scope;
8. when options remain behaviorally equivalent, follow the user's explicit preference or the local codebase convention.

These are tie-breakers, not universal truths. Record the evidence for overriding one when the override materially changes scope or risk.

## Judgment rubric

For non-trivial engineering judgment, evaluate only dimensions relevant to the request. Typical dimensions are:

- correctness and failure modes;
- compatibility and contract stability;
- security and privacy;
- data integrity and concurrency;
- resilience and operability;
- performance with measurements or a named measurement gap;
- complexity and maintainability;
- testability and observability;
- migration and rollback risk.

A judgment should identify the evidence, the criterion being applied, and the consequence. If material evidence is missing, downgrade the claim to a hypothesis, risk, or validation gap instead of forcing a verdict.

## Subjective review

Treat readability, naming, stylistic elegance, API aesthetics, and developer ergonomics as subjective unless they violate an explicit project convention or measurable contract.

When the distinction matters:

- separate subjective suggestions from defect findings;
- do not inflate severity for taste;
- prefer user or repository conventions when visible;
- when subjective quality materially affects acceptance, use a fresh reviewer that did not generate the candidate, or explicit user review;
- if independent evaluation is unavailable, do not claim subjective superiority; label the conclusion as judgment or preference;
- for trivial low-impact style choices, follow explicit user or repository preference without pretending that choice proves higher quality.

## Evidence precedence

Use this precedence when controls conflict:

`executed objective evidence / hard contract > inspectable artifact evidence > bounded heuristic > contextual judgment > subjective preference`

This is not a universal priority across unrelated dimensions. For example, a user preference can decide naming when all mechanically valid options are equivalent, but it cannot override a failed security or correctness gate.

## Reporting

Do not expose this classification table in every answer. Use it internally to choose the control layer. Surface the classification only when it explains a material trade-off, disagreement, limitation, or validation gap.

For reviews, distinguish:

- defect/risk: evidence-backed negative impact;
- heuristic recommendation: preferred default with valid exceptions;
- judgment call: contextual trade-off under stated criteria;
- subjective suggestion: preference among otherwise valid alternatives.

## Anti-patterns

Reject these forms of pseudo-reproducibility:

- turning style preferences into hard failures;
- assigning exact numeric scores to qualitative trade-offs without a calibrated rubric;
- forcing one architecture pattern when multiple satisfy the contract;
- treating a heuristic as mandatory after contrary evidence appears;
- using model confidence as a substitute for tests or measurements;
- hiding uncertainty to make outputs look consistent;
- adding scripts that merely encode the model's previous opinion;
- claiming subjective superiority from the generator alone when subjective quality materially affects acceptance.
