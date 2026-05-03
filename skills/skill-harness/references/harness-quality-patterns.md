# Harness Quality Patterns

Use when scenario or evaluator quality matters beyond structural package validity, especially for high-risk skills, saturated static scores, regression prevention, or user-provided external testing guidance.

These patterns adapt fuzzing-harness discipline to skill harnesses: a harness is only useful if its inputs reach decision-relevant behavior, remain deterministic enough to compare, and expose failures instead of hiding them.

## Target Entry Points and Coverage

Select scenarios from explicit entry points in the target skill: activation triggers, negative boundaries, mode selection, mutation rights, blocked paths, validators, packaging, output contract, stop conditions, and known incidents. Prefer narrow scenario groups for unrelated behaviors; use combined/interleaved scenarios only when the same corpus can exercise related operations without making failures hard to attribute.

Coverage checklist:

- Every supported mode has at least one normal-path scenario and one failure/edge scenario.
- Every blocked path or forbidden claim has at least one adversarial or regression scenario.
- Every output-contract section has an acceptance criterion.
- Every script or validator mentioned in workflow has a command or planned execution check.
- Every package/readiness claim has a package-validation or stop-condition scenario.

## Input Model and Corpus Design

Treat scenario prompts, fixtures, uploaded files, links, reports, and command outputs as the harness input corpus. For each scenario group, define the input shape before evaluating outputs: minimal target folder, malformed target, missing `SKILL.md`, multiple `SKILL.md` files, zip vs folder, saturated benchmark, failed validator, unavailable source truth, read-only path, and package-request variants.

Use structured inputs when free-form prompts would miss important branches: include explicit `mode`, `mutation_mode`, `risk`, `expected_artifacts`, and `blocked_paths` fields in scenario metadata when useful. Keep corpus entries small and focused unless interaction between operations is the behavior under test.

## Determinism and Isolation

Harness results must be reproducible enough to compare baseline and final behavior. Before claiming measured scenario performance, record run ID or timestamp, model/tool environment when available, target version/hash when practical, evaluator criteria, allowed sources, blocked paths, and command outputs. Reset or isolate mutable state between runs: generated reports, temporary package directories, caches, previous zips, and baseline evidence must not leak into final validation.

Non-deterministic or unavailable dependencies must be declared as `unknown`, `blocked`, or `planned`; they must not be converted into measured evidence.

## Throughput and Observability

Prefer fast deterministic gates before semantic review: structure validation, JSON schema, unique scenario IDs, required type coverage, missing references, package exclusions, and script syntax. Keep human or LLM judging for semantic quality only, and label it separately. Avoid excessive logging in scripts; write concise reports that expose the failing gate, file, and scenario ID.

Useful auxiliary metrics when static scores are saturated:

- entry-point coverage count;
- mode-by-risk scenario matrix coverage;
- output-contract criteria coverage;
- blocked-path/adversarial coverage;
- number of deterministic gates added or preserved;
- package validation status and exclusion correctness;
- unresolved risks or unknowns count.

## Anti-Patterns

Avoid these harness failures:

| Anti-pattern | Problem | Correction |
|---|---|---|
| Broad prompt-only scenarios | Misses mode, file, and artifact branches | Add structured metadata and acceptance criteria |
| Unrelated interleaved scenarios | Failures are hard to attribute | Split by behavior unless interaction is intentional |
| Hidden mutable state | Baseline/final comparison is contaminated | isolate temp dirs, zips, reports, and caches |
| Measuring planned scenarios | Fabricates precision, recall, or pass rate | report coverage only until outputs are executed |
| Heavy or noisy validators | Slow, brittle validation hides signal | keep deterministic gates focused and concise |
| Editing fixtures to pass | Invalidates evaluator freeze | treat evaluator changes as a separate hypothesis |
| Package claims without archive check | User receives unverified artifact | run package validator and report path only on pass |
