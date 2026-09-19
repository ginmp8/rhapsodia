# Semantic Safety

## Invariants

Before finalizing, preserve these duties when applicable:

- user intent, requested language, audience, and output format;
- hard constraints, blocked paths, protected files, and tool authority;
- evidence/citation/source/path/line duties, provenance, and freshness;
- executed versus suggested validation;
- safety, privacy, security, legal, medical, financial, and policy boundaries;
- uncertainty, assumptions, compatibility, and final-answer completeness;
- exact commands, schemas, flags, versions, numeric limits, and identifiers that affect correctness.

## Equivalence test

A compressed reasoning path is acceptable only if a fuller safe path would preserve the same conclusion, caveats, citations, validation status, and safety posture. If that cannot be established, expand reasoning.

This is a semantic criterion, not proof from wording similarity. Behavioral equivalence claims require executed paired scenarios when the distinction matters.

## Traceability

Do not collapse traceability into a vague word. Keep the evidence locator needed to audit a claim: citation, file path, line range, command output, report path, artifact identity, version, or source timestamp.

## Chain-of-thought boundary

Hidden reasoning stays hidden. Provide a user-facing rationale or evidence summary instead of raw scratchpad. If the user asks for exact private reasoning, summarize the key factors, assumptions, checks, and conclusion without exposing hidden chain of thought.

## Language floor

Use concise English or the user's language. Avoid gibberish, arbitrary code words, random language changes, and over-compressed fragments that another expert could not audit. Brevity must not make reasoning brittle.

## Escalation triggers

Switch from `dense` or `max-safe` to `readable` when the task involves:

- high-stakes or irreversible advice/action;
- code changes, production risk, security, credentials, or data loss;
- citations, file evidence, current facts, or external dependencies;
- multiple plausible interpretations;
- user-visible decisions requiring trade-offs;
- previous attempt failure or tool error;
- any unresolved contradiction between evidence and the proposed answer.
