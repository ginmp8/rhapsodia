# Visual Language

## Purpose
Make diagram choice stable, semantically meaningful, and compact.

## Selection order
1. Explicit user-requested visual type, if it can represent the evidence without distortion.
2. Mode-specific mandatory view: `change-map` for a change review with multiple meaningful lenses; `timeline` for archaeology where several historical events are essential.
3. Dominant relationship signal using this stable tie-break order:
   1. temporal interaction -> `sequence`
   2. branching/retry/control decision -> `flowchart`
   3. lifecycle/state transition -> `state`
   4. persistent data relationship/read-write shape -> `er`
   5. component/dependency structure -> `architecture`
   6. historical evolution -> `timeline`
   7. semantic file responsibilities -> `change-map`
4. If no relationship is dominant, use `architecture` only for `system-explanation`; otherwise use no diagram.

The tie-break order is not a claim that one diagram is globally better. It exists only to make equal-signal choices reproducible. If choosing one would hide a material second dimension, use at most one secondary visual with a different role.

## Composition rules
- Keep one node/entity per meaningful concept, not per file by default.
- Name nodes with domain/responsibility language; attach file/symbol evidence separately.
- Preserve direction consistently: left-to-right for dependency/data movement when natural; top-to-bottom for staged processes.
- Include unchanged bridge components when omitting them would make a changed path misleading.
- Represent retries/loops explicitly; do not flatten them into a straight line.
- Show failure/alternate paths only when material to the user's question.
- Never add components, data stores, calls, or states merely to make the diagram look complete.

## Density
Default to one primary visual. Add a second only for a different reader question, such as `change-map + sequence` or `architecture + ER`. Prefer splitting a dense visual over shrinking labels into unreadability.
