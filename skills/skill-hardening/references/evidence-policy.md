# Evidence Policy

Use this reference when a hardening run includes research, measured validation, benchmark evidence, or claims about package readiness.

## Evidence hierarchy

Prefer evidence in this order:

1. target package files and current filesystem state;
2. user-provided constraints, failed prompts, prior outputs, or benchmark reports;
3. target-domain repository truth or official project documentation when the skill depends on an external tool or platform;
4. current public skill-format guidance when the weakness concerns skill structure, activation, progressive loading, packaging, or validation;
5. model judgment only for prioritization, never as sole proof that a gate passed.

## Research use

Use research only to answer a concrete weakness found during inspection, such as trigger ambiguity, missing output contracts, weak progressive loading, insufficient scenario coverage, or unclear packaging expectations. Do not add generic excerpts or long background summaries to the target package.

When external research is used:

- record which sources influenced the change in the final report;
- prefer official docs or primary repositories over commentary;
- reconcile conflicts against the target skill's existing purpose and user constraints;
- avoid hardcoding time-sensitive facts unless they are essential and dated.

## Measured versus proposed claims

A result is measured only when it was executed in the current run or supplied as execution evidence by the user. Scenario suites, benchmark plans, evaluator rubrics, and acceptance gates are proposed until prompts or tests are actually run and decisions are recorded.

Never claim:

- scenario precision, recall, robustness, or pass rate from a planned suite;
- package readiness before folder and archive validators pass;
- script correctness before a representative run or syntax check succeeds;
- benchmark improvement when the baseline metric is already saturated unless an auxiliary non-saturated metric improved.

## Evidence record minimums

For applied hardening or package delivery, preserve or report:

- baseline inventory and audit results;
- hardening map with hypotheses and gates;
- changed files;
- commands executed with pass/fail outcomes;
- final validator and package results;
- residual risks and unmeasured behavior.
