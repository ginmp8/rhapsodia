---
name: security-and-governance-review
description: 'Use when the primary task is an evidence-based security/governance review of a skill or agent package, script, validator, template, or nearby helper project, including secrets/sensitive logging, unsafe shell/file handling, dependency or supply-chain risk, agent/tool authority, responsible AI or compliance evidence, threat modeling, and remediation planning. Default read-only. Do not use for broad package hardening/optimization, ordinary application or PR security review, MCP-only security review, or direct risky remediation.'
---

# Security and Governance Review

## Selection boundary

Use this skill when security/governance assurance is the primary objective for reusable AI/agent packages or their supporting technical artifacts. It owns evidence-based review across code/configuration plus authority, supply chain, responsible-AI, compliance-evidence, or threat-model concerns.

Do not use it as the primary skill for:

- broad skill quality, activation, portability, packaging, or hardening -> use a package hardening/optimization skill;
- ordinary application/PR bug or security review -> use the code/security reviewer that owns that target;
- focused secret/credential handling in ordinary application code -> use `secure-code-review`;
- MCP server/client/gateway security as the main subject -> use `mcp-security-review`; load this skill's MCP profile only when MCP is one surface in a broader package/agent review;
- implementing risky remediation. Review and plan first; mutate only with explicit authorization and separate validation gates.

## Critical rules and invariants

- **Read-only by default.** Never install dependencies, run untrusted hooks, perform destructive actions, mutate network state, or edit the target unless separately authorized.
- **Never reveal a complete secret.** Mask or omit credentials, tokens, private keys, cookies, session ids, passwords, or equivalent secret material.
- **Evidence before claims.** Do not claim vulnerability/CVE applicability, concrete exposure, license violation, conformity, certification, or compliance failure without evidence bound to the relevant target/source identity.
- **Fail closed on critical evidence gaps.** High-impact unknown authorization, stale/unbound CVE evidence, post-snapshot identity drift, or unsafe secret verification cannot produce positive assurance.
- **Capability is not authorization.** For high-impact agent actions, identify resource scope, authorization source, approval, audit/receipt, failure behavior, and rollback/containment where applicable.
- **Separate evidence layers.** Structural/static evidence is not behavioral, runtime, or external-current evidence; unexecuted scenarios and checklists never prove runtime enforcement.
- **Use SGR-2.0.** Every material finding is `confirmed`, `suspicious-pattern`, `governance-risk`, `needs-verification`, or `not-applicable`, with severity/confidence from `references/security-review-rubric.md`.
- **Map every material finding:** `finding -> evidence -> risk -> recommendation -> validation`, preserving source identity when available.
- Protect `.git`, credentials, `.env`, private keys, fixtures/golden inputs, expected outputs, frozen evaluators, generated baseline evidence, and user-declared protected paths from mutation.
- Reproducibility is analytic: equivalent evidence should yield materially comparable classifications, severity reasoning, mappings, gates, and report structure; do not mechanize analyst judgment merely for determinism.

## Modes

- `secret-handling-review`: secrets, credentials, `.env` leakage, sensitive logging.
- `script-security-review`: subprocess/shell injection, traversal, symlinks, archives, deserialization, broad deletes/writes.
- `dependency-risk-review`: manifests/locks, floating versions, install URLs/hooks, registries, provenance, licenses/policy, current vulnerability evidence.
- `llm-agent-governance-review`: authority, approvals, policy enforcement, audit, budgets/rates, handoffs, fail-closed behavior, cross-agent trust.
- `agentic-security-review`: goals/tools/privileges, memory/context, inter-agent trust, cascading failures, runtime controls, agentic supply chain.
- `responsible-ai-review`: privacy, fairness, accessibility, explainability, consent, automation impact, human override, exclusion; add lifecycle impact assessment for consequential systems.
- `threat-model`: assets, boundaries, actors, abuse cases, controls, assumptions, residual risks, validation probes.
- `remediation-plan`: prioritized fixes, owner assumption, safe order, validation, rollback/containment.
- `security-report` (default): complete evidence-based review and optional machine-readable report.

## Quick start

1. Resolve `TARGET_PATH`, mode, evidence policy, allowed actions, protected evidence, and requested output. If a concrete finding depends on ambiguous target identity, do not guess.
2. Read target `SKILL.md` first when present; inventory only relevant files and never follow symlinks into blocked/out-of-scope paths.
3. For filesystem targets, snapshot source identity to work storage outside the target before substantive conclusions; then run deterministic static triage when useful. Treat scanner matches as triage, not exploit/live-secret/CVE proof.
4. Load only the mode-specific references below. For agent/governance review, build an explicit authority boundary; for agentic systems, also record control-effectiveness level and runtime inventory when composition can drift independently of source bytes.
5. Classify findings with SGR-2.0, enforce evidence mapping, and block positive assurance when critical evidence is missing.
6. Validate JSON output with the core validator; run the extension validator when authority/inventory/control/framework/compliance extensions are present. Report every command as pass/fail/not-run.
7. Freeze the final evidence/report state. Any later edit affecting findings, evidence, redaction, classification, or validation requires rerunning affected gates.

## Direct resource map

Always load `references/security-review-rubric.md` for SGR-2.0 and `references/evidence-and-source-integrity.md` when identity, dependencies, current sources, or protected evidence matter.

- Secrets -> `references/secret-handling-checklist.md`.
- Scripts/files/archives -> `references/script-security-checklist.md`.
- Dependencies/build provenance -> `references/supply-chain-security.md`.
- Agent authority/governance -> `references/agent-governance-checklist.md`.
- Agent-specific attack surfaces -> `references/agentic-security-checklist.md` plus `references/runtime-control-and-inventory.md` when control/runtime drift matters.
- MCP as a secondary profile -> `references/mcp-security-profile.md`.
- Responsible AI -> `references/responsible-ai-checklist.md`; consequential systems -> `references/ai-impact-assessment.md`.
- Framework/regulatory mapping -> `references/framework-crosswalk-policy.md`; mapping is not conformity/certification/legal compliance.
- Report/threat-model output -> `assets/templates/security-report.md.template`, `schemas/security-review-report.schema.json`, `schemas/threat-model.schema.json`; optional authority/runtime/control extensions use the corresponding schemas under `schemas/`.
- Calibration/regression context -> `examples/security-review-prompts.md`, `evals/activation-scenarios.json`, `evals/agentic-security-scenarios.json`, and `evals/mcp-security-scenarios.json`; planned scenarios are not behavioral evidence until executed against frozen evaluator/runtime identity.

## Evidence tooling

Use the standard-library helpers when local Python is available. `<WORK>` must resolve outside the reviewed target.

```text
<PYTHON> scripts/evidence_snapshot.py --target <TARGET_PATH> --output <WORK>/evidence-receipt.json
<PYTHON> scripts/security_static_review.py --target <TARGET_PATH> --format json --output <WORK>/static-triage.json
```

The evidence snapshot records safe relative paths/hashes and protected states without contaminating target identity. Secret-bearing paths should be `protected-unread`; fixtures/expected outputs may be `protected-hash-only`. A hash proves identity, not safety.

Static triage uses deterministic ordering/ids/redaction. Pattern matches do not prove exploitability, a live credential, a CVE, or concrete exposure.

## Detailed review workflow

### 1. Resolve target, mode, authority, and protected scope

Record what may be read, what may be executed, and what is protected from mutation or content exposure. No authorization is inferred from capability or user intent that did not explicitly grant it.

### 2. Snapshot evidence identity before analysis

For a filesystem target, create the receipt before substantive conclusions when runtime permits. Reject output aliases or paths inside the reviewed target. If material source identity cannot be established, state the limitation; high-impact conclusions depending on that evidence fail closed.

### 3. Run deterministic static triage when useful

Keep triage output outside the target. The scanner is an evidence provider, not a finding classifier by itself.

### 4. Perform mode-specific review

For agent/governance work, build an authority matrix for meaningful read/write/execute/delete/send/publish/schedule/deploy/approve/delegate actions. Capability never implies authorization.

For agentic systems, classify the strongest supported control-effectiveness level (`declared`, `statically-present`, `behaviorally-demonstrated`, `runtime-observed`) and capture a separate runtime inventory when model/tool/policy/MCP/runtime configuration can drift independently of source bytes. Load the MCP profile only when MCP is actually in scope.

For supply-chain work, inspect provenance and privileged build/workflow boundaries in addition to package/CVE evidence. Absence of a specific attestation/BOM framework is not a vulnerability by itself.

For threat modeling, use the schema as structure while preserving evidence-based analyst judgment. State assumptions and evidence refs; do not generate arbitrary scores.

### 5. Classify with SGR-2.0

Assign exactly one canonical classification and then severity/confidence using the versioned rubric and tie-breakers. Do not upgrade from naming, intuition, keywords, or model consensus.

### 6. Enforce evidence mapping

Evidence should include source identity when available. For secrets, report only masked/omitted evidence. For current dependency/CVE claims, bind the claim to resolved dependency identity plus scanner/authoritative-source identity; otherwise use `needs-verification`. For living framework/protocol/regulatory mappings, record source version/date or retrieval identity and keep mapping separate from SGR severity/classification.

### 7. Fail closed on critical evidence gaps

Examples include unverifiable high-impact mutation authority, unresolved/current CVE evidence unavailable, target integrity drift after snapshot, or secret-like material whose authenticity/exposure cannot be safely established. In machine-readable reports, non-empty `critical_evidence_gaps` requires `review_status=blocked-critical-evidence`.

### 8. Validate output

For JSON reports:

```text
<PYTHON> scripts/validate_security_report.py <REPORT.json>
```

When optional authority/inventory/control/framework/compliance extension sections are present, also run:

```text
<PYTHON> scripts/validate_security_extensions.py <REPORT.json>
```

The extension validator is additive and never replaces the core validator. Do not imply dynamic/runtime checks passed when they were not run.

### 9. Finalize without post-pass mutation

Treat the final evidence/report gates as frozen. Any later edit affecting the reviewed conclusions invalidates the affected evidence and requires revalidation.

## Claims and evidence limits

- `confirmed` confirms only the precise claim supported by evidence; it does not automatically prove exploitability or broader impact.
- Use `needs-verification` when evidence is absent, stale, blocked, or unbound to exact source identity.
- Current vulnerability/license/policy facts may require current primary/scanner evidence. If freshness/applicability cannot be verified, report the limitation rather than guessing.
- A declared/statically present policy is not evidence that a runtime action was intercepted.
- Framework mapping is interpretation metadata, not proof of compliance, exploitability, or severity.

## Machine-readable report contract

A JSON report should contain at least:

- `report_version: security-review-report-1` and `rubric_version: SGR-2.0`;
- target name/identity, mode, and `review_status: complete | partial | blocked-critical-evidence`;
- evidence snapshot/tree identity and `critical_evidence_gaps`;
- findings with classification/severity/confidence/location/evidence/risk/recommendation/validation/residual risk;
- optional threat model conforming to `schemas/threat-model.schema.json`;
- commands and outcomes;
- evidence layers: `structural`, `behavioral`, `runtime`, `external_current`;
- limitations.

## Output contract

A complete review includes:

1. Mode, target, rubric/report version, and evidence identity.
2. Files/sources inspected plus protected/uninspected surfaces.
3. Executive posture without unsupported assurance.
4. Findings ordered by stable severity criteria with full evidence mapping.
5. Threat model when requested/useful, with assumptions and evidence refs.
6. Dependency/supply-chain observations with dependency/source identity when applicable.
7. Governance/responsible-AI observations tied to actual authority/domain evidence, including impact/reassessment records when consequential.
8. Remediation plan with safe validation and rollback/containment where relevant.
9. Commands/gates with pass/fail/not-run.
10. Structural evidence separated from behavioral/runtime/external-current evidence, including control-effectiveness and runtime-inventory identity when applicable.
11. Limitations, critical evidence gaps, and residual risk.

## Stop conditions

Stop before risky analysis or mutation when:

- output would require exposing a full secret;
- the request requires destructive/untrusted code, malware/exploit execution, or install hooks without a safe authorized sandbox;
- concrete findings are requested but no inspectable target exists;
- a current CVE/license/compliance conclusion requires evidence that is unavailable;
- remediation would mutate `.git`, credentials, `.env`, private keys, fixtures, expected outputs, frozen evaluators, generated baseline evidence, or unrelated project files;
- target/source identity changed after snapshot and trustworthy re-baselining cannot be done;
- positive assurance would require weakening evidence, redaction, or fail-closed gates.

## Host portability

Keep the semantic core host-independent across compatible hosts. Use Agent Skills-compatible Markdown/references/scripts and Python standard-library helpers. Host adapters such as `agents/openai.yaml` are optional and never core dependencies.

If local command execution or Python 3.10+ is unavailable, continue with the safe read-only subset, mark script gates `not-run`, and do not claim those mechanical validations passed.

## Relationship to neighboring skills

The selection boundary above is authoritative. Broad package maturity belongs to hardening/optimization skills; application/PR security belongs to code/security reviewers; focused secret handling in ordinary app code belongs to `secure-code-review`; MCP-only security belongs to `mcp-security-review`. This skill owns broader package/agent security-governance assurance when those concerns span artifacts, authority, supply chain, responsible AI, compliance evidence, or threat modeling.
