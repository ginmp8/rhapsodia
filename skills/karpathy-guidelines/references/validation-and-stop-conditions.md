# Validation and Stop Conditions

Use this reference when verification is incomplete, scope is unsafe, inputs are missing, or the requested change risks exceeding the evidence.

## Failure-model validation

Start with the claim that could be wrong, then choose an oracle that can falsify it. Prefer the narrowest relevant check first and broaden only when contracts or risk require it.

| Failure model / claim | Preferred evidence |
|---|---|
| reproducible functional bug | reproduce failing case -> patch -> rerun it -> relevant regression cases |
| semantic behavior/invariant | focused behavioral tests or before/after observations that exercise the invariant |
| public/type/API contract | compiler/type/schema checks plus affected consumer tests when available |
| refactor equivalence | before/after behavior over representative cases; passing build alone is insufficient |
| performance | benchmark/profile/latency or resource measurement with comparable conditions |
| concurrency/idempotency/retry | invariant, interleaving, stress, replay, or retry-specific evidence |
| security-sensitive behavior | threat-specific test/scanner/static analysis plus specialized security review when material |
| configuration/CI/infrastructure | parser/plan/diff/check mode plus focused smoke/postcondition evidence |
| packaging/artifact integrity | package validator, content/hash check, deterministic build where relevant |

A generic test suite, build, lint pass, or static inspection can be useful adjacent evidence but must not be reported as proof of semantics it does not exercise. When no suitable oracle can run, report the claim as not executed or unverified and name the best next check.

## Scope control

Before changing or recommending changes, confirm each edit is traceable to the request or an explicit invariant. Do not reformat, rename, replace frameworks, add defensive configurability, delete unrelated code, or patch incidental findings as part of a local fix.

Mention unrelated observations separately when they materially affect risk.

## Action risk boundary

Classify the action independently from diff size:

- **local + reversible + scoped**: proceed with normal validation;
- **external or state-changing**: verify the intended target, authorization, and expected postcondition before execution;
- **destructive, production, high-blast-radius, or difficult to reverse**: require explicit authority plus a credible recovery/rollback path before execution.

A tiny code diff can still have high operational blast radius. Do not use user urgency or model confidence as a substitute for authority/recovery evidence.

## Unsafe or under-specified requests

Stop, narrow, or ask for the missing blocker only when continuing risks a materially wrong or unsafe result. Examples:

- no relevant code/error/artifact exists for a concrete fix;
- requested behavior has materially different valid interpretations;
- verification requires unavailable credentials, systems, data, or tools;
- a broad instruction such as "handle every error" or "rewrite everything" lacks a bounded failure model;
- performance, reliability, security, or production-readiness conclusions lack the evidence needed to support them;
- destructive/external action lacks the required authority or recovery path.

When the blocker is not fatal, proceed under a specific assumption and keep the change small.

## Validation reporting

Report executed checks with command/observation and outcome. Report not-executed checks separately with the reason or the best next check. Preserve failures as evidence; do not replace a stronger failing gate with a weaker passing one and imply closure.

If multiple checks pass, state what they establish. Do not infer full semantic equivalence, safety, or performance from a check whose scope is narrower.

## Security escalation

Treat changes involving authentication, authorization, secrets, untrusted input, injection surfaces, cryptography, unsafe deserialization, permission boundaries, or sensitive data as security-sensitive even when the diff is small.

When a stricter security-review/hardening workflow is available, defer security-specific analysis and acceptance to it. Keep Karpathy Guidelines secondary for scope, smallest-change, evidence, and overengineering discipline. Do not duplicate a full security framework here.

## Sensitive-value handling

If code or logs include credentials, tokens, keys, connection strings, or other secrets, do not repeat the value. Flag the exposure, recommend rotation when plausible, and use the approved secret/environment mechanism in examples or fixes.
