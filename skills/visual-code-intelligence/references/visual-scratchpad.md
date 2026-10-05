# Visual Scratchpad

## Purpose
Provide a quick visual explanation when the user wants to see a code concept, flow, call path, or data relationship without performing a full change review.

## Rules
1. Start from the user's exact question and inspect the minimum source needed to answer it.
2. Produce one short framing paragraph plus the smallest useful visual.
3. Prefer one visual; add code snippets only for types/interfaces/invariants that the diagram cannot express clearly.
4. If the explanation spans several files, keep the visual at component/behavior level and use evidence locators for implementation detail.
5. Do not create sections/status scaffolding unless the user asks for a structured document.
6. If a sentence or short code excerpt is clearer than a diagram, answer directly and omit the visual.

## Typical choices
- call sequence or async handoff -> sequence;
- decision/retry/branch -> flowchart;
- lifecycle -> state;
- data relationship -> ER/data;
- dependencies -> architecture/component;
- historical progression -> timeline.
