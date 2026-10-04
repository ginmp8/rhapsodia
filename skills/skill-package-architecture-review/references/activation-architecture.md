# Activation Architecture

**Contract version:** 1.0.0

Use for `activation-architecture-review` and whenever split, extraction, or router decisions depend on how skills are selected from a catalog.

## Separate two questions

Do not treat internal cohesion and activation architecture as the same property.

- **Internal cohesion:** whether one package contains a coherent domain/workflow/evidence lifecycle.
- **Activation architecture:** whether the focal skill can be selected distinctly from adjacent skills for realistic user intents.

A package may be internally cohesive and still collide with an adjacent skill's activation surface. The reverse is also possible.

## Architecture scope

Classify the context needed for the decision before judging structure:

- `single_skill` — the focal skill can be reviewed from its own package and supplied evidence.
- `skill_family` — adjacent skill descriptions, routing relationships, or shared ownership materially affect the decision.
- `plugin_package` — a containing package/plugin or capability composition is the real architectural boundary. Keep the focal skill review bounded and hand off package-level redesign when the containing system is not in scope.

Architecture scope is evidence context, not a seventh architecture decision.

## Evidence to inspect

When available, record:

- focal `name` and `description`;
- explicit invocation language and declared non-triggers;
- adjacent skill names/descriptions that plausibly compete for the same intents;
- stable routing keys such as artifact type, domain, workflow mode, or capability;
- should-trigger and near-miss should-not-trigger cases;
- measured activation results only when those cases were actually executed with an identified evaluator/runtime.

Do not infer the whole catalog from the focal package. If adjacent catalog evidence is unavailable, set activation evidence to `unknown` or `partial` and state the gap.

## Collision states

Use bounded states rather than a fabricated precision score:

- `distinct` — supplied/observed evidence shows stable separation for the relevant intents;
- `overlap` — credible evidence shows recurring ambiguous intent or competing descriptions;
- `partial` — some adjacent surfaces were inspected but material gaps remain;
- `unknown` — the relevant catalog/activation evidence was unavailable.

Text similarity alone does not prove an activation collision. Semantic intent, routing keys, and executed cases are stronger evidence.

## Decision implications

- `split` may be supported when one package contains distinct activation surfaces plus independent ownership/evidence lifecycle signals. Activation overlap alone is not sufficient.
- `extract_mode` requires a distinct user intent plus an independent lifecycle signal from the main rubric.
- `create_router` requires coherent separate destinations and stable dispatch evidence; a router must not duplicate destination semantics.
- `no_change` remains valid when catalog evidence is unknown and the internal package has no evidenced architectural defect.

Never manufacture adjacent skills, trigger results, or collision rates to complete the review.
