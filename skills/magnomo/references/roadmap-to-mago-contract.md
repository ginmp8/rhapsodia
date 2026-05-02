# Roadmap to Mago Contract

Use only for Magnomo governance handoff from roadmap to Mago. Magnomo prepares handoff facts; Mago owns the planning package and technical decomposition.

## Handoff Preconditions

Before `roadmap-to-specs`, collect or preserve unknowns for: feature key/title, problem, desired outcome, requester/stakeholders, owner/decision maker, priority/bucket, risk, target cycle/date, candidate spec ids, dependencies, acceptance or handoff notes, and links/evidence.

## Magnomo May Do

- Mark `feature-map.yaml` handoff status as `ready_for_mago`, `handed_off`, `blocked`, or `unknown` based on evidence.
- Link roadmap items to candidate specs.
- Record governance rationale, open questions, blockers, and handoff notes.
- Validate that handoff facts are sufficient for Mago to start.

## Magnomo Must Not Do

Do not create Mago spec packages, write PRDs, technical designs, tasks, validation plans, ADRs, implementation plans, architecture decisions, or engineering acceptance criteria. Do not infer technical scope from roadmap intent.

## Validation

Run `scripts/validate_contracts.py` and `scripts/validate_roadmap.py` when handoff artifacts change. Missing owner, candidate spec, outcome, or evidence is a warning/blocker according to validator output; never invent it.
