# Activation Description Calibration Examples

Use these examples for static calibration only. They do not prove host-routing behavior.

## 1. Too broad

Bad:

> use when asked to improve skills or prompts.

Static findings:

- `ACTIVATION_FALSE_POSITIVE_RISK` — artifact/action ownership is too broad.
- `ACTIVATION_OVERLAP` — generic prompt authoring, hardening, benchmark, and implementation can collide.

Better:

> use when asked to review or rewrite existing skill activation descriptions, reusable agent instructions, trigger/non-trigger boundaries, stop conditions, activation scenarios, or output contracts. do not use for generic prompt creation, full benchmarking/harness execution, package-wide hardening, repository implementation, or unrelated writing/code review.

Why: it names owned artifacts/actions and adjacent non-trigger boundaries without encoding host-specific invocation syntax.

## 2. Keyword routing

Bad:

> use this whenever the user says prompt, skill, trigger, or agent.

Static finding: `ACTIVATION_FALSE_POSITIVE_RISK`.

Better:

> route by requested artifact + action + ownership; keywords alone are insufficient.

Why: satisfies ACT-001 and OVL-001.

## 3. Unfounded validation claim

Bad:

> validate that this description has high precision and recall.

Static finding: `EVIDENCE_CLAIM`.

Better:

> review the description statically, define/freeze scenarios, and report precision/recall only if baseline and candidate are actually executed against the same frozen suite/evaluator.

Why: follows EVD-001 and CLM-001.

## 4. Mixed-scope request

Input:

> Review the activation description and fix the package's failing Python validator.

Expected handling:

- review the activation surface here;
- do not claim validator implementation ownership;
- split/handoff the implementation portion when a suitable workflow exists.

This is a boundary/overlap case, not a reason to broaden the reviewer.
