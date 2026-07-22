# Mago Getting Started

Use this page when the user has selected Mago but has not supplied an internal mode or does not know the next planning step. It is an onboarding projection, not a new lifecycle or source of truth.

## Route by intent

| User state | Mago action | Hand off instead when |
|---|---|---|
| "I have an idea or demand" | inspect the resolved Nomia handoff, then clarify technical planning inputs | requester, owner, business priority, due date, roadmap, or stakeholder facts are missing and must be authored by Nomia |
| "I need to understand the repository" | use `discovery` and produce bounded repository evidence | the user asks to edit code, run product tests, deploy, commit, or open a PR; route to Magia |
| "I need a plan" | select profile, lifecycle stage, and one internal mode; create only triggered artifacts | canonical identity or registry state is unresolved |
| "I need to change an existing spec" | refine canonical intent and generate a non-authoritative change delta | runtime evidence must be changed; Magia owns it |
| "I need to know what happens next" | render the planning compass and state the next evidence-backed action | the requested status is delivery governance; Nomia owns it |
| "I need tasks grouped for execution" | render dependency waves as a non-authoritative projection | Magia must still check file, contract, and runtime overlap before parallel execution |

## Minimum start sequence

1. Resolve `BOARD_ROOT`, `cycle_id`, `spec_id`, registry state, evidence source, and intended outcome.
2. Select the least costly safe profile using `references/profiles-and-lifecycle.md`.
3. Record unresolved facts as assumptions, questions, or blockers; use `references/clarification-prioritization.md` when several exist.
4. Select exactly one internal write mode.
5. Create only artifacts triggered by `references/artifact-decision-matrix.md`.
6. Run the narrowest validators that prove the current step.
7. Render `scripts/render_planning_compass.py` when a human-readable current-state view is useful.
8. Handoff only after canonical, traceability, mutation, and triggered gates pass.

## Profile quickstart

### Quick

Use for one bounded, reversible, well-understood change with known validation and no contract, migration, auth/security/privacy/compliance, multi-repository, material architecture, or irreversible-data trigger.

Minimum package: `manifest.yaml`, `prd.md`, `tasks.md`, and `validation.md`.

### Standard

Use for normal repository changes requiring explicit requirements, design reasoning, dependencies, compatibility expectations, tasks, notes, and validation.

Minimum package: quick set plus `notes.md` and only triggered technical artifacts.

### Governed

Use for regulated, security-sensitive, financial, privacy, migration, public-contract, operationally risky, cross-service, or multi-repository work. Every trigger family must be satisfied or explicitly marked not applicable with evidence.

## Typical entry prompts

- `Use Mago to inspect this repository and identify planning candidates without editing code.`
- `Use Mago to turn this resolved Nomia handoff into the smallest safe quick plan.`
- `Use Mago to refine this existing spec and show added, modified, removed, and preserved behavior.`
- `Use Mago to show the current planning stage, missing artifacts, pending gates, and next action.`
- `Use Mago to project dependency-safe execution waves for Magia without executing tasks.`

## What Mago never does

Mago does not invent governance facts, implement code, execute product tests, fabricate runtime evidence, certify deployment, accept business risk, or edit generated projections as if they were canonical artifacts.
