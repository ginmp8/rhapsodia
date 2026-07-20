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

## Deterministic validation

Render a temporary, non-authoritative matrix outside `BOARD_ROOT`:

```bash
python scripts/render_traceability.py <package-path> --output <external-dir>/traceability.json
python scripts/validate_traceability.py <external-dir>/traceability.json --profile governed
```

The renderer reads canonical artifacts; the JSON is a disposable validation projection and must never replace PRD, design, tasks, validation, manifest, registry, or source repository truth. Delete or exclude it after validation.

Validation fails for duplicate identifiers, malformed link fields, references to unknown identifiers, missing task/validation coverage, and incomplete governed chains. A passing static traceability check does not prove implementation or runtime acceptance.
