# Workspace contract (v2, with v1 compatibility)

Use these exact shapes; scripts intentionally parse a documented dependency-free YAML subset, not arbitrary YAML. Preserve existing IDs, category names, and result fields when updating a workspace.

## Outline

```yaml
topic: Example topic
output_language: pt-BR
research:
  time_range: since 2025
  geography: global
  scope_notes: Official versions and independent comparisons
  max_age_days: 30
items:
  - name: Item A
    id: item_a
    category: Framework
    description: Representative research object
execution:
  batch_size: 4
  items_per_agent: 1
  output_dir: ./results
```

`topic` and one or more `items[].name` are mandatory. `id` is optional but recommended; immutable when possible, unique and filename-safe. If absent, `item_slug()` derives a collision-resistant name+hash, while legacy result files remain matchable by top-level `name`. `output_dir` resolves from the outline directory; external absolute paths require explicit user authorization. Preserve original `research` qualifiers on resume. `batch_size` and `items_per_agent` do not require worker/agent infrastructure. Avoid YAML anchors, multiline constructs, nested objects, implicit type magic and tabs: unsupported syntax is rejected.

## Fields

```yaml
fields:
  Basic Info:
    - name: name
      description: Canonical item name
      detail_level: brief
    - name: release_date
      description: Verifiable release date
      detail_level: moderate
      required: false
  Technical Features:
    - name: architecture
      description: Architecture and sources
      detail_level: detailed
uncertain: []
```

Each field has a unique `name`; categories contain lists. Supported detail levels: `brief`, `moderate`, `detailed`. A field is **required by default**, even when another field explicitly says `required: false`. Specify `required: false` for each optional field. Changing a field's meaning, type or required status invalidates impacted results and may affect old clients. This is a v2 tightening; compare migrations before reuse.

## Item result JSON

```json
{
  "name": "Item A",
  "release_date": "[uncertain]",
  "technical_features": {"architecture": "Layered"},
  "uncertain": ["release_date"],
  "_sources": [{"id":"S-001", "title":"Official documentation", "url":"https://example.com/docs", "accessed":"2026-10-14"}],
  "_claims": [{"id":"C-001", "text":"The architecture is layered", "status":"supported", "source_ids":["S-001"], "locator":"Architecture section"}]
}
```

Fields may be top-level or nested by category; `uncertain` records fields not settled. `_sources` references must have safe HTTP(S) URLs; `id` is recommended, required for cited `_claims`. `_claims` is optional for legacy files but recommended for consequential claims; supported statuses: `supported`, `contradicted`, `uncertain`, `not_found`. Source linkage is a structural statement only, not independently verified truth. `_run` is a stamp added by `check_resume.py --stamp` **after** evidence review; unsigned historical files can be reported after revalidation but cannot be auto-skipped by the safe resume protocol. Other `_` keys are internal and not rendered as research fields.

## Validation semantics

`validate_result.py` outputs `structural_valid`, `research_ready`, `valid` (strict research readiness), missing/empty/uncertain required fields, source and claim errors, and a caution that source linking is not factual verification. Unknown required values are preserved but not called complete. Use `--allow-incomplete` only for explicit partial/structural workflows. `generate_report.py --allow-partial` never silently includes invalid/incomplete JSON.
