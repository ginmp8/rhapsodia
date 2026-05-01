# Execution Evidence

Use this reference when MAGIA produces structured downstream evidence, implementation notes, or execution-grounded technical documentation.

MAGIA evidence is for implementation truth: repository changes, files touched, tests, commands, runtime output, blockers, implementation decisions, validation results, and residual risks.

Magia does not create downstream governance or communication artifacts, including roadmap, release, status, stakeholder, portfolio, feature reporting, or release communication documents. Magia exposes evidence only; downstream consumers decide how to interpret and communicate it.

## Evidence Types

Record only evidence that was inspected, produced, or explicitly supplied:

- files inspected or changed;
- commands executed;
- tests passed or failed;
- static reasoning checks;
- logs or runtime output with secrets redacted;
- implementation decisions and ADRs;
- blockers and follow-ups;
- validation gaps and not-run reasons.

## Implementation Decisions and ADR Links

When execution produces a technical decision or implementation ADR, include:

- decision title;
- path to the documentation or ADR;
- evidence source;
- validation status;
- scope guard explaining why the decision did not rewrite product intent;
- handoff target when Mago or Magnomo must review.

## Boundary Rules

MAGIA must not rewrite planning intent, PRD content, task definitions, roadmap inputs, product scope, acceptance criteria, feature sequencing, or delivery commitments. Planning-origin artifacts remain execution inputs; their provenance is not a blocker. If execution reveals that planning content itself must change before safe implementation, record the concrete blocker or follow-up as execution evidence and hand off instead of rewriting planning artifacts.

Do not create or update downstream governance or communication artifacts from Magia. Do not add validators for downstream governance or communication artifacts.
