# Review Evidence and Reproducibility Contract

## Purpose

Use this reference for code reviews, architecture reviews, production/security gates, and any claim about correctness, security, performance, reliability, or validation. It constrains process and evidence without pretending that engineering judgment can be fully deterministic.

## Evidence labels

Use exactly one primary label for each validation claim:

| Label | Meaning |
|---|---|
| `executed` | command, test, analyzer, build, benchmark, or runtime probe was run in the current work and its result observed |
| `observed` | code, configuration, logs, or output were directly inspected |
| `supplied` | result was provided by the user/tool/source but not independently rerun |
| `inferred` | conclusion follows from evidence but was not directly measured |
| `planned` | recommended validation/change has not been executed |
| `blocked` | required evidence could not be obtained |

Do not upgrade `supplied`, `inferred`, `planned`, or `blocked` to `executed` for presentation convenience.

## Target and source identity

For reviews tied to repository or file contents, identify the exact revision/snapshot when available. Prefer immutable commit/object bytes over a moving branch or dirty working tree for claims that must be repeatable. If the reviewed source changes after inspection, do not silently reuse earlier findings as if they describe the new bytes; re-run the affected review/validation or explicitly mark the evidence stale.

## Finding identity

A material finding should be reproducible as:

`location/subject -> violated contract or failure condition -> evidence -> impact -> smallest supported fix`

If the failure condition cannot be stated, treat the item as an observation or recommendation rather than a defect.

## Severity rubric

Use the highest severity whose definition is supported by evidence. When evidence is incomplete, reduce confidence before inflating severity.

- `critical`: credible path to catastrophic data loss/corruption, broad auth bypass, secret/private-key compromise, arbitrary code execution, irreversible production damage, or equivalent system-wide impact requiring immediate blocking action.
- `high`: credible path to major security, financial, correctness, availability, or compatibility failure affecting important flows or many users, but below critical scope/impact.
- `medium`: real defect or reliability/security weakness with bounded impact, narrower preconditions, recoverability, or meaningful mitigation already present.
- `low`: limited-impact defect, maintainability issue with a concrete failure mode, or hardening gap unlikely to cause material harm by itself.
- `informational`: observation, trade-off, or improvement opportunity without a demonstrated defect.

Do not assign severity from code smell alone. Security scanners and external tools are evidence sources, not automatic severity authority; reconcile them with reachability, exploitability, compensating controls, and impact.

## Confidence rubric

- `high`: direct code/config/runtime evidence supports the finding and material assumptions are resolved.
- `medium`: evidence is strong but one meaningful assumption, environment detail, or runtime condition remains unresolved.
- `low`: finding is plausible but depends on missing code, configuration, environment, call paths, provider behavior, or reproduction.

A low-confidence `critical`/`high` item should normally be presented as a potential blocker pending verification, not as a confirmed vulnerability.

## Production/security verdict rules

Apply required gates from `34-production-readiness-checklist.md`.

- `approved`: every required gate is supported by `executed` or credible `supplied` evidence, no unresolved blocking finding exists, and residual risks are explicitly bounded.
- `approved with reservations`: required gates have sufficient evidence for deployment, but non-blocking `medium`/`low` risks or bounded operational follow-ups remain.
- `blocked`: any required gate has a blocking failure, a critical unresolved finding exists, a high-severity finding is reachable in the intended deployment without adequate mitigation, or evidence required to make the go/no-go decision is `blocked`.

Do not use `approved with reservations` to bypass missing evidence on a required gate.

## Decision tie-breakers

When multiple technically valid approaches satisfy the same requirement, apply these tie-breakers in order unless repository constraints override them:

1. preserve correctness, security, and compatibility;
2. preserve existing public contracts and deployment behavior;
3. choose the smallest complete change;
4. reuse existing repository/runtime capabilities before adding dependencies;
5. prefer explicit behavior over hidden control flow;
6. prefer the option with simpler validation and rollback;
7. prefer lower operational burden and fewer failure modes;
8. if still tied, preserve the existing architecture rather than introducing a new pattern.

## Validation ladder

Prefer the lowest reliable evidence layer available:

1. parse/compile/build;
2. focused unit/integration/functional/contract tests;
3. analyzers/security/dependency checks;
4. runtime smoke or provider-specific validation;
5. benchmark/load evidence for performance claims;
6. production telemetry for operational claims.

Passing an earlier layer does not imply later layers pass. Compilation does not prove semantics; unit tests do not prove provider behavior; a benchmark does not prove production capacity without comparable conditions.

## Performance claims

A performance recommendation may be reasoned from known complexity or allocation/I/O behavior, but label the claim `inferred` until measured. A quantified improvement claim requires an executed or supplied benchmark with scenario, environment, versions, sample size/repetitions, and measurement method.

## Security claims

Distinguish:

- confirmed vulnerability: evidence demonstrates a reachable weakness and meaningful impact;
- potential risk: suspicious pattern exists but reachability/preconditions are unresolved;
- evidence limitation: required context or runtime evidence is missing.

Do not report "secure" from static inspection alone.

## Regression discipline

For repeated reviews of the same target:

- preserve the same severity/evidence definitions;
- compare the same target revision or explicitly identify the new revision;
- do not change acceptance criteria because a candidate failed;
- convert confirmed recurring defects into tests, analyzers, architecture tests, CI gates, or explicit regression scenarios where practical;
- after a final validation pass, treat later edits as a new candidate requiring affected gates to rerun.

## Claim vocabulary

Allowed claims include:

- `observed in code`;
- `executed: dotnet test ... passed`;
- `supplied by CI`;
- `inferred from provider semantics`;
- `planned validation`;
- `blocked: repository/build environment unavailable`.

Avoid claims such as `production-ready`, `secure`, `faster`, `thread-safe`, or `backward-compatible` unless the evidence level and scope supporting that claim are explicit.
