# Decompose mode

Use decompose mode when one existing spec package has broad remaining work that must be split into smaller dependency-safe execution tasks without changing the initiative boundary.

## Scope
- planning-only by default
- operate on exactly one existing spec package under `<cycle_version>/specs/<spec_id>/`
- keep the same PRD boundary unless decomposition reveals a real contradiction that requires a minimal correction

## Core protocol
- read existing canonical planning docs first
- keep the initiative boundary stable
- preserve correct history
- split broad remaining work into concrete, testable, independently reviewable tasks
- record assumptions and unresolved points in `notes.md`
- use specialist metadata only when it materially helps execution
- finish with the mandatory final review

## Decomposition rules
Split remaining todo work when a task is:
- too large for one bounded execution pass
- vague about the concrete change required
- mixing concerns that should be reviewed separately
- spanning multiple modules, services, layers, or boundaries without checkpoints
- missing prerequisites or unresolved dependencies
- impossible to validate clearly

When splitting:
- preserve original intent
- split by outcome, decision, artifact, boundary, or validation responsibility
- make dependencies explicit
- keep each resulting task independently reviewable

Do not over-fragment into administrative noise.

## Canonical artifact mapping
Update only the canonical files:
- `manifest.yaml` when status, phase, or source-of-truth alignment requires it
- `prd.md` only if decomposition exposes a real contradiction or missing requirement
- `tasks.md` for the task breakdown
- `validation.md` so validation matches the decomposed work
- `notes.md` for assumptions, risks, trade-offs, and specialist rationale

If the source material refers to `MANIFESTO.yaml`, uppercase filenames, or `docs/current`, reinterpret them into the canonical spec package instead of reproducing them.

## Final review
Review in this order:
1. `manifest.yaml`
2. `prd.md`
3. `validation.md`
4. `notes.md`
5. architecture impact when relevant

After review:
- keep the initiative boundary stable
- ensure broad work became execution-ready units
- ensure reasoning is proportional
- keep blocker and dependency guidance aligned across files
