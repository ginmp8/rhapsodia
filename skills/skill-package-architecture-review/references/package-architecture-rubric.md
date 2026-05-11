# Package Architecture Rubric

Use this rubric when a review requires architectural judgment, not only structural inventory.

## Evidence classes

- Mechanical evidence: file tree, line counts, local links, references, script arguments, template locations, eval files, package size, validator output.
- Declared contract: activation description, mode table, workflow, resource map, output contract, stop conditions, handoff rules.
- Behavioral evidence: executed scenario outputs, supplied benchmark results, harness reports, prior failures, user feedback.
- Reviewer judgment: cohesion, coupling, ownership fit, maintainability, cognitive load, and risk interpretation.

Never mix these classes silently. Label findings as mechanical, behavioral, or judgment.

## Scoring dimensions

Score each dimension from 0 to 4 when the user asks for a score. Otherwise use the criteria qualitatively.

| Dimension | 0 | 2 | 4 |
|---|---|---|---|
| Control-plane clarity | no usable `SKILL.md` contract | basic workflow, weak routing | compact router with modes, loading map, stop conditions, and output contract |
| Cohesion | unrelated responsibilities | related but overlapping or ambiguous | one clear domain with coherent activation and owner model |
| Resource integration | resources unexplained or misleading | many resources referenced but weakly consumed | resources are loaded, consumed, filled, validated, or intentionally asset-only |
| Progressive loading | knowledge dump or hidden dependencies | some references but unclear loading | conditional references and scripts are discoverable only when needed |
| Boundary governance | no authority or handoff rules | partial boundaries | explicit ownership, handoffs, stop conditions, and adjacent-skill boundaries |
| Validation architecture | claims without evidence | basic validators or planned scenarios | deterministic checks and measured claims are tied to commands or evidence |
| Package hygiene | scaffold remnants, stale outputs, caches | mostly clean with minor debris | clean tree, no placeholders, no generated noise, packageable layout |
| Maintainability | changes are brittle and cross-cutting | maintainable with known hotspots | modular, testable, and easy to evolve without domain drift |

## Cohesion versus size

A large skill is not automatically a bad skill. Treat size as healthy when:

- one domain or workflow family explains most modes;
- `SKILL.md` remains a control plane, not a knowledge dump;
- branch-specific detail lives in references;
- resources have declared consumers or loading rules;
- validation burden is proportionate to risk;
- one ownership model can maintain the package.

Treat size as a risk only when it creates evidence of low cohesion, wrong activation, hidden dependencies, repeated mode logic, conflicting authority, maintenance difficulty, or excessive context loading.

## Architecture recommendation rules

Recommend `keep unified` when the package has high cohesion, one owner model, one activation surface, and manageable progressive loading.

Recommend `extract mode` when one mode has distinct trigger language, separate resources, independent validators, different user expectations, or different release cadence.

Recommend `fragment into skills` when there are multiple domains, conflicting owners, incompatible evidence policies, activation collisions, or repeated conditional routing that hides the real task.

Recommend `merge resources` when two references, templates, or scripts serve the same decision with duplicated instructions and no useful separation.

Recommend `create router` when several coherent subpackages need a shared dispatch layer and stable handoff protocol.

Recommend `handoff` when the next action is better owned by an adjacent workflow: consistency repair, hardening, harness, improver, benchmark, code review, or secure review.

## Severity model

- Critical: architecture can trigger wrong skill use, unsafe authority, fabricated measured claims, or broken package delivery.
- High: architecture blocks reliable use, hides required resources, or causes conflicting handoffs.
- Medium: maintainability or context-efficiency issue with clear operational impact.
- Low: naming, organization, or clarity issue that does not block correct execution.

## Claim discipline

A benchmark score, validator pass rate, scenario metric, package-readiness claim, or before/after improvement is measured only when supported by supplied evidence or commands executed in the current run. Otherwise mark it as planned, assumed, inferred, or not measured.
