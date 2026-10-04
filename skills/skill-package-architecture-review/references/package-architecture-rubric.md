# Package Architecture Rubric

**Rubric version:** 3.0.0

Use this rubric for architectural judgment. It is a decision contract, not a substitute for context. Architecture scope, activation evidence, evolution scenarios, and trust topology expand the evidence model; they do not add new primary decisions.

## Evidence discipline

Separate:

- mechanical observation;
- declared package contract;
- executed behavioral evidence;
- supplied external evidence;
- derived evidence;
- reviewer judgment.

Every material judgment must reference evidence. A static rubric score is structural judgment, not measured behavioral quality. `unknown` catalog/history/trust evidence must stay unknown rather than being scored as failure.

## Dimensions

Score 0-4 only when the user asks for scoring. Otherwise apply qualitatively.

| Dimension | 0 | 2 | 4 |
|---|---|---|---|
| Control-plane clarity | unusable or contradictory | basic workflow, weak routing | compact modes/routing/loading/stop/output contract |
| Cohesion | unrelated domains/responsibilities | related but ambiguous overlap | one coherent domain/workflow family |
| Architecture-scope fit | review boundary is wrong/implicit | focal skill known but surrounding boundary uncertain | single-skill/family/plugin context is explicit and bounded |
| Activation architecture | recurring collision or fabricated routing evidence | focal triggers known, adjacent evidence partial | relevant activation surfaces/routing keys are explicit and evidence-backed |
| Resource integration | misleading/unowned resources | mixed integration | declared, consumed, validated, or intentionally asset-only resources |
| Progressive-loading architecture | knowledge dump/hidden mandatory dependencies | partial conditional loading | branch-specific resources with observable, justified context topology |
| Evolution/change isolation | routine changes cross unrelated boundaries | manageable change radius | change-sensitive decisions are localized and scenario tradeoffs explicit |
| Boundary/trust governance | unclear authority/trust transitions | partial authority mapping | explicit ownership/authority/trust topology and handoffs |
| Validation architecture | claims without evidence | basic validators/planned scenarios | independent deterministic gates and executed evidence where claimed |
| Spec/host portability | core requires host-private behavior | portable intent with gaps | host-neutral semantic core with optional adapters and explicit capabilities |
| Maintainability | changes require broad coupled edits | manageable hotspots | modular evolution without domain drift |

## Primary architecture decision enum

Choose exactly one when a primary decision is requested:

- `keep_unified`
- `split`
- `extract_mode`
- `create_router`
- `merge_resources`
- `no_change`

A handoff is a follow-up action, not an architecture decision. `architecture_scope` is context, not a seventh decision.

## Minimum evidence by decision

### `keep_unified`

Eligible when evidence supports one coherent domain/workflow family and no hard separation signal exists. Prefer when:

- one activation surface can route the focal package without evidenced persistent ambiguity;
- one authority/owner model is coherent;
- mode evidence/validation lifecycles are compatible;
- progressive loading contains context cost;
- resources can remain integrated without duplicated ownership;
- realistic change scenarios do not expose a material unresolved boundary problem.

Do not require small package size, shallow depth, or inspected repository history.

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
6. progressive-loading failure that cannot be repaired by routing/reference extraction;
7. realistic change scenarios repeatedly cross a candidate boundary while remaining isolated on each side.

File count, line count, reference count, routing depth, or stylistic preference are never separation signals by themselves. Change coupling alone is not a separation signal; it can corroborate lifecycle/change-radius evidence.

### `extract_mode`

Eligible when both are true:

1. the mode has meaningfully distinct trigger/user intent; and
2. at least one independent lifecycle signal exists: dedicated resources, validators/evals, owner/authority, release cadence, trust boundary, or separate user expectation.

Prefer extraction over full split when the rest of the package remains cohesive and the mode is the localized source of independence. Use a change scenario when future evolution is material to the choice.

### `create_router`

Eligible when all are true:

- two or more destinations are already coherent or should remain separately owned;
- stable dispatch evidence exists: explicit user intent, artifact type, domain, mode, or another deterministic key;
- one shared entry point materially reduces activation ambiguity or user burden;
- router authority can remain narrow: dispatch, not duplicate subskill semantics.

Catalog-level activation evidence should be inspected when available. Do not create a router only because a package has many modes or because adjacent catalog evidence is unknown.

### `merge_resources`

Eligible when resources share the same decision ownership/consumer set and one of these is evidenced:

- duplicated rules have drifted or conflict;
- resources are always loaded together and separation adds no independent lifecycle value;
- two resources represent one canonical contract split by historical accident.

Do not merge when different audiences, modes, validation cycles, ownership, trust boundaries, or likely change scenarios justify separation. Co-change can corroborate, never establish, merge eligibility.

### `no_change`

Eligible when:

- no evidenced architectural defect requires mutation; or
- several architectures are reasonable but the existing design satisfies current boundaries, loading, validation, activation, and maintainability needs; or
- evidence is insufficient for a safe structural recommendation.

`no_change` is a valid positive conclusion, not a failure to decide. Missing catalog or repository-history evidence can justify bounded `no_change` when no current defect is established.

## Scenario and tradeoff discipline

When a recommendation materially changes boundaries, consider at least one realistic change/quality scenario that could falsify the recommendation. Record sensitivity/tradeoff points only when evidence exists. Do not require full ATAM ceremony or invent scenario records for trivial reviews.

## Tie-breakers

When more than one decision remains eligible, apply in this order:

1. **Safety/authority**: resolve unsafe/conflicting authority without weakening controls.
2. **Activation clarity**: remove persistent activation ambiguity with the least duplicated semantics.
3. **Ownership/evidence lifecycle**: preserve independently owned/validated behavior when evidence shows real independence.
4. **Evolution/change isolation**: prefer the option that confines realistic change without creating a larger activation/composition problem.
5. **Progressive-loading repairability**: prefer routing/reference extraction over structural fragmentation when loading alone is the issue.
6. **Change radius**: prefer the smallest structural change that fully addresses the evidenced problem.
7. **Minimum-change default**: when still tied or evidence is incomplete, choose `no_change` and state what evidence would justify a different decision.

Record the tie-breaker used in the report.

## Observation versus judgment

Examples:

- Observation: "`mode-x` has a dedicated validator and three mode-only references."  
  Judgment: "This creates an independent validation lifecycle."
- Observation: "Two adjacent skill descriptions both target the same user intent."  
  Judgment: "Activation overlap is plausible; execution evidence is still needed before claiming a measured collision rate."
- Observation: "The package has 24 reference files."  
  Invalid judgment: "It should be split." Size alone has no architectural conclusion.
- Observation: "No deterministic consumer signal was found for `legacy.md`."  
  Invalid judgment: "`legacy.md` is orphaned." Consumer tracing is incomplete until dynamic/external/intentional retention paths are checked.
- Observation: "Files A and B co-changed in 80% of selected commits."  
  Invalid judgment: "A and B must be merged." Historical co-change needs causal/context corroboration.

## Severity

- `critical`: wrong activation/authority, unsafe ownership, fabricated measured claims, or broken delivery can result.
- `high`: architecture blocks reliable use, hides mandatory resources, or creates conflicting handoffs.
- `medium`: maintainability/context/evolution issue with concrete operational impact.
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

Do not claim architecture precision, reviewer consistency, activation rate, behavioral improvement, regression reduction, or scenario pass rate unless the relevant scenarios were actually executed.
