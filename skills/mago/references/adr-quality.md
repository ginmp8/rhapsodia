# ADR Quality

Use when notes.md design decisions, technical-design.md trade-offs, architecture-decisions.md, or spec-scoped ADR files are in scope.

MAGO owns planning-level architecture rationale and planned Architecture Decision Records. It does not own nomia governance decision logs and it does not own Magia execution-grounded implementation ADRs.

## Planning Decision Quality

- State decisions directly; avoid titles or bullets phrased as questions.
- Include the technical context or force that made the decision necessary.
- Tie the choice to repository truth, discovery evidence, nomia handoff, roadmap evidence, explicit user input, or a necessary downstream planning constraint.
- Record the main rejected alternative when it affects future planning.
- Include the accepted downside or trade-off when one exists.
- Include validation expectations for Magia, not executed validation claims.
- Preserve historical rationale unless repository truth shows it was wrong; add a new dated note or correction instead of silently rewriting meaning.

Good planning rationale includes system boundary choices, contracts, data persistence, workflow orchestration, eventing, dependency posture, validation strategy, package shape, migration strategy, rollback strategy, observability, security posture, and task split rationale.

Do not create governance decision logs from Mago. For material roadmap, priority, stakeholder, ownership, due date, or business-risk decisions, hand off to nomia.
Priority terminology in this file follows `references/priority-contract.md`: Nomia-owned business priority remains read-only; Mago owns technical criticality and execution sequence.

Do not create implementation ADRs from Mago after code has been changed unless Magia supplied execution evidence and the request is to refine planning records based on that evidence.

