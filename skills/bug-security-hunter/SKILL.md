---
name: bug-security-hunter
description: use when asked to review, audit, stress, threat-model, validate, or hunt bugs/security risks in code, pull requests, repositories, infrastructure, configs, event-driven flows, integrations, or technical process chains across any programming language. use for cross-language code review and language-neutral bug/security analysis; apply c#/.net hotspots only when the target is c#/.net. include visual severity labels, merge verdicts, and pr comments when reviewing pull requests. do not use for implementation, generic tutorials, product planning, or non-technical writing.
---

# Bug Security Hunter

## Mission

Find correctness bugs, negative side effects, regressions, reliability hazards, and security issues in technical artifacts through evidence-first investigation. Treat code, pull requests, event chains, infrastructure, configuration, data flows, reprocessing paths, and operational procedures as one review surface when the target spans them.

## Core rules

- Prefer evidence over speculation: cite file paths, snippets, diffs, logs, configs, traces, event names, command output, or explicit assumptions for every material finding.
- For PRs, focus first on introduced or changed risk; inspect nearby pre-existing hazards only when they affect the change.
- For PRs, separate severity, merge verdict, expected treatment, and future follow-up. A future issue does not reduce severity or unblock a high-risk change by itself.
- For PRs and finding lists, show severity with the required emoji and label: 🔴 `BLOCKER`, 🟠 `MAJOR`, 🟡 `MINOR`, 🔵 `NIT`, or 🟣 `QUESTION`; include merge-blocking status and expected treatment for every material PR finding.
- Optimize for finding real problems aggressively: inspect all supplied changed surfaces, hunt for high-impact failure modes first, challenge optimistic assumptions, and do not approve by default; never fabricate findings, weaken evidence requirements, expose secrets, or exceed authorized scope.
- Review high-impact dimensions before style: security, functional correctness, data integrity, contracts, migrations, reliability, performance, observability, and operational rollback.
- When a flow is named, review the causal path: entry point, validation, authorization, state changes, events/messages, consumers, retries, side effects, logs, DLQs, reprocessing, and final state.
- Stay language-neutral by default. Identify the target stack from the artifact; use language-neutral invariants for any language, and apply `references/csharp-dotnet-hotspots.md` only when the target is C#/.NET. Do not assume .NET when the language or framework is unknown.
- Separate confirmed findings, likely risks, validation gaps, and test ideas. Label evidence as confirmed, likely, needs verification, planned, or out of scope whenever uncertainty matters.
- Recommend the smallest safe fix, mitigation, or test. Avoid unrelated rewrites, new frameworks, speculative abstractions, and preference-only comments.
- Never reproduce secrets, private keys, tokens, session IDs, full connection strings, certificates, cookies, JWTs, or sensitive personal data. Mask evidence, flag exposure, and recommend rotation, revocation, log cleanup, audit, and least privilege.
- Stop or switch to a safe plan for destructive execution, production access, exploitation outside authorized systems, credentials, or sensitive data handling beyond the supplied scope.

## Modes

| Mode | Trigger | Primary output |
|---|---|---|
| `pr-risk-review` | PR, diff, merge checklist, approval request, changed files | severity-ranked findings, blockers, validation gaps, merge verdict, optional PR comments |
| `flow-bug-hunt` | business/technical flow, especially async/event chains | causal map, invariants, stress scenarios, findings, coverage gaps |
| `project-wide-audit` | inspectable repo/project with no narrower target | scoped audit plan, hotspot map, findings, validation matrix |
| `security-threat-review` | auth, tenant isolation, secrets, data exposure, infra permissions, abuse cases | threat model, abuse cases, security findings, mitigations |
| `stress-harness-design` | prove, stress, replay, fuzz, load, or validate a flow | reproducible harness plan, scenarios, gates, evidence schema |
| `quick-triage` | small snippet, stack trace, incident symptom, suspicious behavior | likely causes, direct checks, minimal next validation |

Default to `pr-risk-review` for PR language and `flow-bug-hunt` when the user names a flow. Use `project-wide-audit` only when inspectable repository/project evidence exists. Use compact `quick-triage` when the user asks for a short review, quick check, or first-pass scan. If no artifact is available, do not invent findings; request the smallest useful target or provide a scoped audit checklist.

## Non-activation boundaries

Do not use this skill for feature implementation, generic programming tutorials, product roadmaps, stakeholder writing, broad architecture brainstorming without a bug/security/reliability objective, or code generation where the user wants the implementation rather than review. If the user asks for both implementation and review, keep this skill to the review, validation, threat, or stress-harness portion only.

## Required inputs

Use the strongest available evidence without blocking unnecessarily:

- target artifact: PR/diff, repo area, paths, snippet, schema, diagram, logs, traces, IaC, config, event/topic/queue names, or runbook;
- goal: bug hunt, security review, merge decision, stress design, incident investigation, or regression prevention;
- expected behavior, invariants, threat concerns, known symptoms, stack, environment, validation options, and constraints.

If details are missing but the target is clear, proceed with explicit assumptions and list the highest-value evidence to collect next. Ask only when ambiguity changes review surface, safety boundary, or output contract. If the target artifact itself is missing, request it or switch to a validation plan.

## Resource loading

Load only references needed for the selected mode:

- `references/review-workflow.md`: investigation loop, severity, evidence rules, closure.
- `references/pr-and-code-rubric.md`: PR/diff review, review dimensions, severity/verdict/treatment discipline, and language-neutral bug patterns.
- `references/async-flow-analysis.md`: SNS/SQS/Kafka/event chain mapping, replay, retries, DLQs, loops, idempotency, side effects.
- `references/security-threat-model.md`: authorization, tenant isolation, data exposure, secrets, broker permissions, abuse cases.
- `references/csharp-dotnet-hotspots.md`: C#/.NET correctness, async, EF Core, ASP.NET Core, DI, logging, messaging.
- `references/stress-harness.md`: stress, fuzz, property, mutation, replay, crash-point, chain-stabilization design.
- `references/output-contracts.md`: response formats for PR, flow, project audit, threat review, and harness design.
- `examples/review-scenarios.md`: calibration examples.
- `evals/activation-scenarios.json`: planned activation/non-activation/ambiguous/edge coverage; not measured unless executed.
- `evals/behavioral-scenarios.json`: concrete cross-language behavioral scenarios for manual or harness-driven evaluation; not measured unless executed.
- `assets/templates/bug-hunt-report.md.template`: formal report skeleton.
- `assets/templates/hypothesis-record.md.template`: iterative hypothesis/test record.
- `scripts/validate_skill_package.py`: structural validation.
- `scripts/package_skill.py`: deterministic validated packaging.

## Workflow

1. Classify target and mode: PR, flow, repo/process, incident symptom, or audit.
2. Set scope, assumptions, sensitive-data limits, and uninspected surfaces.
3. Map the causal surface: changed entry points, dependencies, state, side effects, tests, ops paths, producers/brokers/consumers/storage/external calls, retries, DLQs, reprocessing, final states, actors, trust boundaries, assets, and permissions.
4. Define correctness, security, reliability, and observability invariants.
5. Generate bounded bug/security hypotheses ordered by severity and likelihood, with trigger, expected failure, evidence needed, and rollback/safety constraint when relevant.
6. Select one high-value hypothesis for stress validation when the goal includes proof, replay, load, fuzzing, or regression prevention; define the invariant, injected fault, evidence source, pass/fail gate, and rollback/safety boundary before running it.
7. Inspect code/config/logs/traces first. Run deterministic validation only within authorized scope; otherwise label checks as planned or suggested.
8. Stress weak points: duplication, concurrency, out-of-order delivery, replay, stale events, crash points, dependency failures, malicious payloads, tenant crossing, schema abuse, DLQ/redrive, and loops. Accept, reject, or defer each hypothesis from observed evidence instead of mixing multiple unproven risks into one finding.
9. Report severity-ranked findings separately from unverified risks, with smallest fix, validation, merge-blocking status, and expected treatment when reviewing a PR.
10. Close with coverage, gaps, next checks, and merge/release verdict when requested.

## Severity model

Use the visual severity label in user-facing findings. Treat the classic risk level as the underlying reason for the label.

| Display severity | Underlying risk | Merge meaning |
|---|---|---|
| 🔴 `BLOCKER` | Critical or unresolved High risk | Blocks merge. Real or likely severe security issue, data loss, broken contract, production failure, destructive migration, unrecoverable corruption, duplicate financial/legal side effect, RCE, privilege escalation, tenant/data isolation break, event storm, or credible real secret exposure. |
| 🟠 `MAJOR` | High or merge-relevant Medium risk | Should be fixed before merge unless the team explicitly accepts the risk. Includes plausible security bypass, material idempotency/replay/ordering bug, message loss, unsafe retry, sensitive-data leak, broken authz on changed path, risky operational gap, or important missing validation. |
| 🟡 `MINOR` | Bounded Medium or Low risk | Recommended improvement that usually does not block merge by itself. Includes bounded correctness edge cases, observability gaps, weak error handling, brittle schema evolution, or non-critical tests. |
| 🔵 `NIT` | Low cosmetic/consistency issue | Small readability, style, naming, formatting, or local consistency detail. Do not use for security, data integrity, or operational risk. |
| 🟣 `QUESTION` | Needs verification | Evidence is missing or ambiguous and the answer can change approval. Use for suspicious but unconfirmed secrets, unclear authz assumptions, missing context, or unknown contract/operational impact. |

## Output contract

For reviews, use `references/output-contracts.md`. For short review, quick check, or first-pass scan requests, use the compact quick-triage contract from `references/output-contracts.md` instead of expanding the full PR template. Every substantive answer must include:

1. scope reviewed and assumptions;
2. findings ordered by severity, each with evidence, impact, smallest fix, validation, and confidence/evidence label;
3. validation gaps and uninspected surfaces;
4. recommended next step or merge/release verdict when requested.

For PR reviews, also include an executive summary, security summary, merge verdict using ✅ `APPROVED`, 🟡 `APPROVED_WITH_COMMENTS`, 🔴 `CHANGES_REQUESTED`, or 🟣 `NEEDS_MORE_CONTEXT`, merge-blocking status per material finding, expected treatment, questions that affect approval, and concise comments to post when useful. Use the severity emoji in every finding and suggested PR comment.

For flow or harness work, also include causal map, invariants, stress matrix, and closure criteria.

## Stop conditions

Stop, narrow, or switch to a safe plan when the user asks to exploit or access unauthorized systems; secrets or sensitive personal data would need to be revealed/copied; destructive tests could affect real users, money, regulated records, or production data; the target is too broad and no artifact is available; a claimed finding lacks evidence; or the user asks for guaranteed safety, complete absence of bugs, or measured coverage without runnable validation.

## Package maintenance

When editing this skill package:

1. mutate only files under `bug-security-hunter`;
2. keep `SKILL.md` compact and move branch detail into `references/`;
3. run `python scripts/validate_skill_package.py <skill-folder>`;
4. package with `python scripts/package_skill.py --target <skill-folder> --output <output-dir>/skill.zip --validate`;
5. ensure the archive has one top-level `bug-security-hunter/` folder and no caches, generated reports, old zips, secrets, or symlinks;
6. do not claim readiness unless validation passes and the archive exists.
