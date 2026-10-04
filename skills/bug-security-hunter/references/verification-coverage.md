# Verification Coverage

Use this reference for substantive PR, project, flow, or security reviews when review completeness matters. Coverage is an accounting contract, not a mandate to execute every technique on every target.

## Canonical techniques

Account for these techniques using the strongest available evidence. This is a threat modeling and included code verification coverage contract:

1. `threat-modeling` - design-level threats, trust boundaries, assets, actors, abuse paths.
2. `automated-testing` - unit/integration/contract/system tests relevant to the changed risk.
3. `static-analysis` - source/config/IaC analysis or equivalent static checks.
4. `hardcoded-secret-detection` - source, config, fixtures, examples, CI, IaC, logs, and history when relevant.
5. `built-in-protections` - compiler/runtime/framework/platform protections that materially affect the risk.
6. `black-box-testing` - externally observable behavior against a runnable target when useful.
7. `structural-testing` - branch/path/state/coverage-informed tests or source inspection.
8. `historical-regression` - prior incidents, fixed bugs, regression cases, or equivalent known-failure corpus.
9. `fuzzing` - coverage/property/mutation fuzzing where a parser, protocol, serializer, validator, or high-dimensional input surface makes it useful.
10. `web-scanning` - dynamic web/API scanning only when a safe runnable target exists and the technique is relevant.
11. `included-code-review` - third-party libraries, packages, services, generated/runtime artifacts, and supply-chain inputs.

## Per-technique record

For each canonical technique record:

- `applicable`: `true` or `false`;
- `status`: `measured`, `observed`, `supplied`, `planned`, `blocked`, or `out-of-scope`;
- evidence: the command/result/artifact/source inspected, or why no runtime evidence exists;
- rationale: why the technique is or is not material for this scope.

Use `measured` only for an executed check. Static source review is `observed`; external scanner output not reproduced by the reviewer is `supplied`. A `not-applicable` technique should use `applicable=false` and `out-of-scope` with a concise rationale rather than being silently omitted.

## Completion rules

`complete-for-scope` means every canonical technique has an explicit disposition and every technique marked applicable is supported by `measured`, `observed`, or `supplied` evidence adequate for the review decision. If a material applicable technique is only `planned` or `blocked`, coverage is `partial` or `blocked`; do not approve merely because no defect was found elsewhere.

Do not confuse technique coverage with proof of correctness. High coverage can still miss bugs; low coverage can still expose valid findings.

## Output shape

```text
| Technique | Applicable | Status | Evidence | Rationale |
|---|---:|---|---|---|
| threat-modeling | yes | observed | trust-boundary review | auth-sensitive path |
| fuzzing | no | out-of-scope | no parser/input surface | bounded config change |
```

For quick triage, include only material techniques and state that the coverage matrix is intentionally partial.

## Research basis

Adapted from NIST IR 8397's minimum developer-verification techniques. The skill uses the techniques as an applicability/accounting model, not as a universal requirement to execute every technique on every review.
