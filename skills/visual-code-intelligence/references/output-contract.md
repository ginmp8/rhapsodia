# Output Contract

## Purpose
Keep outputs consistent across hosts while adapting depth to the reader and capability surface.

## Audience depth
- `overview`: answer in roughly 30 seconds of reading; one summary, one visual, key impact, minimal evidence.
- `technical`: default for engineering review; summary, visual(s), implementation walkthrough, risks/invariants, evidence.
- `deep-dive`: add failure paths, compatibility/data concerns, historical decisions, uncertainty, and denser evidence only when requested or materially necessary.

## Portable result shape
Use only sections that add value, in this preferred order:
1. Result / What & Why
2. Requirements (only when known)
3. Visual explanation
4. Implementation / behavior walkthrough
5. Risks, invariants, or trade-offs
6. Evidence and uncertainty

For `change-review`, place the semantic change map before the design visual when both exist.

## Output profiles
- `portable`: Markdown + Mermaid and inline evidence locators. This is the default source of truth.
- `rich`: standalone HTML or host-native visual artifact only when explicitly requested and supported. It must not introduce semantics absent from the portable plan.
- `text-fallback`: compact trees/tables/ordered steps preserving the same claims when Mermaid cannot render.

## Quality bar
- State the conclusion before implementation detail.
- Prefer domain language over filenames in visual nodes.
- Keep evidence close to claims.
- Avoid repeating the diagram in prose; prose explains implications and nuance.
- Do not bury missing evidence or inferred relationships in footnotes.
