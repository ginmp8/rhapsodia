# Roadmap to Mago Contract

Use only for nomia governance handoff from roadmap to Mago. nomia prepares handoff facts; Mago owns the planning package and technical decomposition.

## Handoff Preconditions

Before `roadmap-to-specs`, collect or preserve unknowns for: feature key/title, problem, desired outcome, requester/stakeholders, owner/decision maker, priority/bucket, risk, target cycle/date, candidate spec ids, dependencies, acceptance or handoff notes, and links/evidence.

## nomia May Do

- Mark `feature-map.yaml` handoff status as `ready_for_mago`, `handed_off`, `blocked`, or `unknown` based on evidence.
- Link roadmap items to candidate specs.
- Record governance rationale, open questions, blockers, and handoff notes.
- Validate that handoff facts are sufficient for Mago to start.

## nomia Must Not Do

Do not create Mago spec packages, write PRDs, technical designs, tasks, validation plans, ADRs, execution-handoff plans, architecture decisions, or engineering acceptance criteria. Do not infer technical scope from roadmap intent.

## Downstream Feedback

Mago may return planning blockers, missing evidence, or technical questions. Magia may return execution evidence, technical gap notes, validation gaps, and delivery-impact signals. nomia may record these as governance blockers, delivery risks, handoff facts, or reporting evidence, but must not edit the underlying Mago/Magia technical artifacts or treat returned evidence as nomia technical validation.

## Validation

Run `scripts/validate_contracts.py` and `scripts/validate_roadmap.py` when handoff artifacts change. Missing owner, candidate spec, outcome, or evidence is a warning/blocker according to validator output; never invent it.
