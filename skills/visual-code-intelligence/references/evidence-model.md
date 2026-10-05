# Evidence Model

## Purpose
Keep current behavior, requested intent, validation evidence, historical rationale, and inference distinct so a polished visual never outruns its sources.

## Evidence roles
- **current implementation:** source code, configuration, schema/migration, generated contract tied to the resolved revision;
- **validation:** tests, build/static checks, runtime observations when actually executed;
- **requested intent:** user-provided requirement/spec, issue/PR objective, accepted contract;
- **current documentation:** docs/ADRs that describe the current target and are not contradicted by code;
- **historical rationale:** commits, PR discussions, issues, old ADRs, agent traces/session records;
- **diff:** evidence of what changed between resolved endpoints, not by itself proof of runtime correctness.

## Question-specific precedence
For **current behavior**, prefer current implementation; use tests/runtime as corroboration and surface disagreement. Current docs are secondary; historical material cannot override current code.

For **requested intent**, prefer explicit current user/spec requirements, then the scoped issue/PR objective. Do not reverse-engineer intent from implementation when a requirement source exists.

For **rationale**, prefer explicit decision records/PR/issue evidence, then commit/trace evidence. If rationale comes only from architecture/code shape, label it `inferred`.

## Claim classes
- `observed`: directly supported by evidence appropriate to the claim.
- `historical`: directly supported by historical evidence and scoped to the time/event it describes.
- `inferred`: a bounded interpretation; cite its supporting evidence and state uncertainty when material.

Every material claim requires at least one evidence locator. Never fabricate exact lines/SHAs/URLs. When precise locators are unavailable, cite the strongest available file/symbol/artifact identity and say that line-level verification was unavailable.

## Conflict handling
Do not silently average conflicts. If tests/docs/history disagree with current code, report the disagreement and base current-behavior statements on the current implementation unless runtime evidence proves otherwise. If the conflict changes the conclusion, return an unresolved limitation rather than a confident visual.
