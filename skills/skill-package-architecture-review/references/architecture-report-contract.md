# Architecture Review Report Contract

**Schema version:** 2.0.0  
**Rubric version:** 3.0.0

Use this contract for durable `review-report` output and whenever reports from repeated reviews must be comparable. `scripts/validate_architecture_report.py` also accepts legacy schema `1.0.0` with rubric `2.0.0` so existing reports remain readable; new reports should use this contract.

## Canonical logical fields

A schema 2.0.0 report contains:

1. `schema_version`
2. `rubric_version`
3. `target`
   - `name`
   - `package_identity_sha256`
4. `mode`
5. `architecture_scope`: `single_skill | skill_family | plugin_package`
6. `evidence_snapshot`
   - `identity`
   - `source`
7. `observations[]`
   - `id`
   - `kind`: `mechanical | declared-contract | behavioral | supplied | derived`
   - `claim`
   - `evidence[]`
8. `judgments[]`
   - `id`
   - `claim`
   - `evidence_ids[]` referencing observations
   - `confidence`: `low | medium | high`
9. `activation_evidence`
   - `status`: `distinct | overlap | partial | unknown`
   - `signals[]`
   - `catalog_scope`
10. `context_topology`
    - `skill_md_line_count`
    - `direct_declared_resource_count`
    - `reference_chain_max_depth`
    - `nested_reference_edge_count`
11. `quality_scenarios[]`
    - `id`
    - `stimulus`
    - `affected_surfaces[]`
    - `evidence_ids[]`
12. `sensitivity_points[]`
    - `id`
    - `claim`
    - `evidence_ids[]`
13. `tradeoff_points[]`
    - `id`
    - `claim`
    - `evidence_ids[]`
14. `evolution_evidence`
    - `history_status`: `observed | partial | not-inspected | unknown`
    - `change_coupling[]`
    - `change_radius_notes[]`
15. `trust_boundary_map`
    - `status`: `observed | partial | unknown`
    - `executable_resources[]`
    - `network_requirements[]`
    - `filesystem_write_requirements[]`
    - `external_tool_requirements[]`
    - `security_handoff_required`
16. `evidence_gaps[]`
17. `decision`
    - `choice`: `keep_unified | split | extract_mode | create_router | merge_resources | no_change`
    - `evidence_ids[]`
    - `alternatives_considered[]`
    - `tie_breaker_used`
18. `recommendations[]`
19. `measured`
    - `commands[]`
    - `behavioral_scenarios_executed`
20. `residual_risks[]`

The Markdown template renders the same logical areas for humans. The JSON form is the canonical mechanically validated companion when machine-readable output is requested.

## Architecture-scope rules

`architecture_scope` describes the evidence boundary needed for the question; it does not replace the focal target identity or add a seventh architecture decision.

- `single_skill`: package-local evidence is sufficient.
- `skill_family`: adjacent skills materially affect activation/routing/ownership. Missing catalog evidence must be listed in `evidence_gaps`.
- `plugin_package`: a containing plugin/package capability boundary matters. Keep conclusions about unseen package-level structure bounded and hand off when necessary.

## Activation evidence rules

`activation_evidence.status` is not a confidence score:

- `distinct`: relevant supplied/observed evidence supports stable separation;
- `overlap`: credible evidence supports recurring ambiguous intent/competing activation surfaces;
- `partial`: only part of the relevant catalog/routing surface was inspected;
- `unknown`: material adjacent evidence was unavailable.

Do not call activation behavior measured unless the relevant cases were executed.

## Context-topology rules

Copy mechanically measured values from the inventory when available. If Python/inventory execution is unavailable, use prose output and mark the topology `not-measured`; do not fabricate zeros merely to satisfy JSON.

Topology values are facts, not pass/fail thresholds. A depth or count does not independently justify a structural decision.

## Scenario, sensitivity, and tradeoff rules

Use `quality_scenarios` only for scenarios material to the decision. Scenario/sensitivity/tradeoff evidence IDs must resolve to recorded observations/judgments where required by the validator.

Do not create empty ceremonial scenarios to mimic ATAM. Empty arrays are valid when the review does not need this evidence; state the reason in `evidence_gaps` or residual risk when material.

## Evolution evidence rules

`change_coupling` is optional. When populated, each record should identify its repository/history evidence and qualifiers. Historical co-change is corroborating evidence only and cannot independently establish split, merge, extraction, routing, deletion, or ownership transfer.

`history_status: not-inspected` is valid and must not be converted into a negative score.

## Trust-boundary rules

Map only observed/declared executable, network, filesystem-write, external-tool, and permission/provenance surfaces. `security_handoff_required: true` means the architectural decision depends on a detailed security question that this skill does not own.

A clean topology is not a security certification.

## Identity rules

- `target.package_identity_sha256` identifies the exact reviewed focal-package bytes.
- `evidence_snapshot.identity` identifies the evidence bundle/report input used for the review.
- Do not compare two reports as "same package" when target identities differ.
- If exact target identity could not be measured, do not emit a fabricated hash; use prose output and mark identity `not-measured` instead of claiming schema-valid JSON.
- For `skill_family` or `plugin_package`, identify surrounding evidence through `evidence_snapshot`/observations; do not reuse the focal package hash as proof of an unseen collection identity.

## Observation and judgment rules

- Observations state facts/evidence without architectural conclusion.
- Judgments reference observation IDs.
- Decisions reference observations/judgments that justify them.
- Scenario/sensitivity/tradeoff records reference supporting evidence IDs.
- Recommendations reference evidence and specify validation gates.

## Measured claims

`behavioral_scenarios_executed: true` is allowed only when scenarios were actually run in the current evidence set. Presence of `evals/architecture-review-scenarios.json` alone means planned coverage, not measured behavior.

## Validation and final freeze

Validate JSON reports with:

```text
<PYTHON> scripts/validate_architecture_report.py <REPORT.json>
```

A passing schema does not prove the architectural judgment is correct; it proves the report is structurally traceable and identity-bound.

After the final applicable validator passes, freeze the exact report bytes/identity used for delivery or comparison. Any content edit afterward invalidates affected validation and requires revalidation.
