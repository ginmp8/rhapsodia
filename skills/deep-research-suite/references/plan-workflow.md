# Plan workflow

1. Identify the user's research topic, decisions, evaluation population, exclusions, evidence standard, time range, geography, relevant versions/jurisdictions and requested language.
2. Convert it into a bounded item list and complete field schema. Search current evidence only when identifying the population or important fields requires it; do not do item-level deep research unless requested.
3. Preserve existing user-provided item/field terminology and metadata; deduplicate names and semantic equivalents without conflating distinct objects.
4. Create a safe workspace with `outline.yaml` and `fields.yaml` using [the canonical contract](workspace-contract.md); defaults: conversation language, `batch_size: 4`, `items_per_agent: 1`, `output_dir: ./results`. IDs are stable; each field is required by default unless explicitly marked `required: false`.
5. Preserve research time/geo/scope notes in `research:`. Use `research.max_age_days` only when source freshness has a meaningful expiry; it is a cache age policy, not a guarantee of correctness.
6. Validate with `scripts/validate_workspace.py`. Summarize item/field counts and material assumptions, and ask only for unresolved choices that could invalidate the research. No unrequested full investigation.
