---
name: security-and-governance-review
description: 'use when asked to audit a skill package, agent package, validator, script, or auxiliary technical project for security and governance risks: hardcoded secrets, sensitive logging, dangerous shell commands, unsafe file handling, dependency and supply-chain risk, permissions, tool authority boundaries, llm/agent governance controls, policy enforcement, responsible ai, compliance risk, threat modeling, or remediation planning. do not use for general skill hardening, ordinary code style review, or implementing risky fixes without a plan, evidence, validation, and explicit authorization.'
---

# Security and Governance Review

## Purpose

Review reusable skill packages, agents, scripts, validators, templates, and nearby technical helper projects for security, supply-chain, governance, llm/agent authority, responsible-ai, and compliance risks. Treat the review as evidence-based assurance work, not as general hardening or style cleanup.

## Scope boundary

Use this skill only for security and governance review. It may inspect `SKILL.md`, `agents/`, `references/`, `scripts/`, `assets/templates/`, dependency manifests, validators, packaging scripts, examples, and small auxiliary project files.

Do not use this skill to replace broad skill hardening, ordinary code review, vulnerability exploitation, dependency installation, destructive command execution, or risky remediation. If a finding needs code changes, first produce a remediation plan with validation gates; apply changes only when the user explicitly asks for implementation.

## Required inputs

Resolve or conservatively infer:

1. `TARGET_PATH`: skill folder, extracted package, repository subfolder, uploaded files, pasted code, or named installed skill.
2. Review mode: one of the modes below, or `security-report` when unspecified.
3. Evidence policy: target files, user-supplied context, local static scan output, package manifests, and approved primary sources if current facts are required.
4. Allowed actions: read-only by default. No dependency downloads, no package installs, no network calls, no destructive shell commands, and no mutation unless separately authorized.
5. Blocked paths: `.git`, credentials, local env files, private keys, real secrets, fixtures containing expected secret values, expected outputs, generated evidence, old zips, and user-declared read-only paths.
6. Output expectation: inline findings, filled report template, threat model, or remediation plan.

## Modes

- `secret-handling-review`: inspect hardcoded secrets, tokens, credentials, connection strings, private keys, `.env` leakage, and sensitive logging. Never print the full secret value.
- `script-security-review`: inspect Python, JavaScript, TypeScript, shell, PowerShell, packaging, archive, and validator scripts for unsafe subprocess, shell injection, path traversal, symlink handling, archive extraction, untrusted deserialization, broad deletes, and unsafe file writes.
- `dependency-risk-review`: inspect manifests and lockfiles for supply-chain signals, unpinned or floating versions, direct install-from-url patterns, lifecycle scripts, unknown registries, license/compliance flags, and missing vulnerability evidence. Do not claim a CVE without a source or scanner result.
- `llm-agent-governance-review`: inspect agent authority boundaries, tools, permissions, policy enforcement, audit trails, rate limits, handoffs, stop conditions, human approval, fail-closed behavior, and cross-agent trust boundaries.
- `responsible-ai-review`: inspect domain-specific risks around bias, fairness, accessibility, privacy, explainability, consent, automation impact, human override, and exclusion. Avoid generic checklist-only comments.
- `threat-model`: create a lightweight threat model with assets, trust boundaries, actors, abuse cases, controls, residual risks, and validation probes.
- `remediation-plan`: prioritize fixes with severity, evidence, scope, risk, owner assumption, validation gate, rollback, and safe implementation order.
- `security-report`: produce the complete structured report using `assets/templates/security-report.md.template`.

## Resource loading

Load only what the selected mode needs:

- `references/security-review-rubric.md` for severity, evidence classes, confidence, gates, and report judgment.
- `references/secret-handling-checklist.md` for secret detection, masking, logging, rotation, and false-positive rules.
- `references/script-security-checklist.md` for scripts, file handling, subprocess, archive extraction, path traversal, and packaging safety.
- `references/agent-governance-checklist.md` for authority boundaries, tool permissions, policy controls, audit trails, handoffs, fallback, and stop conditions.
- `references/responsible-ai-checklist.md` for contextual responsible-ai review, fairness, accessibility, privacy, explainability, and escalation.
- `assets/templates/security-report.md.template` when the user asks for a durable report or mode `security-report`.
- `examples/security-review-prompts.md` for concrete activation, non-activation, and mode-selection prompt examples.
- `scripts/security_static_review.py` when files are available and a safe, local, read-only static scan will improve coverage.

## Review workflow

1. **Identify the target and mode.** Read the target `SKILL.md` first when present, then inventory relevant files. If the mode is not specified, run `security-report` with all applicable subreviews.
2. **Protect sensitive material.** Do not open or print full secret values unnecessarily. Mask secrets in notes and outputs. Do not inspect `.git` history unless the user explicitly asks and the environment supports safe redaction.
3. **Run optional static scan.** When a filesystem target exists, run:

   ```bash
   python scripts/security_static_review.py --target <TARGET_PATH> --format markdown --output <REPORT_PATH>
   ```

   Treat script output as triage evidence. Manually review likely false positives before finalizing.
4. **Perform human security review.** Apply the relevant checklist files. Select the highest-risk categories first based on target context: secrets, scripts, dependencies, agent authority, responsible ai, then compliance.
5. **Classify evidence.** Label each issue as `confirmed risk`, `potential risk`, or `evidence limitation`. Do not invent vulnerabilities from naming alone.
6. **Assign severity and confidence.** Use the rubric. Severity reflects impact and exploitability; confidence reflects evidence strength.
7. **Recommend safely.** Prefer minimal, auditable controls: least privilege, explicit allowlists, fail-closed policy, managed secret stores, no sensitive logging, safe archive extraction, pinned dependencies, human approval for high-impact actions, and append-only audit trails.
8. **Validate.** State commands executed, scripts checked, files inspected, and gates that passed or failed. If no dynamic validation was performed, say so.
9. **Finalize.** Produce the requested output. For `security-report`, use the template structure and include findings, evidence, recommendations, validation, limitations, and residual risk.

## Evidence and reporting rules

- Never expose secrets. Mask values as `prefix...suffix` or `[masked secret]`.
- Quote only the minimum necessary evidence and never quote full credentials, private keys, tokens, cookies, session ids, or connection strings.
- Distinguish `confirmed risk`, `potential risk`, and `evidence limitation` in every finding.
- Use `critical`, `high`, `medium`, `low`, or `informational` severity. Use `high`, `medium`, or `low` confidence.
- Do not claim dependency vulnerability, license violation, or compliance failure without manifest evidence, scanner output, authoritative source, or user-provided policy.
- Do not mark placeholders such as `example-token`, `your_api_key_here`, or `changeme` as confirmed leaks; classify them as sample-hygiene risks only if they encourage unsafe practice.
- Do not recommend removing existing security controls. Improve or tighten them.
- Prefer fail-closed behavior for ambiguous tool authorization and high-impact agent actions.
- For responsible-ai review, map risks to the actual product domain, users, decisions, and harms.

## Output contract

A complete response should include:

1. Mode and target.
2. Files or snippets inspected.
3. Executive security posture.
4. Findings ordered by severity, each with: id, mode, classification, severity, confidence, location, masked evidence, risk, recommendation, validation gate, and residual risk.
5. Threat model when requested or useful.
6. Dependency and supply-chain observations when manifests exist.
7. Governance and responsible-ai observations when agents or ai behavior are present.
8. Remediation plan with priority order and safe validation.
9. Commands executed and pass/fail/not-run status.
10. Limitations and evidence gaps.

## Stop conditions

Stop before mutation or risky analysis when:

- the requested action would expose or print full secrets;
- the user asks to execute destructive commands, untrusted scripts, malware, exploit code, or package install hooks without an explicit safe sandbox and clear authorization;
- the target has no inspectable files and the user requests concrete findings;
- the review requires current vulnerability or license data and browsing or scanner evidence is unavailable;
- the requested remediation would change `.git`, credentials, fixtures, expected outputs, or unrelated project files;
- evidence is insufficient to support a confirmed vulnerability claim.

## Relationship to neighboring skills

- Use broad hardening skills for package maturity, activation, scenario coverage, template integration, consistency, and packaging hygiene.
- Use secure-code-review for focused secret and credential handling in ordinary code artifacts.
- Use this skill when the review spans security plus governance of skills, agents, scripts, validators, authority boundaries, llm safety, responsible ai, and compliance evidence.
