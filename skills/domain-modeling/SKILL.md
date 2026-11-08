---
name: domain-modeling
description: "Clarify ubiquitous language, bounded contexts, domain invariants and decision trade-offs through concrete scenarios; propose glossary entries and ADRs. Use when domain terminology or model boundaries are unresolved. Not for generic repository inventory, implementation or bypassing Mago's canonical planning ownership."
---

# Domain Modeling

## Mission and authority

Sharpen the language and boundaries of an existing product domain. Use real scenarios to distinguish entities, value objects, events, invariants and bounded contexts. **Mago owns canonical technical planning artifacts** in governed RhapsodIA workflows; this skill contributes evidence and proposed changes, never overrides that ownership.

## Workflow

1. Read the repository's existing `GLOSSARY.md`, optional `GLOSSARY-MAP.md`, design decisions, relevant code and approved Mago artifacts. Treat the repository and current normative requirements as evidence.
2. Identify ambiguous terms, synonyms that should not be interchangeable, overlapping aggregates or inconsistent meanings across contexts. Ask targeted **grilling** questions when only the user can resolve a domain choice.
3. Create small, realistic scenarios that distinguish competing meanings, edge cases, ownership boundaries and transitions. Verify claims against current implementation when available; do not assume code is the specification.
4. Record resolved vocabulary with one-to-two-sentence definitions and terms to avoid. Use [glossary format](GLOSSARY-FORMAT.md); do not put implementation detail into glossary definitions.
5. Propose ADRs sparingly: an ADR is justified when the choice is hard to reverse, surprising without its rationale and a real trade-off. Use [ADR format](ADR-FORMAT.md).
6. Edit only authorized documents and after validating current files and concurrent changes. Route canonical Mago-owned artifacts through Mago's approved handoff; otherwise deliver proposed changes rather than silently mutating them.

## Boundaries and output

Return: term/meaning/avoided synonyms, bounded context, tested scenarios, contradictions, accepted choices, deferred decisions, exact evidence and any document changes or proposed ADR paths. The user's actual decisions remain distinguishable from recommendations. Do not perform implementation, change delivery status or elevate unconfirmed terms into requirements.

## File conventions

Default to root `GLOSSARY.md` for a single context. For multiple established contexts, `GLOSSARY-MAP.md` may point to context-local glossaries. Preserve existing naming and use migration proposals rather than renaming legacy files automatically.
