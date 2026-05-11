# Security Review Rubric

Use this rubric to classify findings consistently.

## Evidence class

- `confirmed risk`: the target contains a concrete unsafe pattern, exposed sensitive value, dangerous operation, missing control in an active authority path, or scanner-backed issue.
- `potential risk`: the target contains a suspicious pattern, weak guardrail, incomplete policy, ambiguous permission, risky dependency pattern, or plausible misuse path that needs confirmation.
- `evidence limitation`: the target lacks enough files, manifests, policy context, runtime configuration, scanner output, or domain detail to confirm or dismiss a risk.

Never upgrade a finding from potential to confirmed solely because a variable name contains `token`, `secret`, `password`, `admin`, or `agent`.

## Severity

- `critical`: likely credential compromise, arbitrary code execution, destructive command path, unrestricted high-impact tool authority, or unsafe automation that can directly cause severe financial, legal, safety, or data harm.
- `high`: exploitable secret exposure, unsafe command execution with user input, broad write/delete authority, missing authorization on privileged actions, unreviewed dependency execution hooks, or serious responsible-ai harm without mitigation.
- `medium`: meaningful weakness that requires additional conditions, such as missing audit logs, weak allowlists, path traversal risk without a proven write primitive, unpinned dependencies in a controlled package, or incomplete human approval.
- `low`: hygiene issue, weak documentation, missing validation gate, non-sensitive sample issue, or defense-in-depth improvement.
- `informational`: observation, context, or limitation without an immediate risk claim.

## Confidence

- `high`: exact file evidence, deterministic static scan, manifest evidence, or supplied runtime/security output supports the finding.
- `medium`: strong pattern evidence exists but exploitability, environment, or policy context is incomplete.
- `low`: only weak indicators or absent context are available.

## Review gates

A security/governance review should not be marked complete unless:

1. The target scope and mode are stated.
2. Secrets are masked in outputs.
3. Confirmed risks are separated from potential risks and limitations.
4. Every high or critical finding has a containment or validation recommendation.
5. Dangerous commands are not executed as part of review.
6. Dependency vulnerability claims are backed by scanner output, manifest evidence plus current source, or user-provided evidence.
7. Responsible-ai findings tie to the domain and affected users.
8. Agent governance findings tie to authority, tools, policy, audit, fallback, or handoff evidence.
9. Limitations are explicit.

## Prioritization model

Prioritize by combined impact, likelihood, authority level, blast radius, evidence strength, and remediation effort:

1. Exposure containment: secrets, credentials, private keys, sensitive logs.
2. Execution containment: dangerous shell, subprocess, deserialization, archive extraction, path traversal.
3. Authority containment: tool permissions, allowlists, approval gates, fail-closed policy, audit trail.
4. Supply-chain containment: install hooks, floating dependencies, untrusted registries, unchecked lockfiles.
5. Responsible-ai containment: privacy, fairness, accessibility, explainability, opt-out, human override.
6. Documentation and validation: test gates, report templates, handoff clarity.

## Finding format

Use this format for findings:

```markdown
### [finding-id] [short title]
- **Mode:** secret-handling-review | script-security-review | dependency-risk-review | llm-agent-governance-review | responsible-ai-review | threat-model
- **Classification:** confirmed risk | potential risk | evidence limitation
- **Severity:** critical | high | medium | low | informational
- **Confidence:** high | medium | low
- **Location:** file path and line, function, section, or unavailable
- **Evidence:** masked excerpt or precise description
- **Risk:** impact and abuse path
- **Recommendation:** safe change or control
- **Validation gate:** how to verify the fix
- **Residual risk:** what remains after remediation
```
