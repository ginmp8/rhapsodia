# Ingestion adapters

## At a Glance
- **Purpose:** Define how external parsers and model-assisted extraction may feed GraphPatch safely.
- **Load when:** Adding a new source type, programming-language parser, repository scanner, or LLM-assisted semantic relation.
- **Decision impact:** Determines provenance labels and stops approximate parser/model output from being misrepresented as exact structure.

## Adapter rule
An adapter emits `graph-patch-v1`; it does not write SQLite directly. Keep parsing independent of persistence so the same patch can be validated, reviewed, replayed, and tested.

## Preferred evidence order
1. Structured source/API/schema facts -> `EXTRACTED`.
2. Deterministic computations over accepted facts -> `DERIVED`.
3. Model/heuristic semantic interpretation -> `INFERRED`.
4. User-authored assertion -> `MANUAL`.

For code intelligence, prefer AST/compiler APIs over regex when symbol correctness matters. Conservative regex/token adapters may emit only relations they can prove from syntax and must report unsupported/unresolved cases separately. Never infer a missing import/call edge because it "looks likely".

## Coverage
Adapters should report what they processed, skipped, or could not resolve. Silent partial extraction creates a plausible but misleading graph and is worse than an explicit coverage gap.
