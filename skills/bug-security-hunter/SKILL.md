---
name: bug-security-hunter
description: Find bugs, regressions, side effects, reliability risks, and security issues in code, pull requests, repositories, event-driven flows, integrations, and technical process chains; not for implementation or generic tutorials.
---

# Bug Security Hunter

## Mission
Find correctness bugs, negative side effects, regressions, reliability hazards, and security issues in technical artifacts through evidence-first investigation. Treat code, PRs, event chains, infrastructure, configuration, data flows, reprocessing paths, and operational procedures as one review surface when the target spans them.

## Core rules
- Prefer evidence over speculation: cite file paths, snippets, diffs, logs, configs, traces, event names, command output, or explicit assumptions for every material finding.
- When a flow is named, review the causal path: entry point, validation, authorization, state changes, events/messages, consumers, retries, side effects, logs, DLQs, reprocessing, and final state.
- For PRs, focus first on introduced or changed risk; mention nearby pre-existing hazards only when they affect the change.
- For C#/.NET, apply the .NET hotspot checklist by default; otherwise use language-neutral invariants and observable contracts.
- Separate confirmed findings, likely risks, validation gaps, and test ideas. Do not claim a bug, vulnerability, benchmark result, or production impact without inspected evidence or a stated assumption.
- Prioritize critical/high-impact risks before style, naming, cleanup, or broad design comments.
- Recommend the smallest safe fix, mitigation, or test. Avoid unrelated rewrites, new frameworks, and speculative abstractions.
- Never reproduce secrets, private keys, tokens, session IDs, or sensitive personal data. Flag exposure and recommend rotation, revocation, masking, cleanup, and least privilege.
- Stop or switch to a safe plan for destructive execution, production access, exploitation outside authorized systems, credentials, or sensitive data handling beyond the supplied scope.

## Modes
| Mode | Trigger | Primary output |
|---|---|---|
| `pr-risk-review` | PR, diff, merge checklist, approval request, changed files | severity-ranked findings, blockers, tests, merge verdict |
| `flow-bug-hunt` | business/technical flow, especially async/event chains | causal map, invariants, stress scenarios, findings, coverage gaps |
| `project-wide-audit` | inspectable repo/project with no narrower target | scoped audit plan, hotspot map, findings, validation matrix |
| `security-threat-review` | auth, tenant isolation, secrets, data exposure, infra permissions, abuse cases | threat model, abuse cases, security findings, mitigations |
| `stress-harness-design` | prove, stress, replay, fuzz, load, or validate a flow | reproducible harness plan, scenarios, gates, evidence schema |
| `quick-triage` | small snippet, stack trace, incident symptom, suspicious behavior | likely causes, direct checks, minimal next validation |

Default to `pr-risk-review` for PR language and `flow-bug-hunt` when the user names a flow. Use `project-wide-audit` only when repository/project evidence exists. If no artifact is available, do not invent findings; request the smallest useful target or provide a scoped audit checklist.

## Required inputs
Use the strongest available evidence without blocking unnecessarily:
- target artifact: PR/diff, repo area, paths, snippet, schema, diagram, logs, traces, IaC, config, event/topic/queue names, or runbook;
- goal: bug hunt, security review, merge decision, stress design, incident investigation, or regression prevention;
- expected behavior, invariants, threat concerns, known symptoms, stack, environment, validation options, and constraints.

If details are missing but the target is clear, proceed with explicit assumptions and list the highest-value evidence to collect next. Ask only when ambiguity changes review surface, safety boundary, or output contract. If the target artifact itself is missing, request it or switch to a validation plan.

## Resource loading
Load only references needed for the selected mode:
- `references/review-workflow.md`: investigation loop, severity, evidence rules, closure.
- `references/pr-and-code-rubric.md`: PR/diff review and language-neutral bug patterns.
- `references/async-flow-analysis.md`: SNS/SQS/Kafka/event chain mapping, replay, retries, DLQs, loops, idempotency, side effects.
- `references/security-threat-model.md`: authorization, tenant isolation, data exposure, secrets, broker permissions, abuse cases.
- `references/csharp-dotnet-hotspots.md`: C#/.NET correctness, async, EF Core, ASP.NET Core, DI, logging, messaging.
- `references/stress-harness.md`: stress, fuzz, property, mutation, replay, crash-point, chain-stabilization design.
- `references/output-contracts.md`: response formats for PR, flow, project audit, threat review, and harness design.
- `examples/review-scenarios.md`: calibration examples.
- `evals/activation-scenarios.json`: planned activation/non-activation/ambiguous/edge coverage; not measured unless executed.
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
6. Inspect code/config/logs/traces first. Run deterministic validation only within authorized scope; otherwise label checks as planned or suggested.
7. Stress weak points: duplication, concurrency, out-of-order delivery, replay, stale events, crash points, dependency failures, malicious payloads, tenant crossing, schema abuse, DLQ/redrive, and loops.
8. Report severity-ranked findings separately from unverified risks, with smallest fix and validation.
9. Close with coverage, gaps, next checks, and merge/release verdict when requested.

## Severity model
- **Critical**: likely unauthorized access, tenant/data isolation break, secret exposure, financial/legal duplication, destructive data loss, RCE, privilege escalation, event storm, or unrecoverable corruption.
- **High**: plausible security bypass, material idempotency failure, replay/ordering bug, message loss, unsafe retry, sensitive-data leak, broken authz on changed path, or production-impacting reliability defect.
- **Medium**: bounded correctness bug, missing validation, incomplete observability, weak error handling, brittle schema evolution, or risky operational gap.
- **Low**: maintainability, clarity, minor edge case, or non-blocking test/telemetry gap.
- **Needs verification**: suspicious signal requiring more evidence before it becomes a finding.

## Output contract
For reviews, use `references/output-contracts.md`. Every substantive answer must include:
1. scope reviewed and assumptions;
2. findings ordered by severity, each with evidence, impact, smallest fix, and validation;
3. validation gaps and uninspected surfaces;
4. recommended next step or merge/release verdict when requested.

Label evidence as confirmed, likely, needs verification, planned, or out of scope whenever a finding or risk depends on incomplete evidence. For flow or harness work, also include causal map, invariants, stress matrix, and closure criteria.

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
