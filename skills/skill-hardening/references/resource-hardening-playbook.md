# Resource Hardening Playbook

## Principle: necessity before presence

Optional resource directories are not maturity points. Add a resource only when evidence shows it reduces variance, removes duplication, creates useful validation, or makes a recurring artifact safer to produce. A correct `SKILL.md`-only package can be better than a larger package with ornamental machinery.

## Resource choices

- `references/`: long, conditional, domain, mode-specific, or rubric content that would otherwise overload the control plane.
- `scripts/`: deterministic mechanics/checks that are repetitive or fragile. Do not add a script when instructions plus available tools already perform the task reliably.
- `assets/templates/`: reusable stable artifact skeletons that are actually copied/filled/validated.
- `evals/` and `examples/`: scenario/calibration assets when behavioral coverage is needed. Definitions are not measured evidence until executed.
- `agents/openai.yaml`: optional OpenAI adapter/UI metadata; never a portable-core correctness requirement.

## Hardening map

For each proposed resource record: evidence/hypothesis, requirement, file, expected effect, validation gate, integration/loading condition, rollback, and accept/reject decision. A resource without reverse justification is probable gold plating.

## Existing-resource quality

Present resources must still be sound:

- scripts: deterministic inputs/outputs where objective, nonzero failure exit, readable diagnostics, no hidden network dependency unless declared, representative execution evidence, no secrets in args/logs/fixtures;
- references: narrow purpose, explicit loading condition, decision-useful preview when long, direct discoverability from `SKILL.md` for required knowledge, minimal duplication, no knowledge-dump drift;
- templates: stable artifact, workflow-fillable placeholders, usage rule, validation when strict;
- scenarios: concrete acceptance criteria and frozen execution evidence for measured claims.

## Asset triage

Classify before deletion: operational template, script input/output, explanatory reference, example/calibration, host adapter/visual asset, unused scaffold. Integrate useful resources first; remove only duplicated/obsolete/scaffold material with evidence.

## Common improvements

Prefer, only when justified: compact control plane + progressive references; explicit mode/output/stop contracts; deterministic validator for fragile mechanics; claim-sensitive scenarios; trust intake for untrusted packages; portable host profiles; freeze/rollback/package receipts. Do not manufacture these layers simply to increase a score.
