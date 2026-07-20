# Roadmap to Mago Contract

Use only for nomia governance handoff from roadmap to Mago. nomia prepares handoff facts; Mago owns identity registration, the planning package, and technical decomposition.

## Handoff Preconditions

Before `roadmap-to-specs`, collect or preserve unknowns for: feature key/title, problem, desired outcome, requester/stakeholders, owner/decision maker, priority/bucket, risk, target cycle/date, dependencies, acceptance or handoff notes, and links/evidence.

A handoff does not require nomia to invent a spec identity. Use `candidate_spec_id: null` until a canonical `spec_id` is supplied or evidenced by a Mago registry record. If a candidate id is present, it must use `spec-YYYY-MM-DD-feature-key--ULID` and its embedded feature key must match `feature_key`.

## nomia May Do

- Mark `feature-map.yaml` handoff status as `ready`, `draft`, `blocked`, `parked`, `accepted`, or `unknown` based on evidence.
- Mark a feature `ready_for_spec: true` before registration when governance evidence is sufficient.
- Link roadmap items to an existing canonical spec after Mago registration.
- Record governance rationale, open questions, blockers, and handoff notes.
- Validate that handoff facts are sufficient for Mago to start.

## nomia Must Not Do

Do not create `cycle.yaml`, registry records, Mago spec packages, generated catalog/queue projections, PRDs, technical designs, tasks, validation plans, ADRs, execution-handoff plans, architecture decisions, or engineering acceptance criteria. Do not infer technical scope from roadmap intent and do not mint `cycle_id` or `spec_id` values.

## Downstream Feedback

Mago may return a registered `spec_id`, planning blockers, missing evidence, or technical questions. Magia may return execution evidence, technical gap notes, validation gaps, and delivery-impact signals. nomia may record these as governance blockers, delivery risks, handoff facts, or reporting evidence, but must not edit the underlying Mago/Magia technical artifacts or treat returned evidence as nomia technical validation.

## Validation

Run `scripts/validate_contracts.py` and `scripts/validate_roadmap.py` when handoff artifacts change. Missing owner, outcome, evidence, or an assigned candidate spec may warn or block according to validator output; never invent them. A feature may be handoff-ready with `candidate_spec_id: null` when registration is intentionally delegated to Mago.
