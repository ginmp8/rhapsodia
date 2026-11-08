# Maintainability smell baseline

## Purpose

Use only for **advisory** observations in the Standards review. The repository's documented conventions override these heuristics, and deterministic lint/test checks take priority. A smell does not itself prove a defect.

## Heuristics

- **Mysterious Name:** a name conceals the domain intent; choose an explanatory name.
- **Duplicated Code:** the same logic shape recurs; consolidate only where abstraction improves locality.
- **Feature Envy:** logic over-reads another module's data; examine moving it to the owner.
- **Data Clumps:** fields repeatedly travel together; consider a domain-specific value type.
- **Primitive Obsession:** primitives hide a stable domain concept; consider a dedicated type.
- **Repeated Switches:** distributed case cascades on the same discriminant; centralize behavior safely.
- **Shotgun Surgery:** one change touches many unrelated owners; identify the missing seam.
- **Divergent Change:** one module responds to unrelated kinds of modification; narrow responsibilities.
- **Speculative Generality:** abstraction is introduced for no evidenced requirement; delete or simplify.
- **Message Chains:** callers know too much navigation detail; hide traversal behind an owning API.
- **Middle Man:** near-empty wrapper passes everything through; reassess depth before removing.
- **Refused Bequest:** subtype ignores its inheritance contract; consider composition.

For each observation cite the diff hunk, state why the pattern matters, and identify a counterexample or reason it may be acceptable. Never present this list as a coding standard of the target repository.
