# Validation Gates

## Runtime behavior gate

Before finalizing a response, check:

- the answer addresses the actual request and requested format;
- hard semantic obligations and the applicable quality floor are satisfied;
- compression or lower effort did not remove a material assumption, caveat, citation, evidence path, validation result, compatibility duty, or safety boundary;
- sources and dates are current when required;
- file, command, test, package, or runtime claims have the right evidence label;
- completion/truncation state is acceptable for the requested result;
- visible text is readable and is not a dump of private reasoning.

## Activation gate

Activate for multi-step private reasoning, adaptive effort control, tool planning, code/artifact analysis, evidence synthesis, validation-heavy work, or explicit requests to reduce unnecessary reasoning work without lowering quality. Do not activate for simple direct answers, ordinary rewriting/translation, or visible prose compression by itself.

## Effort gate

Choose the minimum safe `direct|light|standard|deep` effort from `references/adaptive-effort-policy.md`. Escalate when risk, ambiguity, evidence burden, failed checks, contradictions, or validation complexity increase. Do not lower effort merely to satisfy a token/latency target.

## Compression-level gate

Use `readable` whenever risk, ambiguity, citations, code correctness, destructive actions, security, or a failed attempt increases the cost of omission. Use `dense` only after obligations are stable. Use `max-safe` only for low-risk substeps with stable success criteria.

Representation and effort are independent. Escalation is one-way for the current risky subproblem until the triggering condition is resolved.

## Sufficiency gate

After each material step, stop only when applicable obligations are satisfied, the answer/decision is stable under current evidence, no material contradiction remains, required validation is complete or honestly bounded, the output is complete, and another step has no plausible material information gain.

Confidence alone is not a stopping proof. Missing citations, failed checks, unresolved contradictions, or truncation require continuation, escalation, or a bounded limitation.

## Capability and portability gate

The portable core must remain valid when host-specific reasoning controls are absent. Host adapters may map effort, telemetry, state continuity, truncation, caching, or lazy-tool features, but no core correctness rule may require a vendor-private parameter or runtime.

When reasoning-state preservation is unavailable, use only a compact semantic checkpoint; never reconstruct or expose hidden chain of thought.

## Package update gate

For an existing-package update, require all applicable checks:

1. immutable baseline preserved;
2. evaluator used for before/after comparison frozen outside the candidate mutation surface;
3. baseline and candidate run through the same frozen baseline validator;
4. `scripts/token_audit.py` uses the same declared method for both;
5. `scripts/compare_candidate.py` reports no hard semantic/protected-literal loss;
6. candidate-owned `scripts/validate_skill.py` passes;
7. independent package validation passes;
8. requested-host structural portability passes for any multi-platform claim;
9. freeze after pass: final candidate identity is frozen after the last successful check;
10. package/receipt hashes refer to those exact frozen bytes;
11. rollback or last-known-good evidence is preserved until delivery succeeds.

A planned eval suite is not behavioral evidence. If no harness executes it, mark behavioral comparison `not-run`.

## Repair loop

For a failing objective gate: keep the diagnostic, apply the smallest supported fix, rerun the same gate, then adjacent gates. Stop that branch after two consecutive non-improving repairs unless new evidence changes the diagnosis. Never lower a threshold, edit a frozen evaluator, delete a semantic obligation, or accept truncated output merely to obtain a pass.

## Claim gate

Keep claim strength aligned to evidence:

- static footprint -> package/control-plane size only;
- structural validators -> contract/package preservation only;
- executed paired scenarios -> behavioral equivalence or delta under that evaluator;
- host telemetry -> hidden/billed token cost for the measured host/model/run only;
- latency/cost/cache metrics -> only the measured environment and run identity.

Quality and hard gates precede efficiency claims. Do not convert a lower evidence layer into a stronger claim.

## Package validation gate

Pass only when exactly one root `SKILL.md` exists; frontmatter is valid; local references resolve; scripts parse; scenario IDs/categories are valid; no blocked caches/archives/secrets/scaffold residue is included; and the package validator succeeds before a zip path is reported.
