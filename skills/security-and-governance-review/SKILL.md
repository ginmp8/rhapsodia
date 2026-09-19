---
name: security-and-governance-review
description: 'use when asked to audit a skill package, agent package, validator, script, or auxiliary technical project for security and governance risks: hardcoded secrets, sensitive logging, dangerous shell commands, unsafe file handling, dependency and supply-chain risk, permissions, tool authority boundaries, llm/agent governance controls, policy enforcement, responsible ai, compliance risk, threat modeling, or remediation planning. do not use for general skill hardening, ordinary code style review, or implementing risky fixes without a plan, evidence, validation, and explicit authorization.'
---

# Security and Governance Review

## Purpose

Review reusable skill packages, agents, scripts, validators, templates, and nearby technical helper projects for security, supply-chain, governance, llm/agent authority, responsible-ai, and compliance risks. This is evidence-based assurance work, not general hardening or style cleanup.

Default to **read-only** review. Mutation requires explicit user authorization and must not change protected evidence merely to make a finding disappear.

## Reproducibility contract

This is a `research-analytic` skill. Reproducibility means equivalent inputs/evidence should produce materially comparable classifications, severity reasoning, evidence mappings, gates, and report structure. It does **not** require byte-identical threat-model prose or eliminate analyst judgment.

Use:

- rubric `SGR-2.0` from `references/security-review-rubric.md`;
- deterministic local helpers for static triage, evidence identity, redaction, and report validation;
- explicit source/evidence identity;
- frozen scenario/evaluator inputs when comparing versions;
- separate structural, behavioral, runtime, and external-current evidence.

Do not convert threat modeling, responsible-ai analysis, or governance judgment into mechanical scoring merely to increase determinism.

## Scope boundary

Use this skill only for security/governance review. It may inspect `SKILL.md`, agents, references, scripts, templates, dependency manifests/lockfiles, validators, packaging scripts, examples, small auxiliary project files, and policy evidence relevant to the review.

Do not use it to replace broad skill hardening, ordinary code review, vulnerability exploitation, dependency installation, destructive execution, or risky remediation. If code changes are needed, first produce a remediation plan with validation gates; implement only when explicitly authorized.

## Required inputs

Resolve or conservatively infer:

1. `TARGET_PATH`: exact skill/project/files/snippets being reviewed.
2. Review mode: one mode below, or `security-report` when unspecified.
3. Evidence policy: target files, user context, local read-only scan output, manifests/lockfiles, runtime evidence supplied by the user, and approved current primary/scanner sources when freshness matters.
4. Allowed actions: read-only by default; no installs, dependency hooks, destructive commands, network mutation, or target mutation unless separately authorized.
5. Protected paths/evidence: `.git`, credentials, `.env`, private keys, real secrets, fixtures/golden inputs, expected outputs, frozen evaluator evidence, generated baseline evidence, and user-declared protected paths.
6. Output expectation: inline findings, Markdown report, machine-readable JSON report, threat model, or remediation plan.

If target identity is ambiguous and a concrete finding depends on it, do not guess.

## Modes

- `secret-handling-review`: hardcoded secrets, tokens, credentials, connection strings, private keys, `.env` leakage, and sensitive logging. Never emit a complete secret value.
- `script-security-review`: unsafe subprocess/shell use, injection, traversal, symlinks, archive extraction, deserialization, broad deletes, and unsafe writes.
- `dependency-risk-review`: manifests/lockfiles, floating versions, install-from-url, lifecycle hooks, registries, licenses/policy, and current vulnerability evidence. Never claim a CVE/applicability without evidence bound to dependency/source identity.
- `llm-agent-governance-review`: authority boundaries, permissions, approval, policy enforcement, audit, rate/budget limits, handoffs, fail-closed behavior, and cross-agent trust.
- `responsible-ai-review`: contextual risks around privacy, fairness, accessibility, explainability, consent, automation impact, human override, and exclusion.
- `threat-model`: evidence-linked assets, trust boundaries, actors, abuse cases, controls, assumptions, residual risks, and validation probes using `schemas/threat-model.schema.json` as the machine-readable shape.
- `remediation-plan`: prioritized fixes with evidence, risk, owner assumption, safe order, validation gate, and rollback/containment.
- `security-report`: complete report using the Markdown template and, when machine-readable output is useful/requested, `schemas/security-review-report.schema.json`.

## Progressive resource loading

Load only what the active mode needs:

- `references/security-review-rubric.md`: SGR-2.0 classifications, stable severity criteria, confidence, tie-breakers, and critical gates.
- `references/evidence-and-source-integrity.md`: deterministic source/evidence snapshot, protected evidence, dependency/source identity, and evidence-layer separation.
- `references/secret-handling-checklist.md`: secret detection, absolute no-full-secret rule, protected secret sources, and safe remediation.
- `references/script-security-checklist.md`: scripts, subprocess, file handling, traversal, archives, deserialization, and packaging.
- `references/agent-governance-checklist.md`: authority matrix, approvals, audit, fail-closed rules, handoffs, and trust boundaries.
- `references/responsible-ai-checklist.md`: contextual responsible-ai review.
- `assets/templates/security-report.md.template`: durable Markdown report.
- `schemas/security-review-report.schema.json`: machine-readable report contract.
- `schemas/threat-model.schema.json`: threat-model contract.
- `evals/activation-scenarios.json`: frozen/planned regression scenarios; scenario files are not behavioral evidence until executed.
- `scripts/security_static_review.py`: deterministic read-only static triage.
- `scripts/evidence_snapshot.py`: deterministic evidence/source identity receipt.
- `scripts/validate_security_report.py`: standard-library machine-readable report gate.

## Review workflow

### 1. Resolve target, mode, authority, and protected scope

Read target `SKILL.md` first when present, then inventory relevant files. Record what may be read and what is protected from mutation or content exposure. Do not follow symlinks into blocked/out-of-scope paths.

### 2. Snapshot evidence identity before analysis

When a filesystem target exists and the runtime permits it, create a receipt before substantive conclusions:

```text
<PYTHON> scripts/evidence_snapshot.py --target <TARGET_PATH> --output <WORK>/evidence-receipt.json
```

Use relative paths and hashes for safe files. Credentials/`.env`/private-key sources should be `protected-unread`; fixtures/expected outputs should be protected from mutation and may be `protected-hash-only`. A hash proves identity, not safety.

If material source identity cannot be established, say so. For high-impact conclusions that depend on missing evidence, fail closed.

### 3. Run deterministic static triage when useful

```text
<PYTHON> scripts/security_static_review.py --target <TARGET_PATH> --format json --output <WORK>/static-triage.json
```

Treat results as triage evidence only. The scanner uses stable ordering/ids and deterministic redaction. Pattern matches do not prove exploitability, a live credential, a CVE, or concrete exposure.

### 4. Perform mode-specific review

Apply the relevant checklists. For agent/governance work, build an authority matrix for meaningful read/write/execute/delete/send/publish/schedule/deploy/approve/delegate actions. Capability never implies authorization.

For threat modeling, use the schema as structure while preserving evidence-based analyst judgment. State assumptions and evidence refs; do not generate arbitrary scores.

### 5. Classify with SGR-2.0

Every material finding uses exactly one classification:

- `confirmed`
- `suspicious-pattern`
- `governance-risk`
- `needs-verification`
- `not-applicable`

Then assign severity/confidence using the versioned rubric and tie-breakers. Do not upgrade based on naming, intuition, or model consensus.

### 6. Enforce evidence mapping

Every material finding must map:

`finding -> evidence -> risk -> recommendation -> validation`

Evidence should include source identity when available. For secrets, report only masked/omitted evidence. For current dependency/CVE claims, bind the claim to resolved dependency identity plus scanner/authoritative source identity; otherwise use `needs-verification`.

### 7. Fail closed on critical evidence gaps

Do not silently produce a positive assurance conclusion when critical evidence is missing. Examples:

- high-impact agent mutation authority exists but authorization policy cannot be verified;
- user asks whether a dependency is affected by a current CVE but resolved version/current advisory evidence is unavailable;
- target integrity changed after the evidence snapshot;
- a secret-like value appears but authenticity/exposure cannot be safely established.

For machine-readable reports, non-empty `critical_evidence_gaps` requires `review_status=blocked-critical-evidence`.

### 8. Validate output

For JSON reports:

```text
<PYTHON> scripts/validate_security_report.py <REPORT.json>
```

The validator checks report/rubric versions, classifications, severities, evidence mapping, evidence layers, fail-closed status, duplicate finding ids, and recognized unredacted secret-like values.

State commands executed and exact pass/fail/not-run status. If dynamic/runtime checks were not run, do not imply they passed.

### 9. Finalize without post-pass mutation

Once the final evidence/report gates pass, treat that result as frozen. Any later edit that affects findings, evidence, redaction, classification, or validation requires rerunning the affected gates.

## Absolute secret rule

Never print a complete credential, token, private key, cookie, session id, password, connection-string password, or equivalent secret. This is absolute for this skill's outputs and helper scripts.

Use `[masked secret]`, `[masked private key block]`, or an evidence fingerprint that omits content. Do not use prefix/suffix fragments as the default redaction mechanism.

## Claims and evidence limits

- Do not allege a vulnerability, CVE applicability, concrete exposure, license violation, or compliance failure without appropriate evidence.
- `confirmed` confirms only the scope of the precise claim supported by evidence; do not inflate it into exploitability or impact not demonstrated.
- Use `needs-verification` when evidence is absent/stale/unbound to exact source identity.
- Do not call a static score, checklist, unexecuted scenario file, or model-only review behavioral validation.
- Current vulnerability/license/policy facts may require current primary/scanner evidence; if unavailable, report the limitation rather than guessing.

## Machine-readable report contract

A JSON report should contain at least:

- `report_version: security-review-report-1`
- `rubric_version: SGR-2.0`
- target name/identity and mode
- `review_status: complete | partial | blocked-critical-evidence`
- evidence snapshot/tree identity
- `critical_evidence_gaps`
- findings with classification/severity/confidence/location/evidence/risk/recommendation/validation/residual risk
- optional threat model conforming to `schemas/threat-model.schema.json`
- commands and outcomes
- evidence layers: `structural`, `behavioral`, `runtime`, `external_current`
- limitations

## Output contract

A complete review should include:

1. Mode, target, rubric/report version, and evidence identity.
2. Files/sources inspected plus protected/uninspected surfaces.
3. Executive posture stated without unsupported assurance.
4. Findings ordered by stable severity criteria, each with the full evidence mapping.
5. Threat model when requested/useful, with assumptions and evidence refs.
6. Dependency/supply-chain observations with dependency/source identity where applicable.
7. Governance/responsible-ai observations tied to actual authority/domain evidence.
8. Remediation plan with safe validation and rollback/containment where relevant.
9. Commands/gates with pass/fail/not-run.
10. Structural evidence separated from behavioral/runtime/external-current evidence.
11. Limitations, critical evidence gaps, and residual risk.

## Stop conditions

Stop before risky analysis or mutation when:

- output would require exposing a full secret;
- the user asks to execute destructive/untrusted code, malware, exploit code, or install hooks without a safe authorized sandbox;
- concrete findings are requested but no inspectable target exists;
- a current CVE/license/compliance conclusion requires evidence that is unavailable;
- remediation would mutate `.git`, credentials, `.env`, private keys, fixtures, expected outputs, frozen evaluators, generated baseline evidence, or unrelated project files;
- target/source identity changed after snapshot and trustworthy re-baselining cannot be done;
- the only way to reach a positive conclusion is to weaken evidence, redaction, or fail-closed gates.

## Host portability

Keep the semantic core host-independent and portable across compatible hosts. Use Agent Skills-compatible Markdown/references/scripts and Python standard-library helpers. Do not require ChatGPT-, Claude-, Copilot-, Cursor-, or other host-specific invocation semantics for correctness. Treat `agents/openai.yaml` as an optional adapter, not a core dependency.

If local command execution or Python 3.10+ is unavailable, continue with the safe read-only subset, mark script gates `not-run`, and do not claim those mechanical validations passed.

## Relationship to neighboring skills

- Use broad hardening/reproducibility skills for package maturity, activation, regression infrastructure, and packaging beyond this security/governance scope.
- Use secure-code-review for focused secret/credential handling in ordinary application code.
- Use this skill when security review spans skills/agents/scripts/dependencies together with authority, governance, responsible-ai, compliance evidence, or threat modeling.
