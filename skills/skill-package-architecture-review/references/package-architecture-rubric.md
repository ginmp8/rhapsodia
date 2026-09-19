# Package Architecture Rubric

**Rubric version:** 2.0.0

Use this rubric for architectural judgment. It is a decision contract, not a substitute for context.

## Evidence discipline

Separate:

- mechanical observation;
- declared package contract;
- executed behavioral evidence;
- supplied external evidence;
- derived evidence;
- reviewer judgment.

Every material judgment must reference evidence. A static rubric score is structural judgment, not measured behavioral quality.

## Dimensions

Score 0-4 only when the user asks for scoring. Otherwise apply qualitatively.

| Dimension | 0 | 2 | 4 |
|---|---|---|---|
| Control-plane clarity | unusable or contradictory | basic workflow, weak routing | compact modes/routing/loading/stop/output contract |
| Cohesion | unrelated domains/responsibilities | related but ambiguous overlap | one coherent domain/workflow family |
| Resource integration | misleading/unowned resources | mixed integration | declared, consumed, validated, or intentionally asset-only resources |
| Progressive loading | knowledge dump/hidden dependencies | partial conditional loading | branch-specific resources loaded only when needed |
| Boundary governance | unclear authority | partial ownership/handoffs | explicit authority, stop conditions, adjacent-skill handoffs |
| Validation architecture | claims without evidence | basic validators/planned scenarios | independent deterministic gates and executed evidence where claimed |
| Package hygiene | stale/generated/scaffold noise | mostly clean | packageable, intentional tree |
| Maintainability | changes require broad coupled edits | manageable hotspots | modular evolution without domain drift |

## Primary architecture decision enum

Choose exactly one when a primary decision is requested:

- `keep_unified`
- `split`
- `extract_mode`
- `create_router`
- `merge_resources`
- `no_change`

A handoff is a follow-up action, not an architecture decision.

## Minimum evidence by decision

### `keep_unified`

Eligible when evidence supports one coherent domain/workflow family and no hard separation signal exists. Prefer when:

- one activation surface can route the package without persistent ambiguity;
- one authority/owner model is coherent;
- mode evidence/validation lifecycles are compatible;
- progressive loading contains context cost;
- resources can remain integrated without duplicated ownership.

Do not require small package size.

### `split`

Eligible only with either:

- one hard incompatibility: conflicting authority/safety/evidence policies that cannot safely coexist; **or**
- at least two independent separation signals from different categories below.

Separation signals:

1. distinct domains/activation surfaces with recurring collisions;
2. conflicting ownership or authority models;
3. incompatible evidence/validation policies;
4. independent release/maintenance lifecycle with cross-cutting change burden;
5. repeated routing branches that effectively hide separate products/workflows;
6. progressive-loading failure that cannot be repaired by routing/reference extraction.

File count, line count, number of references, or stylistic preference are never separation signals by themselves.

### `extract_mode`

Eligible when both are true:

1. the mode has meaningfully distinct trigger/user intent; and
2. at least one independent lifecycle signal exists: dedicated resources, validators/evals, owner/authority, release cadence, or separate user expectation.

Prefer extraction over full split when the rest of the package remains cohesive and the mode is the localized source of independence.

### `create_router`

Eligible when all are true:

- two or more destinations are already coherent or should remain separately owned;
- stable dispatch evidence exists: explicit user intent, artifact type, domain, mode, or other deterministic key;
- one shared entry point materially reduces activation ambiguity or user burden;
- router authority can remain narrow: dispatch, not duplicate subskill semantics.

Do not create a router only because a package has many modes.

### `merge_resources`

Eligible when resources share the same decision ownership/consumer set and one of these is evidenced:

- duplicated rules have drifted or conflict;
- resources are always loaded together and separation adds no independent lifecycle value;
- two resources represent one canonical contract split by historical accident.

Do not merge when different audiences, modes, validation cycles, or ownership justify separation.

### `no_change`

Eligible when:

- no evidenced architectural defect requires mutation; or
- several architectures are reasonable but the existing design satisfies current boundaries, loading, validation, and maintainability needs; or
- evidence is insufficient for a safe structural recommendation.

`no_change` is a valid positive conclusion, not a failure to decide.

## Tie-breakers

When more than one decision remains eligible, apply in this order:

1. **Safety/authority**: choose the option that resolves unsafe or conflicting authority without weakening controls.
2. **Activation clarity**: prefer the option that removes persistent activation ambiguity with the least duplicated semantics.
3. **Ownership/evidence lifecycle**: preserve independently owned or independently validated behavior when evidence shows real independence.
4. **Progressive-loading repairability**: prefer routing/reference extraction over structural fragmentation when loading alone is the issue.
5. **Change radius**: prefer the smallest structural change that fully addresses the evidenced problem.
6. **Minimum-change default**: when still tied or evidence is incomplete, choose `no_change` and state what evidence would justify a different decision.

Record the tie-breaker used in the report.

## Observation versus judgment

Examples:

- Observation: "`mode-x` has a dedicated validator and three mode-only references."  
  Judgment: "This creates an independent validation lifecycle."
- Observation: "The package has 24 reference files."  
  Invalid judgment: "It should be split." Size alone has no architectural conclusion.
- Observation: "No deterministic consumer signal was found for `legacy.md`."  
  Invalid judgment: "`legacy.md` is orphaned." Consumer tracing is incomplete until dynamic/external/intentional retention paths are checked.

## Severity

- `critical`: wrong activation/authority, unsafe ownership, fabricated measured claims, or broken delivery can result.
- `high`: architecture blocks reliable use, hides mandatory resources, or creates conflicting handoffs.
- `medium`: maintainability/context/load issue with concrete operational impact.
- `low`: organization/clarity issue without correctness impact.

Severity never substitutes for decision evidence.

## Claim discipline

Use:

- `measured`: current-run executed command/scenario evidence;
- `observed`: direct package/output inspection;
- `derived`: deterministic calculation from evidence;
- `supplied`: user/external evidence not independently executed;
- `planned`: not executed;
- `blocked`: could not be obtained.

Do not claim architecture precision, reviewer consistency, behavioral improvement, regression reduction, or scenario pass rate unless the relevant scenarios were actually executed.
