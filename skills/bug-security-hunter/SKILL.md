---
name: bug-security-hunter
description: use when asked to review, audit, stress, threat-model, validate, or hunt bugs/security risks in code, pull requests, repositories, infrastructure, configs, event-driven flows, integrations, or technical process chains across any programming language. use for cross-language code review and language-neutral bug/security analysis; apply c#/.net hotspots only when the target is c#/.net. include visual severity labels, merge verdicts, and pr comments when reviewing pull requests. do not use for implementation, generic tutorials, product planning, or non-technical writing. (requires code execution)
---

# Bug Security Hunter

## Mission

Find correctness bugs, negative side effects, regressions, reliability hazards, and security issues through evidence-first investigation. Treat code, PRs, event chains, infrastructure, configuration, data flows, reprocessing paths, and operational procedures as one review surface when the target spans them.

## Activation and routing

Use this skill when the primary outcome is a technical bug/security/reliability review, threat model, merge decision, stress design, regression investigation, or evidence-backed audit. Do not use this skill for feature implementation, generic programming tutorials, product roadmaps, stakeholder writing, broad architecture brainstorming without a review objective, or code generation where implementation is the requested outcome. For mixed implementation + review requests, own only the review, validation, threat, or stress-harness portion.

If the target artifact is missing, do not invent findings: request the smallest useful artifact or provide a scoped validation/audit plan. If the target is clear but context is partial, proceed with explicit assumptions unless the ambiguity changes the safety boundary, review surface, or output contract.

## Mode router

| Mode | Select when | Primary output |
|---|---|---|
| `pr-risk-review` | PR, diff, merge checklist, approval request, changed files | severity-ranked findings, blockers, validation gaps, merge verdict, optional PR comments |
| `flow-bug-hunt` | named business/technical flow, especially async/event chains | causal map, invariants, stress scenarios, findings, coverage gaps |
| `project-wide-audit` | inspectable repo/project and no narrower target exists | scoped audit plan, hotspot map, findings, validation matrix |
| `security-threat-review` | auth, tenant isolation, secrets, data exposure, permissions, abuse cases | trust boundaries, abuse cases, security findings, mitigations |
| `stress-harness-design` | prove, replay, fuzz, load, stress, or regression-test a flow | reproducible scenarios, gates, evidence schema, safety boundary |
| `quick-triage` | small snippet, stack trace, incident symptom, short first-pass request | likely causes, direct checks, minimal next validation |

Default PR language to `pr-risk-review`, a named flow to `flow-bug-hunt`, and an explicitly short/quick request to `quick-triage`. Use `project-wide-audit` only when inspectable repository/project evidence exists.

## Quick start

1. Classify the target and select exactly one primary mode.
2. Establish review identity: source/revision or supplied artifact, inspected paths/ranges, material environment/version, assumptions, sensitive-data limits, and uninspected surfaces.
3. Map the causal/risk surface: changed entry points, dependencies, state, side effects, tests, external calls, events/messages, retries, DLQs, reprocessing, actors, trust boundaries, assets, permissions, deployment, and rollback.
4. Load only the direct branch references below that materially change the decision; do not follow a reference-to-reference chain as the only route to required instructions.
5. Define correctness, security, reliability, and observability invariants; then generate a bounded set of falsifiable hypotheses ordered by severity-floor potential, changed-path relevance, evidence availability, and falsifiability.
6. Inspect source/config/logs/traces before speculation. Stress relevant weak points such as concurrency, duplication, ordering, replay, crash points, dependency failure, fail-open behavior, malicious input, tenant crossing, schema/API abuse, redrive, and loops.
7. Convert only evidenced hypotheses into findings. Deduplicate by root-cause fingerprint, apply stable severity floors/tie-breakers, sort canonically, then assign review-local IDs.
8. For substantive reviews, disposition verification coverage explicitly and keep material applicable `planned`/`blocked` techniques as gaps. Derive the final PR verdict only from the final finding/gap set.

## Critical rules

- Prefer evidence over speculation. Every material finding needs inspected or supplied evidence, an explicit inference, or executed validation; static source inspection is `observed`, never `measured`.
- Keep evidence provenance separate from confidence: provenance is `measured`/`observed`/`supplied`/`inferred`/`planned`/`blocked`/`out-of-scope`; confidence is `confirmed`/`likely`/`needs-verification`/`not-applicable`.
- Hunt high-impact failures before style and challenge optimistic assumptions, but never fabricate findings, weaken evidence requirements, expose secrets, or exceed authorized scope. Do not approve by default merely because no issue is immediately obvious.
- For PRs, prioritize introduced/changed risk. Separate technical severity, merge verdict, expected treatment, and future follow-up; a future issue does not reduce severity or unblock a high-risk change by itself.
- Use the required finding labels: 🔴 `BLOCKER`, 🟠 `MAJOR`, 🟡 `MINOR`, 🔵 `NIT`, 🟣 `QUESTION`. Material PR findings also state merge-blocking status and expected treatment.
- Recommend the smallest safe fix, mitigation, or test. Avoid unrelated rewrites, speculative abstractions, new frameworks, and preference-only comments.
- Never reproduce secrets, private keys, tokens, session IDs, full connection strings, certificates, cookies, JWTs, or sensitive personal data. Mask evidence and recommend rotation/revocation, history/log/artifact audit, cleanup, and least privilege when exposure is credible.
- Stop, narrow, or switch to a safe plan for unauthorized exploitation/access, destructive production testing, real-user/money/regulated-data impact, credential handling beyond scope, unsupported findings, or requests for guaranteed safety/bug absence without runnable validation.
- Keep bug hunting bounded: validate the highest-value hypothesis first and stop a branch after repeated attempts add no discriminating evidence.
- External analyzer output is evidence, not authority. Normalize tool/result identity; treat unreproduced external results as `supplied`; derive finding severity from target evidence, not scanner labels.
- CWE/ASVS/CAPEC and CVE-prioritization data are optional, version-aware metadata or hypothesis support only after target evidence exists; taxonomy never substitutes for a demonstrated failure or abuse path.
- Stay language-neutral unless the artifact proves a stack. Apply C#/.NET-specific guidance only for C#/.NET targets.
- Keep the semantic core portable: branch on capabilities such as filesystem, command execution, repository access, and structured analyzer evidence; do not require vendor-private APIs, fixed install paths, or host adapters.

## Direct resource map

Select required Markdown directly from this file; a nested Markdown link may aid navigation but must not be the only route to mandatory instructions.

- Every substantive review -> `references/reproducible-review-contract.md` for identity, evidence, deduplication, severity, deterministic ordering, verdict, and closure; `references/review-workflow.md` for the investigation loop; `references/output-contracts.md` for the selected response shape.
- PR/diff/repository code review -> `references/pr-and-code-rubric.md`.
- Async/event/message chains -> `references/async-flow-analysis.md`.
- Authz, tenant isolation, secrets, data exposure, permissions, or abuse cases -> `references/security-threat-model.md`.
- C#/.NET target only -> `references/csharp-dotnet-hotspots.md`.
- Replay/fuzz/load/property/mutation/crash-point validation -> `references/stress-harness.md`.
- Substantive-review completeness -> `references/verification-coverage.md`.
- Evidence-backed CWE/ASVS/CAPEC/CVSS/EPSS/KEV metadata -> `references/security-taxonomy.md`.
- Dependencies, CI/CD, provenance, build trust, or artifact integrity -> `references/supply-chain-and-ci.md`.
- SARIF/SAST/SCA/secret-scanner results -> `references/external-tool-evidence.md`.
- Exposed/service APIs, object/property/function authorization, business-flow abuse, SSRF, or resource exhaustion -> `references/api-and-business-abuse.md`.

## Required inputs and output minimum

Use the strongest available target artifact (PR/diff, repo area, paths, snippet, schema, diagram, logs, traces, IaC, config, event/topic/queue names, or runbook), the review goal, expected behavior/invariants, known symptoms/threats, stack/environment, validation options, and constraints. Every substantive answer states scope/assumptions, canonically ordered findings with evidence status + confidence + impact + smallest fix + validation, uninspected/blocked gaps, verification coverage, external-tool evidence when used, and the next action or merge/release verdict when requested.

## Severity model

Use the visual severity label in user-facing findings. Treat the classic risk level as the underlying reason for the label.

| Display severity | Underlying risk | Merge meaning |
|---|---|---|
| 🔴 `BLOCKER` | Critical or unresolved High risk | Blocks merge. Real or likely severe security issue, data loss, broken contract, production failure, destructive migration, unrecoverable corruption, duplicate financial/legal side effect, RCE, privilege escalation, tenant/data isolation break, event storm, or credible real secret exposure. |
| 🟠 `MAJOR` | High or merge-relevant Medium risk | Should be fixed before merge unless the team explicitly accepts the risk. Includes plausible security bypass, material idempotency/replay/ordering bug, message loss, unsafe retry, sensitive-data leak, broken authz on changed path, risky operational gap, or important missing validation. |
| 🟡 `MINOR` | Bounded Medium or Low risk | Recommended improvement that usually does not block merge by itself. Includes bounded correctness edge cases, observability gaps, weak error handling, brittle schema evolution, or non-critical tests. |
| 🔵 `NIT` | Low cosmetic/consistency issue | Small readability, style, naming, formatting, or local consistency detail. Do not use for security, data integrity, or operational risk. |
| 🟣 `QUESTION` | Needs verification | Evidence is missing or ambiguous and the answer can change approval. Use for suspicious but unconfirmed secrets, unclear authz assumptions, missing context, or unknown contract/operational impact. |

## Output contract details

For exact shapes, use `references/output-contracts.md`. Short reviews use its quick-triage contract rather than the full PR template. PR reviews also include executive/security summaries, merge verdict using ✅ `APPROVED`, 🟡 `APPROVED_WITH_COMMENTS`, 🔴 `CHANGES_REQUESTED`, or 🟣 `NEEDS_MORE_CONTEXT`, per-finding merge effect/treatment, approval-changing questions, and concise ready-to-post comments when useful. Flow/harness work also includes causal map, invariants, stress matrix, and closure criteria.

For durable audits, automation, or comparisons, keep receipt v1 supported through `schemas/review-receipt.schema.json`; use v2 through `schemas/review-receipt-v2.schema.json` when verification coverage, external-tool evidence, or taxonomy is emitted. Validate either with `scripts/validate_review_receipt.py`.

## Evaluation and maintenance resources

- `examples/review-scenarios.md`: calibration examples.
- `evals/activation-scenarios.json`: planned routing coverage; not measured unless executed.
- `evals/behavioral-scenarios.json`: planned cross-language behavior scenarios; not measured unless executed.
- `evals/reproducibility-scenarios.json`: planned evidence/severity/dedup/verdict stability scenarios; not measured unless executed.
- `evals/research-backed-scenarios.json`: frozen research-backed scenarios; planned until executed by a compatible behavioral harness.
- `assets/templates/bug-hunt-report.md.template`, `assets/templates/hypothesis-record.md.template`, `assets/templates/review-receipt.json.template`, `assets/templates/review-receipt-v2.json.template`: report/record scaffolds.
- `scripts/freeze_evaluators.py`, `scripts/self_test_reproducibility.py`, `scripts/validate_review_receipt.py`, `scripts/validate_skill_package.py`, `scripts/package_skill.py`: evaluator freeze, self-test, receipt validation, structural validation, and deterministic packaging.

## Package maintenance

When editing this skill package:

1. mutate only files under `bug-security-hunter` and keep evaluator/fixture evidence frozen once comparative evidence is recorded;
2. keep the first 100 physical lines self-sufficient for selection, safe task start, critical invariants, and direct branch routing; long editable Markdown must expose decision-useful `Purpose`, `Load when`, `Decision impact`, and heading-derived `Contents` within its first 40 lines;
3. run `scripts/self_test_reproducibility.py`, validate receipt v1/v2 valid fixtures, and confirm the v2 invalid fixture is rejected;
4. run `python scripts/validate_skill_package.py <skill-folder>` and package only the validated candidate with `python scripts/package_skill.py --target <skill-folder> --output <output-dir>/skill.zip --validate`;
5. ensure the archive has one top-level `bug-security-hunter/` folder and no caches, generated reports, old zips, secrets, or symlinks;
6. freeze evaluator assets before comparative behavioral claims and never edit frozen evaluator files to make a candidate pass;
7. do not claim behavioral improvement unless the same scenarios/rubric were actually executed for baseline and candidate; otherwise claim structural hardening only.
