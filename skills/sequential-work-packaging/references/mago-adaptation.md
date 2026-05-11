# MAGO adaptation rules

Use this file when the prompt explicitly references `mago-define`, `mago-refine`, or `mago-decompose`.

## Goal
Preserve the planning intent of the MAGO agents while forcing all outputs and internal decisions to follow the canonical sequential work packaging specification.

## Mapping
- `.MAGO-DEFINE`
  - order requests -> `order` mode
  - per-spec package creation or revision -> `define` mode
- `.MAGO-REFINE` -> `refine` mode
- `.MAGO-DECOMPOSE` -> `decompose` mode

## Mandatory normalization
Do not preserve these as authoritative outputs:
- `docs/current`
- `MANIFESTO.yaml`
- `PRD.md`
- `TASKS.md`
- `VALIDATION.md`
- `NOTES.md`
- `FEATURE_ORDER.yaml`

Normalize them to:
- `<cycle_version>/spec-catalog.yaml`
- `<cycle_version>/specs/<spec_id>/manifest.yaml`
- `<cycle_version>/specs/<spec_id>/prd.md`
- `<cycle_version>/specs/<spec_id>/tasks.md`
- `<cycle_version>/specs/<spec_id>/validation.md`
- `<cycle_version>/specs/<spec_id>/notes.md`

## Compatibility interpretation
When adapting MAGO prompts:
- preserve planning-only behavior unless implementation is explicitly requested
- preserve minimal-change refinement behavior
- preserve decomposition behavior for broad remaining work
- preserve final review discipline
- preserve reasoning guidance and sparse specialist metadata
- reject legacy casing and legacy directory layout as canonical

## Output expectation
The result must read as if the MAGO mode had always been designed for the canonical spec model.
