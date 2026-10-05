---
name: secure-code-review
description: Review secret and credential exposure across code, configuration, CI/CD, IaC, build artifacts, Git history, logs, docs/examples, containers, and agent skills. Use when the primary question is hardcoded credentials, unsafe secret handling, credential leakage, rotation/revocation, or post-exposure cleanup. Do not use as the primary reviewer for unrelated application-security issues such as injection, authorization, dependency CVEs, or cryptographic design.
---

# Secure Code Review

## Mission and ownership

Review **secret and credential exposure** with explicit per-surface coverage, redacted evidence, semantic risk assessment, and lifecycle-aware remediation. Automated detection produces candidate signals; it never proves credential validity, confidence, or severity by itself.

Keep this skill narrow. Route unrelated application-security findings to a broader security review skill. Keep the semantic core host-neutral; detect capabilities rather than host names, and never make optional host adapters required for correctness.

## Activate and route

Use this skill when the main question concerns hardcoded passwords/API keys/tokens/client secrets/signing or private keys/certificates with private material/session material/credential-bearing connection strings; unsafe secret fallbacks, loading, storage/persistence, injection/propagation, logging, masking, rotation/revocation; repository or history secret scanning; or exposure across source, artifacts, CI/CD, IaC, containers, docs/examples, logs, or agent skills.

Do **not** use it as the primary skill for SQL injection, XSS, authorization design, dependency vulnerabilities, general threat modeling, exploit development, or broad secure-code posture unless that issue directly creates a credential exposure path.

Never authenticate with a discovered credential. Provider- or user-supplied external validity evidence may be consumed, but this skill does not create validity evidence by trying the credential.

## Review routes

Choose the smallest route that covers the requested surfaces:

1. **Direct** — pasted snippets, screenshots, or a small file set.
2. **Working tree** — scan a readable file/directory with `scripts/scan_secrets.py`, then review semantic context.
3. **Git history** — add `scripts/scan_git_history.py` when history matters and Git is available.
4. **Platform/artifact** — CI/CD, Docker, Kubernetes, Terraform/IaC, build artifacts; load `references/platform-secret-review.md`.
5. **Agent skill** — instructions, scripts, tool args, stdout/stderr, outputs, temporary files; load `references/agent-skill-credential-review.md`.
6. **Mixed** — combine applicable surfaces and deduplicate by credential/exposure identity.

## Quick-start workflow

1. **Scope coverage.** Record requested surfaces, available artifacts, capabilities, and intended conclusion. Track each material surface as `complete | partial | not-run | unavailable | not-applicable`. Missing access is never a clean result; do not invent repository, history, artifact, log, image, CI, container, or external-system coverage.
2. **Detect candidates deterministically.** For files/directories run `<PYTHON> scripts/scan_secrets.py <TARGET> --format json --output <SCAN_JSON>` then `<PYTHON> scripts/validate_scan_result.py <SCAN_JSON>`. For Git history run `<PYTHON> scripts/scan_git_history.py <REPOSITORY> --format json --output <HISTORY_JSON>` then `<PYTHON> scripts/validate_history_scan_result.py <HISTORY_JSON>`. Git absence/failure is `not-run`/`unavailable`, never a clean history result.
3. **Review semantics and flow.** Distinguish likely credentials from synthetic fixtures, public identifiers, public keys, hashes/checksums, encrypted/redacted material, and other non-secret values; trace `source/store -> process -> transport -> log/output/artifact/client`; inspect nearby config and reachable secondary copies. Keep **detector signal**, **confidence** (`confirmed | likely | possible`), and **severity** (`critical | high | medium | low`) independent. Base severity on exposure surface, privilege/authority, environment, lifetime, and distribution breadth. Apply `references/security-policy.md`.
4. **Remediate by lifecycle.** Prefer workload/managed/federated identity or short-lived credentials where supported. Managed secret storage or runtime injection is a fallback, not proof that every exposure path is safe. For likely exposure, prioritize containment and rotation/revocation, then active-path cleanup, privilege reduction, reuse/copy search, and only then optional history cleanup. Apply `references/remediation-playbook.md`.
5. **Validate the conclusion.** Validate scanner JSON before trusting counts. A `complete` working-tree scan covers only supported text scope, not Git history, binaries, remote CI logs, external systems, or container images. If any material surface is partial/unavailable/not-run, conclude `no candidate secrets found in inspected coverage` rather than `no secrets`.

## Non-negotiable safety and evidence invariants

- Preserve exact file/line/commit/section provenance when available.
- Redact credentials; never reproduce a usable full value in reports, receipts, examples, logs, or tool output.
- Never execute untrusted code or an untrusted agent skill merely to decide whether it leaks credentials.
- A scanner hit, provider prefix, entropy score, or token shape alone cannot make a finding `confirmed` or set high/critical severity.
- Keep provider validity metadata explicitly external/supplied; never self-derive it by authentication.
- State every skipped, partial, unavailable, or unsupported material surface.
- Return a bounded partial review when safe inspection would require escaping scope, executing untrusted material, authenticating with a credential, or accessing unavailable remote/binary surfaces.

## Direct branch references

All decision-critical Markdown is directly reachable from this file; do not require reference-to-reference hops.

- `references/exposure-surfaces.md` — coverage states and completeness semantics.
- `references/security-policy.md` — secret taxonomy, semantic categories, severity/confidence, evidence and deduplication rules.
- `references/remediation-playbook.md` — containment, identity-first replacement, rotation/revocation, copy search, cleanup.
- `references/platform-secret-review.md` — CI/CD, Docker, Kubernetes, Terraform/IaC and artifact-specific checks.
- `references/agent-skill-credential-review.md` — LLM/agent instruction, tool, log, output and temporary-file leakage.
- `references/scanner-contract.md` — deterministic scanner scope, exclusions, result contracts and validators.
- `references/source-basis.md` — standards/research basis and freshness boundary.

## Detailed coverage contract

Before executable review, detect capabilities rather than host names: filesystem read/write; Python 3.10+ or equivalent execution; Git CLI for history scanning; and access to requested artifacts, CI logs, container/image contents, or external validity metadata. If a capability is missing, mark the affected surface `not-run` or `unavailable`.

Typical surfaces are working tree/supplied files; Git history; generated files/build artifacts; container/image contents; CI/CD config/logs; IaC/state/plan material; docs/examples/tickets when supplied; agent instructions/scripts/stdout/stderr/tool arguments; and external secret-store/provider metadata. Read `references/exposure-surfaces.md` for exact semantics.

## Detailed semantic review

For every candidate or manually observed issue:

- determine whether material is synthetic, public, encrypted, redacted, credential-bearing, or likely usable;
- trace credential flow and inspect reachable copies or derived forms that simple masking can miss;
- inspect nearby configuration, CI/CD, examples, logs, generated output, and build artifacts when available;
- load `references/platform-secret-review.md` for platform/IaC surfaces and `references/agent-skill-credential-review.md` for agent/LLM surfaces;
- assess confidence independently from potential-impact severity using `references/security-policy.md`;
- merge duplicate detector hits for the same source value/exposure path, but keep findings separate when remediation, surface, authority, or post-exposure response differs.

If authenticity is uncertain, lower confidence; do not automatically lower potential-impact severity when the credential would be dangerous if real.

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

## Package resources

- `schemas/scan-result.schema.json` — working-tree scanner JSON contract.
- `schemas/history-scan-result.schema.json` — Git-history scanner JSON contract.
- `evals/review-scenarios.json` and `evals/research-regression-scenarios.json` — planned routing/regression scenarios; scenario definitions are not executed behavioral evidence.
- `agents/openai.yaml` — optional OpenAI adapter only; the portable core must not depend on it.
