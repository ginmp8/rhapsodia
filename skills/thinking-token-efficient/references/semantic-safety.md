# Semantic Safety

## Invariants

Before finalizing, preserve these duties when applicable:

- user intent, requested language, audience, and output format;
- hard constraints, blocked paths, protected files, and tool authority;
- evidence/citation/source/path/line duties;
- executed versus suggested validation;
- safety, privacy, security, legal, medical, financial, and policy boundaries;
- uncertainty, assumptions, and freshness requirements;
- final answer completeness.

## Equivalence test

A compressed reasoning path is acceptable only if a fuller normal path would produce the same answer, same caveats, same citations, same validation status, and same safety posture. If not, expand reasoning.

## Traceability

Do not collapse traceability into a vague word. If a claim depends on external or internal evidence, keep where it came from: citation, file path, line range, command output, report path, or inspected artifact.

## Chain-of-thought boundary

Hidden reasoning stays hidden. Provide a user-facing rationale or evidence summary instead of raw scratchpad. If the user asks for the exact private reasoning, summarize the key factors, assumptions, checks, and conclusion without exposing internal chain of thought.

## Language floor

Use concise English or the user's language. Avoid gibberish, arbitrary code words, random language changes, and over-compressed fragments that another expert could not audit. Brevity must not make reasoning brittle.

## Escalation triggers

Switch from dense or max-safe to readable when the task involves:

- high-stakes advice or irreversible action;
- code changes, production risk, security, credentials, or data loss;
- citations, file evidence, or up-to-date facts;
- multiple plausible interpretations;
- user-visible decisions that require trade-offs;
- previous attempt failure or tool error.
