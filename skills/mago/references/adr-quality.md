# ADR Quality

Use when notes.md `Design Decisions` or `Trade-Offs` are in scope.

Mago may record planning-level rationale inside the selected spec package, but it does not own Magnomo ADR records, repository-wide ADRs, or Magia execution decisions.

## Planning Decision Quality

- State decisions directly; avoid titles or bullets phrased as questions.
- Include the context or force that made the decision necessary.
- Tie the choice to repository truth, discovery evidence, roadmap evidence, or a necessary downstream planning constraint.
- Record the main rejected alternative when it affects future planning.
- Include the accepted downside or trade-off when one exists.
- Preserve historical rationale unless repository truth shows it was wrong; add a new dated note or correction instead of silently rewriting meaning.

Good planning rationale includes spec boundary choices, non-goals, dependency posture, validation strategy, package shape, or task split rationale.

Do not create governance ADRs from Mago. For material roadmap, priority, stakeholder, ownership, or handoff decisions, use Magnomo `adr-record`.

