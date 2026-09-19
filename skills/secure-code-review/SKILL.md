---
name: secure-code-review
description: review code, configuration, infrastructure-as-code, ci/cd, logs, examples, and technical documentation specifically for hardcoded secrets, credential exposure, sensitive logging, unsafe secret loading, and remediation. use for focused secret/credential review of pasted code, files, repositories, yaml, json, env examples, docker files, or deployment manifests. do not use as the primary reviewer for unrelated application-security flaws.
---

# Secure Code Review

## Purpose

Review code, configuration, infrastructure-as-code, CI/CD, examples, logs, and technical documentation for **secret exposure and insecure credential handling**. Produce evidence-linked findings without copying usable credentials into the review itself.

This is a focused security skill. It is not the primary reviewer for injection, authorization logic, dependency vulnerabilities, cryptography design, threat modeling, or broad application-security posture unless those issues directly concern secrets or credentials.

## Activation boundaries

Use this skill when the request is mainly about one or more of:

- hardcoded passwords, tokens, API keys, client secrets, signing keys, private keys, certificates with private material, or credential-bearing connection strings;
- secrets in source, configuration, IaC, CI/CD, tests, examples, screenshots, logs, or documentation;
- unsafe credential loading, fallback secrets, long-lived static credentials, or secret redaction;
- repository or file-tree scanning for likely secret exposure;
- remediation after a secret appears to have been exposed.

Do not use it as the primary skill for:

- a general secure-code review whose main risks are unrelated to credentials;
- vulnerability research or exploit development;
- validating whether a credential is live by attempting authentication;
- generic code quality or architecture review with no secret-handling question.

If the request spans broad security/governance plus credentials, keep this skill responsible only for the credential/secret portion or route to the broader security skill.

## Modes and routing

Choose one route before reviewing:

1. **Direct review** — pasted snippets, screenshots, or a small number of files. Review manually against the policy and output contract.
2. **Filesystem review** — a readable file or directory is available. Run the bundled scanner first, validate its JSON result, then perform semantic review of the scanner findings and relevant surrounding code.
3. **Mixed review** — both pasted context and a filesystem target exist. Scan the target and review the supplied context separately; merge findings by stable issue identity without duplicating the same exposure.

Do not invent repository coverage. If a requested file, history, log, branch, or external system is unavailable, say that surface was not inspected.

## Evidence and safety contract

Before reporting a finding:

- distinguish a real or likely credential from synthetic examples, public identifiers, hashes, and random-looking non-secret IDs;
- do not echo a full suspected credential in the answer, scanner evidence, logs, receipts, or examples;
- use the minimum redacted fragment needed to locate the issue;
- preserve file/line provenance when available;
- separate **severity** from **confidence**;
- do not attempt to authenticate with a discovered credential as part of this skill.

A scanner match is supporting evidence, not proof that a credential is live. A manual finding still requires concrete source evidence.

## Severity and confidence

Use the versioned rules in [`references/security-policy.md`](references/security-policy.md).

Severity is one of:

`critical | high | medium | low`

Confidence is one of:

`confirmed | likely | possible`

`possible` replaces the old practice of using "needs verification" as if it were a severity. If authenticity is uncertain, keep the potential impact severity and lower confidence instead.

Order findings by:

`severity desc -> path -> line -> rule -> finding id`

Do not raise severity only because a string looks random. Exposure surface, privilege, environment, credential type, and evidence determine severity.

## Review workflow

### 1. Establish scope and coverage

Record what was actually inspected: pasted content, exact files/directories, repository surface, logs, history, or screenshots. Note inaccessible or intentionally skipped surfaces.

### 2. Run deterministic scanning when files are available

```bash
python3 scripts/scan_secrets.py /path/to/target --format json --output /tmp/secure-code-review-scan.json
python3 scripts/validate_scan_result.py /tmp/secure-code-review-scan.json
```

The scanner:

- traverses files canonically;
- does not follow symbolic-link files;
- emits relative paths and stable finding IDs;
- redacts matched credential material;
- reports skipped files and scan counts;
- does not claim that zero matches means zero secrets outside scanned coverage.

Read [`references/scanner-contract.md`](references/scanner-contract.md) before interpreting partial coverage or scanner diagnostics.

### 3. Review semantic context

For each candidate:

- determine whether the value is synthetic, public, redacted, encrypted, credential-bearing, or likely usable;
- inspect how the value is loaded, transmitted, logged, persisted, and scoped;
- look for related copies in nearby config, tests, CI/CD, examples, and logging code when those surfaces are available;
- distinguish storage risk from exposure risk and post-exposure response.

Do not promote a scanner heuristic directly into a confirmed finding without reviewing context.

### 4. Deduplicate

Merge detections that describe the same source location and secret-handling defect. Prefer the more specific rule over a generic entropy/assignment rule. Keep separate findings when remediation, exposure surface, or credential identity materially differs.

### 5. Recommend the safest practical remediation

Use [`references/remediation-playbook.md`](references/remediation-playbook.md). Preferred order:

1. workload, instance, or federated identity;
2. managed secret store;
3. deployment-time secret injection;
4. developer-local untracked configuration only when the stronger options do not fit the environment.

For likely exposed credentials, include rotation or revocation, reuse search, least-privilege review, and preventive scanning where applicable.

### 6. Validate claims

If the scanner reports skipped files, unreadable files, size limits, or unsupported surfaces, phrase the conclusion as coverage-bounded. Do not write "no secrets" unless the requested surface was completely inspected and the evidence supports that statement.

## Output contract v2

Use this structure unless the user requests another format.

### Security summary

One short paragraph stating the inspected scope, highest material risk, and any important coverage limitation.

### Findings

For each finding:

- **ID:** stable identifier when available
- **Severity:** critical | high | medium | low
- **Confidence:** confirmed | likely | possible
- **Location:** file and line, or precise section when lines are unavailable
- **Rule:** stable category such as `hardcoded_credential`, `credential_in_log`, `private_key_material`, or scanner rule ID
- **Issue:** what is wrong
- **Evidence:** redacted, minimum necessary evidence
- **Risk:** concrete consequence if the credential is usable or the practice persists
- **Fix:** safest practical replacement
- **Post-exposure:** rotate/revoke and scope-audit actions when exposure is likely

### Coverage

State scanned/inspected surfaces and any skipped or unavailable surfaces. Omit this section only when the scope is trivially complete from the user-provided snippet.

### Remediation checklist

Order by containment first, then code/config cleanup, rotation/revocation, least privilege, and prevention.

## Stop conditions

Stop or return a bounded partial review when:

- the requested artifact is unavailable or unreadable;
- following a symlink would leave the requested scan root;
- a binary/unsupported format is material but cannot be inspected safely;
- a file is skipped by the scanner size or type policy and manual inspection is not feasible;
- determining whether a credential is live would require attempting authentication;
- a conclusion would require repository history, CI logs, or external systems that were not provided or accessible.

Report the missing evidence instead of inferring a clean result.

## Progressive references

- [`references/security-policy.md`](references/security-policy.md): severity, confidence, evidence, tie-breakers, and finding taxonomy.
- [`references/remediation-playbook.md`](references/remediation-playbook.md): containment and replacement guidance.
- [`references/scanner-contract.md`](references/scanner-contract.md): deterministic scanner behavior and coverage semantics.
- [`schemas/scan-result.schema.json`](schemas/scan-result.schema.json): machine-readable scanner output contract.
- [`references/source-basis.md`](references/source-basis.md): external standards and primary-source basis used to ground the policy.
- [`evals/review-scenarios.json`](evals/review-scenarios.json): planned activation/boundary/regression cases; these are scenario definitions, not executed behavioral evidence.
