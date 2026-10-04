---
name: secure-code-review
description: Review code, configuration, CI/CD, infrastructure-as-code, build artifacts, Git history, logs, examples, documentation, and agent skills for hardcoded secrets, credential exposure paths, unsafe secret loading or persistence, sensitive logging, and post-exposure remediation. Use when the main question is about credentials or secret handling. Do not use as the primary reviewer for unrelated application-security flaws such as injection, authorization, dependency vulnerabilities, or cryptographic design.
---

# Secure Code Review

## Purpose

Review **secret and credential exposure** with explicit coverage, redacted evidence, contextual risk assessment, and lifecycle-aware remediation. Keep automated detection separate from final security judgment: a detector match is a candidate signal, not proof of credential validity or impact severity.

This skill is intentionally narrow. Route unrelated application-security findings to a broader security review skill.

## Portable core and capabilities

Keep the semantic workflow host-neutral and compatible with the open Agent Skills format. `SKILL.md`, relative `scripts/`, `references/`, `schemas/`, and `evals/` are the portable core. `agents/openai.yaml` is optional OpenAI adapter metadata and must not be required for correctness.

Before executable review, detect capabilities rather than host names:

- filesystem read/write;
- Python 3.10+ or equivalent execution;
- Git CLI for optional Git history scanning;
- access to build artifacts, CI logs, container/image contents, or external validity metadata when those surfaces are requested.

If a capability is unavailable, mark that surface `not-run` or `unavailable`; never convert missing coverage into a clean result.

## Activation boundaries

Use this skill when the request is mainly about:

- hardcoded passwords, API keys, tokens, client secrets, signing/private keys, certificates with private material, session material, or credential-bearing connection strings;
- secrets in source, configuration, generated/build artifacts, repository history, CI/CD, IaC, containers, logs, examples, documentation, or agent skill packages;
- unsafe secret fallbacks, storage, injection, propagation, persistence, masking, rotation, or revocation;
- repository/file-tree scanning for credential exposure;
- remediation after a secret appears exposed.

Do not use it as the primary skill for SQL injection, XSS, authorization design, dependency CVEs, general threat modeling, exploit development, or broad secure-code posture unless the issue directly creates a credential exposure path.

Never attempt to authenticate with a discovered credential. Provider- or user-supplied **external validity** evidence may be consumed as evidence, but this skill does not create it by trying the credential.

## Modes and routing

Choose the smallest route that covers the requested surfaces:

1. **Direct review** — pasted snippets, screenshots, or a small set of files.
2. **Working-tree review** — scan a readable file/directory with `scan_secrets.py`, then semantically review findings and nearby code.
3. **Repository-history review** — when a Git repository is available and history matters, additionally run `scan_git_history.py`.
4. **Artifact/platform review** — inspect build artifacts, CI/CD, Docker, Kubernetes, Terraform, or similar secret-flow surfaces; load `references/platform-secret-review.md`.
5. **Agent skill review** — inspect an Agent Skill or agent workflow for credential leakage across instructions, scripts, tools, outputs, logs, and temporary files; load `references/agent-skill-credential-review.md`.
6. **Mixed review** — combine applicable surfaces and deduplicate by credential/exposure identity.

Do not invent repository, history, artifact, log, image, or external-system coverage.

## Coverage contract

Read `references/exposure-surfaces.md` for surface semantics. Track each material surface independently using:

`complete | partial | not-run | unavailable | not-applicable`

Typical surfaces include:

- working tree / supplied files;
- **Git history**;
- generated files and **build artifacts**;
- container/image contents;
- CI/CD configuration and logs;
- IaC/state/plan material;
- documentation/examples/tickets when supplied;
- agent skill instructions/scripts/stdout/stderr/tool arguments;
- external secret stores or provider validity metadata.

A `complete` working-tree scan means complete only for the scanner's supported text scope. It does not imply complete Git history, binary artifact, remote CI-log, external-system, or container-image coverage.

## Detection and risk contract

Keep three concepts separate:

1. **Detector signal** — regex/format/context candidate emitted by a scanner.
2. **Confidence** — how strongly available evidence indicates secret material: `confirmed | likely | possible`.
3. **Severity** — potential security impact after context: `critical | high | medium | low`.

Do not raise final severity merely because a string has high entropy, a known prefix, or a detector labels it strongly. Evaluate exposure surface, privilege/scope, environment, credential authority, lifetime, distribution breadth, and evidence of actual secret semantics. Use `references/security-policy.md`.

## Evidence and safety invariants

For every reported finding:

- preserve exact file/line/commit/section provenance when available;
- redact the credential; never reproduce a usable full value in reports, receipts, examples, or logs;
- distinguish real/likely credentials from placeholders, public identifiers, hashes, checksums, and synthetic fixtures;
- do not execute untrusted code or an untrusted agent skill merely to determine whether it leaks credentials;
- do not authenticate with discovered credentials;
- keep provider validity metadata explicitly external/supplied;
- state skipped/unavailable surfaces.

## Workflow

### 1. Establish scope and coverage

Record requested surfaces, available artifacts, capability limits, and the intended conclusion. If the user asks for "no secrets anywhere", expand coverage only to surfaces actually available and report the rest explicitly.

### 2. Run deterministic candidate detection

For a file or directory:

```text
<PYTHON> scripts/scan_secrets.py <TARGET> --format json --output <SCAN_JSON>
<PYTHON> scripts/validate_scan_result.py <SCAN_JSON>
```

The working-tree scanner includes supported text files under common build/output directories; binary and unsupported formats remain outside its proof surface.

For Git history when requested/available:

```text
<PYTHON> scripts/scan_git_history.py <REPOSITORY> --format json --output <HISTORY_JSON>
<PYTHON> scripts/validate_history_scan_result.py <HISTORY_JSON>
```

History scanning requires Git. Failure or absence of Git is `not-run`/`unavailable`, not a clean history result.

### 3. Review semantic context and secret flow

For every candidate or manually observed issue:

- determine whether the material is synthetic, public, encrypted, redacted, credential-bearing, or likely usable;
- trace where it comes from and where it flows: source/store -> process -> transport -> log/output/artifact/client;
- inspect nearby config, CI/CD, examples, logs, generated output, and build artifacts when available;
- consider transformed/derived credentials that simple masking may miss;
- load `references/platform-secret-review.md` for CI/CD, Docker, Kubernetes, Terraform, or IaC;
- load `references/agent-skill-credential-review.md` for agent skill / LLM workflow review.

A scanner hit alone is never `confirmed` merely because it matched a provider prefix.

### 4. Assess final severity and confidence

Apply `references/security-policy.md`. Keep severity and confidence independent. If authenticity is uncertain, lower confidence; do not automatically lower potential impact when the credential would be dangerous if real.

### 5. Deduplicate by defect and credential flow

Merge duplicate detector hits for the same source value/exposure path. Keep separate findings when remediation, exposure surface, credential authority, or post-exposure response materially differs.

### 6. Recommend lifecycle-aware remediation

Use `references/remediation-playbook.md`. Prefer eliminating static credentials through workload/managed/federated identity or short-lived credentials when the platform supports it. Managed secret storage or runtime injection is a fallback, not proof that every exposure path is safe.

For likely exposure, prioritize containment and rotation/revocation before optional history rewriting. Search available surfaces for copies/reuse and review privilege scope.

### 7. Validate the conclusion

- validate scanner JSON before trusting counts;
- if any requested/material surface is partial, unavailable, or not-run, keep the conclusion coverage-bounded;
- say `no candidate secrets found in inspected coverage`, not `no secrets`, unless the requested surface is actually complete and the evidence supports that stronger statement.

## Output contract v3

Use this structure unless the user requests another format.

### Security summary

State inspected scope, highest material risk, and the most important coverage limitation.

### Findings

For each finding include:

- **ID** — stable scanner/history ID when available;
- **Severity** — `critical | high | medium | low`;
- **Confidence** — `confirmed | likely | possible`;
- **Location** — file/line, commit/path/line, or precise section;
- **Rule** — narrow semantic category or detector rule;
- **Issue** — what is wrong;
- **Evidence** — minimum redacted evidence;
- **Risk** — concrete consequence if usable/exploitable;
- **Fix** — safest practical replacement;
- **Post-exposure** — rotation/revocation, reuse search, privilege review, and cleanup actions when applicable;
- **External validity** — `active | inactive | unknown | not-supplied` only when provider/user evidence exists; never self-derived by authentication.

### Coverage

Use a table with `surface | status | evidence/limitation`. Include every requested or materially relevant surface.

### Remediation checklist

Order by containment -> rotation/revocation -> active-path cleanup -> privilege reduction -> secondary-copy/history cleanup -> prevention.

## Stop conditions

Return a bounded partial review when:

- the requested artifact/repository/surface is unavailable or unreadable;
- safe inspection would require following a symlink outside scope;
- a binary/unsupported artifact is material but cannot be inspected;
- Git history is requested but Git/repository history is unavailable;
- determining validity would require authenticating with the discovered credential;
- a conclusion requires CI logs, remote artifacts, container images, secret stores, or external systems that were not supplied/accessible;
- an agent skill would need to be executed despite being untrusted merely to inspect possible credential leakage.

Report missing evidence instead of inferring a clean result.

## Progressive resources

- `references/security-policy.md` — final severity/confidence, semantic taxonomy, evidence rules.
- `references/exposure-surfaces.md` — coverage model and completeness semantics.
- `references/remediation-playbook.md` — containment, identity-first replacement, rotation and cleanup.
- `references/platform-secret-review.md` — CI/CD, Docker, Kubernetes, Terraform and IaC secret-flow checks.
- `references/agent-skill-credential-review.md` — agent skill / LLM credential leakage review.
- `references/scanner-contract.md` — deterministic working-tree and history scanner contracts.
- `references/source-basis.md` — research/standards basis and freshness boundary.
- `schemas/scan-result.schema.json` — working-tree scanner JSON contract.
- `schemas/history-scan-result.schema.json` — Git history scanner JSON contract.
- `evals/review-scenarios.json` and `evals/research-regression-scenarios.json` — planned routing/regression scenarios; scenario definitions are not executed behavioral evidence.
