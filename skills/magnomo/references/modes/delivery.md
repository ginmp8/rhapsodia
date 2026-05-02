# Delivery Modes

Use for `delivery-intake`, `delivery-triage`, `delivery-status`, `delivery-replan`, and `delivery-portfolio`.

## Canonical Rules

`BOARD_ROOT` is required for repository-facing artifacts. Prompt `BOARD_ROOT` wins after validation; otherwise derive it from `references/canonical-paths.md`. Spec-scoped artifacts require `BOARD_ROOT/specs/<spec_id>/`. Board-scoped portfolio artifacts stay directly under `BOARD_ROOT`.

Create/refresh template-backed artifacts with local scripts; validate with `scripts/validate_artifact.py` or narrower validators. Do not copy template text manually when a script can write or validate.

## delivery-intake / delivery-triage

Purpose: register or triage a demand into governance records.

Inputs: requester, problem/request, source, desired outcome, target date, owner, stakeholders, priority, risk, links when supplied. Unknowns remain explicit.

Outputs: `ops.yaml` and, when useful, `status.md` or `stakeholder-brief.md` in the selected spec package. Use `scripts/write_ops_scaffold.py` or `scripts/write_artifact_scaffold.py`; populate supported lists with `scripts/update_template_lists.py`; validate touched artifacts and board paths.

## delivery-status

Purpose: update human delivery status without claiming technical validation or deployment.

Inputs: current state evidence, notes, risks, blockers, next steps, validation/release/deployment evidence when supplied. Outputs: `status.md` and relevant `ops.yaml.status` updates. Preserve missing validation/release/deployment as unknown.

## delivery-replan

Purpose: record material changes to target date, sprint, scope, owner, commitment, priority, or risk.

Outputs: append `replanning.md` entry and mirror structured `ops.yaml.replanning` change. Include date, changed fields, from, to, reason, impact, and decision maker when known. Do not use for routine status updates.

## delivery-portfolio

Purpose: board-level delivery summary across specs.

Outputs: `portfolio.yaml` and `portfolio.md` under `BOARD_ROOT`. Derive from supplied `ops.yaml` files and evidence. Use `scripts/update_template_lists.py` for mechanical list population. Validate with `scripts/validate_portfolio.py` or `scripts/validate_artifact.py`, then board paths.

## Boundaries

Do not store branches, PRs, commits, checks, review state, deployments, or last commit age as maintained Magnomo status. Do not create Mago tasks, execution-handoff plans, technical designs, code changes, tests, or execution evidence. Use such material only as linked evidence when supplied.
