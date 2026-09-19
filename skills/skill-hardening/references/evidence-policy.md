# Evidence Policy

Use when a run includes research, measured validation, benchmark evidence, or readiness claims.

## Evidence order

1. Target package files and current filesystem.
2. User constraints, failed prompts, prior outputs, benchmark reports.
3. Target-domain repository truth or official docs when the skill depends on an external tool/platform.
4. Current public skill-format guidance for structure, activation, progressive loading, packaging, or validation gaps.
5. Model judgment only for prioritization, never sole proof that a gate passed.

## Research

Research only concrete inspection gaps: trigger ambiguity, missing output contracts, weak progressive loading, thin scenario coverage, unclear packaging expectations. Do not add generic excerpts or background summaries.

When external research is used: record sources in the final report; prefer official docs/primary repos; reconcile conflicts against purpose and user constraints; avoid undated time-sensitive facts unless essential.

## Measured vs proposed

A result is measured only if executed in this run or supplied as execution evidence. Scenario suites, benchmark plans, evaluator rubrics, and gates stay proposed until prompts/tests run and decisions are recorded.

Never claim scenario precision/recall/robustness/pass rate from a planned suite; package readiness before folder/archive validators pass; script correctness before a representative run or syntax check; benchmark improvement when baseline is saturated unless an auxiliary metric improved.

## Claim layers and labels

Keep four evidence layers separate:

- structural evidence: package shape, references, schemas, hashes, and static gates;
- behavioral evidence: executed scenarios and evaluator decisions;
- runtime evidence: actual application, browser, tool, or integration behavior;
- perceptual evidence: independent human or image-capable review.

Label material claims as `measured`, `observed`, `derived`, `supplied`, `planned`, or `blocked`. Do not upgrade a weaker label because the result is plausible. A static maturity score is structural evidence, not proof of behavioral improvement.

## Evidence record

For applied hardening or package delivery, report immutable baseline identity, candidate identity, evaluator identity/verification, baseline inventory/audit, hardening map with hypotheses/gates, changed files, commands with pass/fail/not-run outcomes, final validator/package results, residual risks, and unmeasured behavior.
