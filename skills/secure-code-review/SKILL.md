---
name: secure-code-review
description: review code, configuration, infrastructure-as-code, ci/cd definitions, and technical examples for hardcoded secrets, unsafe credential handling, sensitive logging, and insecure secret usage. use when chatgpt needs to inspect pasted code, uploaded files, repositories, pull requests, scripts, yaml, json, env examples, docker files, or deployment manifests for tokens, api keys, passwords, connection strings, private keys, or weak secret-management practices.
---

# Secure Code Review

## Overview

Review technical artifacts for secret exposure and insecure credential-handling patterns. Identify concrete findings, explain the risk, and recommend safer replacements such as environment variables, managed secret stores, workload identity, or short-lived credentials.

## Core Review Flow

1. Classify the input.
   - Treat source code, configuration, IaC, CI/CD files, shell scripts, examples, and documentation as in scope.
   - Treat values as sensitive when they can grant access, decrypt data, or reveal internal topology.

2. Look for the highest-risk issues first.
   - Hardcoded passwords, tokens, API keys, client secrets, private keys, certificates, and connection strings.
   - Secrets embedded in examples, tests, fixtures, Dockerfiles, compose files, Terraform, Kubernetes manifests, GitHub Actions, and application settings.
   - Logging or printing of credentials, authorization headers, cookies, JWTs, session IDs, or full connection strings.
   - “Temporary” fallback secrets, default credentials, and secrets stored in comments.

3. Distinguish suspicious strings from true findings.
   - Do not label placeholders such as `your_api_key_here`, `example-password`, `changeme`, or obvious fake values as confirmed leaks.
   - Mark uncertain cases as `needs verification` when the pattern is suspicious but the value may be synthetic.
   - Treat private-key blocks, real provider token formats, and live-looking connection strings as strong evidence.

4. Recommend remediation with a direct replacement path.
   - Move runtime secrets to environment variables only as a minimum baseline.
   - Prefer a managed secret store when the deployment platform supports one.
   - Prefer identity-based access over long-lived static credentials when available.
   - Recommend rotation and revocation for any exposed real secret.
   - Recommend log redaction, masking, and least-privilege scoping when the issue involves output or observability.

5. Produce a structured review.
   - Summarize the security posture in 1-2 sentences.
   - List findings ordered by severity.
   - For each finding, include: severity, location, evidence, why it matters, and the safest practical fix.
   - End with a concise remediation checklist.

## Review Rules

### Treat these as findings

- Secrets hardcoded directly in code or config.
- Secrets concatenated from multiple literals in the same file.
- Base64-encoded secrets when their purpose is still credential storage rather than harmless transport.
- Full database URIs that include usernames or passwords.
- Private keys or PEM blocks committed anywhere in the artifact.
- Authorization headers, bearer tokens, cookies, or session values shown in logs, tests, screenshots, or examples.
- Secrets stored in comments, TODOs, sample payloads, or documentation.

### Treat these as weaker signals unless corroborated

- Variable names like `token`, `secret`, `password`, or `key` without a real value.
- Placeholder strings or obvious documentation examples.
- Random-looking strings without context.
- Hashes or IDs that are non-secret identifiers.

### Escalate severity when any of the following apply

- The value looks valid for a known provider format.
- The secret is in a public-facing artifact, client-side bundle, mobile app, or frontend code.
- The secret appears in version-controlled history, CI logs, or shared screenshots.
- The credential has broad scope, admin access, production access, or long-lived expiry.

## Remediation Priorities

### Preferred replacement order

1. Replace hardcoded credentials with workload identity, instance roles, or federated identity.
2. Otherwise, load secrets from a managed secret store.
3. Otherwise, inject them via deployment-time environment variables.
4. Avoid local `.env` files in committed repositories except as untracked developer-only scaffolding, and keep `.env.example` free of real values.

### Always recommend after exposure

- Rotate or revoke the exposed credential.
- Remove the secret from active code paths.
- Check logs, build systems, and documentation for the same value.
- Audit blast radius and permissions.
- Add or improve automated secret scanning.

## Output Format

Use this structure unless the user asks for a different format:

### Security summary
One short paragraph.

### Findings
For each finding, use:
- **Severity:** critical | high | medium | low | needs verification
- **Location:** file and line, or snippet section when exact lines are unavailable
- **Issue:** what was found
- **Evidence:** brief quoted fragment or precise description
- **Risk:** why it matters
- **Fix:** the safest practical replacement

### Remediation checklist
- immediate containment
- code/config cleanup
- rotation or revocation
- preventive guardrails

## Using the bundled scanner

Use `scripts/scan_secrets.py` when files are available in the working directory and a deterministic scan will improve coverage. The scanner is especially useful for repositories, config trees, infrastructure folders, and mixed-language codebases.

Example:

```bash
python scripts/scan_secrets.py /path/to/project
python scripts/scan_secrets.py /path/to/file --format json
```

Use the script results as supporting evidence, not as the sole judgment. Manually review likely false positives before presenting a final conclusion.

## References

- Use `references/security-policy.md` for the review standard and severity model.
- Use `references/remediation-playbook.md` for concrete replacement and cleanup guidance.
