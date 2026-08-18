# Requirements and Traceability Contract

Use this contract for `standard` and `governed` planning and whenever behavior, compatibility, security, migration, or acceptance must be audited. `quick` may use the same syntax with fewer records, but it must still link every changed requirement to at least one task and validation.

## Normative requirement convention

Use stable uppercase identifiers:

- requirement: `REQ-001`
- acceptance behavior: `AC-001`
- planned technical decision: `DECISION-001`
- task: existing canonical `task001`
- validation: `VAL-001`

Identifiers are immutable within a spec version. Do not recycle removed identifiers. Preserve superseded identifiers in change history or the change-delta projection.

Write normative requirements with an EARS-style condition and response when the pattern fits:

- ubiquitous: `The <system> MUST <response>.`
- event-driven: `WHEN <trigger>, the <system> MUST <response>.`
- state-driven: `WHILE <state>, the <system> MUST <response>.`
- unwanted behavior: `IF <condition>, THEN the <system> MUST <response>.`
- optional feature: `WHERE <feature is enabled>, the <system> MUST <response>.`
- complex: combine `WHILE`, `WHEN`, and `IF/THEN` only when each clause is necessary and observable.

Use BCP 14 keywords only with their normative meanings and only in uppercase: `MUST`, `MUST NOT`, `REQUIRED`, `SHALL`, `SHALL NOT`, `SHOULD`, `SHOULD NOT`, `RECOMMENDED`, `NOT RECOMMENDED`, `MAY`, and `OPTIONAL`. Avoid normative keywords in descriptive prose when no obligation is intended.

## Observable acceptance behavior

Use Gherkin scenarios when an acceptance condition is observable through user, API, event, data, security, or operational behavior:

```gherkin
Scenario: AC-001 <short behavior>
  Given <evidenced precondition>
  When <observable trigger>
  Then <observable outcome>
  And <additional outcome only when necessary>
```

Gherkin is acceptance evidence design, not runtime proof. Do not mark a scenario passed unless Magia or another authorized execution source supplies current evidence.

## Machine-checkable links

The governed chain is:

```text
REQ -> AC -> DECISION -> TASK -> VALIDATION
```

Markdown records use these parsable forms:

```text
### REQ-001 - <title>
### AC-001 - <title>
- Requirements: REQ-001
### DECISION-001 - <title>
- Requirements: REQ-001
- [ ] task001: <title>
  - Requirements: REQ-001
  - Acceptance: AC-001
  - Decisions: DECISION-001
  - Validations: VAL-001
### VAL-001 - <title>
- Requirements: REQ-001
- Acceptance: AC-001
- Tasks: task001
```

Use comma-separated IDs or `none` only where the selected profile permits omission. `governed` forbids `none` for the required chain. A decision may cover several requirements, but every material governed requirement must have at least one linked planned decision or an explicit recorded rationale that no design decision is needed; the validator treats that rationale as a decision record, not as a missing link.


## Governed plan-quality fields

Before governed handoff, run `scripts/validate_plan_quality.py <package>`. Each functional requirement records `Evidence basis`, `Failure/recovery behavior`, and linked acceptance `Verification`. Acceptance criteria classify an observable path (`normal`, `boundary`, `error`, `abuse`, `recovery`, or `operational`); governed coverage includes a normal path and at least one non-happy path. Material nonfunctional requirements use stable `NFR` records with a metric, threshold, and `VAL` link, or the NFR section states an evidence-backed non-applicability rationale.

When technical design is triggered, record at least two explicit `OPTION` records with benefits, costs, failure modes, and operational impact, then link the selected option from a `DECISION`. Validation records name environment, command or procedure, expected result, and failure disposition. These fields improve auditability and execution readiness but remain planning evidence, not runtime proof.

## Deterministic validation

Render a temporary, non-authoritative matrix outside `BOARD_ROOT`:

```bash
python scripts/render_traceability.py <package-path> --output <external-dir>/traceability.json
python scripts/validate_traceability.py <external-dir>/traceability.json --profile governed
```

The renderer reads canonical artifacts; the JSON is a disposable validation projection and must never replace PRD, design, tasks, validation, manifest, registry, or source repository truth. Delete or exclude it after validation.

Validation fails for duplicate identifiers, malformed link fields, references to unknown identifiers, missing task/validation coverage, and incomplete governed chains. A passing static traceability check does not prove implementation or runtime acceptance.

## Governed quality contract v2

New governed packages use `quality_contract: 2` and run `scripts/validate_plan_quality.py <package> --require-v2`. Every requirement records `Criticality` and `Criticality basis`; acceptance coverage is calibrated per requirement rather than only across the package. High and critical requirements require linked recovery coverage, critical requirements require explicit error coverage, and critical security requirements require abuse-path coverage. Every acceptance criterion must be covered by a validation record. V2 validation records also declare evidence capture and residual-risk disposition, and decisions declare rollback or reversibility. Legacy v1 packages remain readable through the default validator and must migrate through `refine` or `adapt` before a new governed handoff.
