---
name: archify-review
description: "Review Archify issues, pull requests, code, contracts and maintainability using evidence-based Value, Cost and Impact decisions. Verify scope agreement, current branch, compatibility, source-backed behavior and required tests. Use for Archify maintenance triage or PR reviews, not generic code review, diagram generation, release execution or automatic approval/merge."
---

# Archify Review

Review Archify changes against the **actual target repository revision**, not a presumed branch or stale policy. Judge the problem and proposed solution on three axes:

- **Value**: Who benefits, what user-visible harm exists, and why is the work worthwhile now?
- **Cost**: Implementation, verification, complexity and long-term support; can a smaller existing solution work?
- **Impact**: Changed and preserved behavior, callers, compatibility, users, security and future maintenance.

## Review workflow

1. Identify the repository, target branch and candidate head. Check the linked issue, required scope agreement and current-base behavior. **Do not assume `dev` exists in a fork**; use actual refs. Read [Review readiness](references/REVIEWING.md).
2. Reconstruct the affected behavior, public contracts and user value. Distinguish verified observations, existing receipts, hypotheses and missing evidence. A reproduction is evidence of a failure, not automatically approval for a proposed solution.
3. Classify changed code and requirements using [Contribution and impact policy](references/CONTRIBUTING.md). Include other diagram types when shared routing, rendering, schemas, text measurement, Viewer or delivery code can affect them.
4. Inspect code, relevant call paths and tests. Where risk is material, compare the same frozen input against base/candidate; separate deterministic validation, browser measurements and perceptual judgment. Do not accept regenerated snapshots alone as independent proof.
5. Give one disposition: **Blocking defect**, **Required evidence/scope decision**, **Suggestion**, or **Ready**. Every material finding needs the trigger, impact, location/evidence and smallest adequate fix or verification.
6. On re-review, pin the new head, check changes since the previous review and invalidating updates to the base. Keep unrelated findings out of the current PR. **A review never authorizes approval, merge, deployment, release or publication by itself.**

## Output contract and stop condition

Lead with whether the change is worth doing and whether the candidate is acceptable, then state material findings by severity, supporting evidence and remaining uncertainty. Keep evidence from a real run separate from CI claims and author-reported tests. Stop short of a `Ready` verdict if a blocking defect or required authorization/evidence is unresolved. If the target repo cannot be inspected, provide a limited checklist rather than an invented review.

## Source scope

This is a **portable review adaptation** of the Archify reviewer in `ginmp8/archify` at commit `a4065941f12be7967436261d9934784e381d423c`. Project policy may change; when reviewing a newer revision, read the repository's current `REVIEWING.md` and `CONTRIBUTING.md`. This packaged skill contains concise decisions, not a frozen complete copy of those large governance documents.
