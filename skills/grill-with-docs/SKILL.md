---
name: grill-with-docs
description: "Compose Grilling and Domain Modeling to clarify a design while drafting glossary entries, constraints and justified ADR proposals. Use for a requested documented decision interview; not for autonomous implementation, delivery governance or unilateral changes to Mago-owned artifacts."
---

# Grill with Docs

## Mission and routing

Compose **grilling** (decision interview) with **domain-modeling** (terms, contexts and decision documentation). This is a thin composition; it must not duplicate either skill or replace RhapsodIA's Mago planning authority.

## Workflow

1. Resolve the user-approved topic, repository, available evidence, target document locations, authorized write scope and any Mago-owned canonical artifacts.
2. Invoke **grilling** to develop the decision frontier and elicit actual choices. Use **domain-modeling** in parallel only for *read-only* discovery; write a term or decision only after the relevant user choice is settled.
3. As decisions are confirmed, draft concise glossary entries, scenario examples, and candidate ADRs. Only write to authorized user-owned documents; Mago-owned specs/ADRs require Mago's artifact pathway and validation.
4. If the user wants the accepted outcomes published, hand grounded, provenance-linked decisions to **Mago** for canonical technical documentation and to **Nomia** only when delivery/governance fields change. Never bypass owner contracts.
5. End with a short decision record: accepted, rejected, deferred, source evidence, unresolved dependencies and the exact document paths edited or proposed.

## Guardrails

- Do not fabricate user answers or convert recommendations into approved requirements.
- Do not create ADRs for trivial decisions; prefer an ADR when costly to reverse, surprising, and involving real alternatives.
- Do not write into another skill's owned artifact storage, a remote tracker or repository without authorization.
- Preserve existing glossary terminology and preexisting decisions; surface conflicts before editing.
- If either composable skill is unavailable, report the missing capability instead of silently replacing it.
