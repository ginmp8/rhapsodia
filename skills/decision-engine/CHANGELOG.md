# Changelog

## [2.2.0] - 2026-10-18

- Adds a source-backed selective-decision policy: separate epistemic uncertainty, capability/authority blocks, and independent escalation within existing `decision-engine/2` statuses.
- Adds risk-versus-coverage and false-abstention evaluation requirements only when a caller uses a selective decision policy with representative labeled examples; prohibits invented confidence thresholds and statistical guarantees.
- Makes calibration provenance, distribution-shift checks and missing-evidence limitations explicit; preserves all existing schema fields, statuses, safety controls, and selection behavior.
- Adds directly linked operational reference and independent planned scenarios, plus focused deterministic regression checks.
- Portable English-only core and existing v2 consumers remain unchanged; no hosted-model behavioral uplift is claimed.

## [2.1.0] - 2026-10-18

- Added a conditional quantitative-evidence screen for bounded decisions, covering aggregation/Simpson reversal, denominators, base rates, conditional direction, selection/collider risks, p-value misuse and material effect/uncertainty.
- Retained `decision-engine/2` without adding required fields, invented probabilities, thresholds, or unbounded statistical-analysis activation.
- Added a directly discoverable methodological reference and planned adversarial/metamorphic evaluation scenarios, plus deterministic guidance/portability regression checks.
- Refined control placement for numerical calculation vs. semantic decision and calibrated-probability limits.
- Repaired optional OpenAI adapter `policy.products` values to match its documented `CHAT|CODEX` vocabulary; host-independent core unchanged.
- Release repair: added required root `CHANGELOG.md` absent from the installed 2.0.2 baseline. History before 2.1.0 is not reconstructed here.

## Previous releases

- `2.0.2` is the verified installed baseline. Its historical changelog was not present in the supplied skill tree.
