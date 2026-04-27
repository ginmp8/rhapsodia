# Delivery Mode

## Canonical Rules

- `BOARD_ROOT` is required for repository-facing delivery artifacts.
- Prompt-provided `BOARD_ROOT` takes precedence after validation; otherwise derive it from `references/canonical-paths.md`.
- `delivery-intake`, `delivery-triage`, `delivery-status`, and `delivery-replan` require a selected spec package under `BOARD_ROOT/specs/<spec_id>/`.
- Keep `ops.yaml`, `status.md`, `stakeholder-brief.md`, and `replanning.md` in the selected spec package.
- Keep `portfolio.yaml` and `portfolio.md` directly under `BOARD_ROOT`.
- Do not create missing spec package directories or Mago package files from a delivery mode.

Use for `delivery-intake`, `delivery-triage`, `delivery-status`, `delivery-replan`, and `delivery-portfolio`.

Keep the work delivery-governance only. Do not create roadmap artifacts, reporting artifacts, Mago task plans, Magia execution records, repository code, or release communication from a delivery mode.

## Shared Rules

- Use `ops.yaml` in the selected spec package as the structured source of truth for delivery metadata.
- Create or refresh Magnomo delivery artifacts with local scripts whenever a script can perform the template-backed operation. Use `scripts/write_artifact_scaffold.py` before filling factual values. Do not copy template text manually.
- Do not invent owners, stakeholders, repos, dates, commitments, blockers, status, or evidence.
- Treat candidate impacted repos as triage candidates, not confirmed implementation ownership.
- Run `scripts/validate_artifact.py` after creating or changing any Magnomo delivery artifact.

## delivery-intake

Convert raw demand into initial `ops.yaml`.

Inputs may be GitHub issue text, chat notes, email text, support notes, or rough demand. Extract only stated facts:

- Request title, requester, requested date, source, and context.
- Known owner, backup owner, stakeholders, watchers, or decision maker.
- Known sprint, planning bucket, target date, commitment, milestone, or rollout target.
- Known priority rationale, urgency, impact, risk, and cost of delay.
- Known blockers, tags, external links, and candidate impacted repos.

Set `status.state` to `intake` unless evidence supports a later state. Use the scaffold script and set `spec_id` to the selected package id.

Preferred creation command:

- `python .github/skills/magnomo/scripts/write_artifact_scaffold.py BOARD_ROOT/specs/<spec_id>/ops.yaml --spec-id <spec_id>`

## delivery-triage

Classify demand so humans can make planning decisions.

Update `ops.yaml` with planning bucket, priority, urgency, impact, risk, known owners/stakeholders, known dates/commitments, candidate repos, blockers, risks, tags, and links.

Create `stakeholder-brief.md` with `scripts/write_artifact_scaffold.py` when stakeholder communication, business decision making, timing alignment, or risk communication is required. Keep it business-facing and do not include implementation task lists.

## delivery-status

Update `status.md` from `ops.yaml` and optional supplied evidence.

Clearly separate:

- manual status: explicitly entered delivery status from `ops.yaml` or human notes
- inferred status: status derived from supplied or linked planning/execution evidence
- unknowns: missing evidence or facts that cannot be inferred

Do not claim implementation progress, validation, release, or deployment without evidence. If evidence is absent, say that evidence is unknown.

## delivery-replan

Record material changes to date, sprint, scope, owner, blocker, or commitment.

Always append a new event. Never rewrite prior replanning events except to add a dated correction for a factual error.

Update `ops.yaml`, `replanning.md`, and `status.md` together.

Each replanning event should include date, changed fields, from, to, reason, impact, and decision maker when known.

## delivery-portfolio

Generate consolidated human-readable and machine-readable portfolio views across delivery specs.

Create or update:

- `portfolio.yaml`
- `portfolio.md`

The portfolio view must identify:

- blocked items
- overdue items
- replanned items
- missing-owner items
- at-risk items
- multi-repo items

Keep every portfolio item traceable to source `ops.yaml`, supplied roadmap context, or supplied execution evidence. Do not invent delivery state.
