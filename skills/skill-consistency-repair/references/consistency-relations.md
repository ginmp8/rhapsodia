# Consistency Relations

Use this reference when consistency spans more than one representation of the same contract.

## Relation model

Treat files as artifacts and explicit package evidence as typed directed relations. The deterministic inventory currently emits:

- `IMPORTS`: executable Python import relation detected statically;
- `REFERENCES`: local Markdown reference;
- `MENTIONS`: deterministic package-local textual reference.

A relation record contains source, target, relation type, detector, and evidence class. Mechanical edges are evidence of reachability/consumption, not semantic ownership by themselves.

Semantic review may add higher-level relations in a report or repair plan when directly evidenced, including `VALIDATES`, `GENERATES`, `CONFORMS_TO`, `EXEMPLIFIES`, `EVALUATES`, `PACKAGES`, `MIGRATES`, `OVERRIDES`, `DELEGATES_AUTHORITY_TO`, and `HANDOFF_TO`. Do not invent these from filenames alone.

## Trace coverage states

For every inspected dimension distinguish:

- `found`: one or more concrete evidence edges were found;
- `inspected-none`: the supported detector ran and found no edge;
- `not-inspected`: that evidence dimension was outside the executed inspection;
- `unsupported`: the current deterministic mechanism cannot inspect the evidence safely/reliably;
- `blocked`: inspection was required but could not proceed.

`inspected-none` is stronger than `not-inspected`, but neither proves that no external consumer exists. Removal still requires the deletion gate in `resource-integration.md`.

## Progressive-disclosure topology

Compute reachability from `SKILL.md` using detected local references. Report cycles and resources first reached beyond depth 1. Depth above 1 is advisory by default: a secondary asset can legitimately be deep. Escalate only when critical operational knowledge becomes undiscoverable, cyclic, contradictory, or inconsistent with the declared loading contract.

## Evidence boundary

A mechanically detected edge proves only that the detector observed a relation. Ownership, semantic equivalence, obsolescence, contradiction meaning, and safe deletion remain semantic decisions governed by authority and trace evidence.
