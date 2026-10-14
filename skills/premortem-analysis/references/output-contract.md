# Report and handoff contract

## Purpose and load condition

Load when composing `standard`/`governed` reports, delivering structured JSON, or providing advisory output to an owning workflow. The canonical JSON shape is documented in `assets/premortem-report.schema.json` (also directly linked by `SKILL.md`).

## Human-readable report layout

1. **Header:** subject, mode, `complete|partial|blocked`, evidence-gathering status, as-of date only when actually known.
2. **Plan:** goal, failure criterion, planning horizon, evidence scope, unknowns and assumptions.
3. **Counterfactual:** one explicit future-failed scenario, labeled fictional.
4. **Risk table or sections:** `RISK-001`-style stable IDs, causal path, affected objective, `supported|contradicted|uncertain|unverified`, controllability, impact with justification, supporting/contrary source refs, challenge and evidence gaps.
5. **Controls:** prevention, observable detection or test, response/rollback, verification and owner or `unknown`.
6. **Changes:** distinct IDs, concrete proposed plan change, associated risk IDs, `proposed|accepted|rejected|deferred` (only if evidenced), decision owner, and decision evidence if status is not proposed.
7. **Closure:** residual risks, no-go/approval gates for governed cases, external validation needed, alternatives such as reduction of scope, and limitations.

A complete analysis may still have unknown risks and unaccepted changes; do not confuse report completion with project readiness. `partial` means material planning/evidence gaps limit the analysis. `blocked` means the skill cannot responsibly support the requested high-stakes decision or the user asks for impermissible authority.

## JSON semantics

Use snake_case, stable risk/change/source IDs, real JSON `null` for unknown optional scalars, and typed enum values. Required fields and enums are enforced by the schema and dependency-free validation script. Machine reports must keep the future-failure scenario explicitly fictional and include any risk source IDs in the source registry.

Every retained risk must have a nonempty causal chain, evidence status, a falsifiable challenge, a proposed control package, consequence/impact rationale, and control owner as a string (`unknown` if absent). If no risks can be grounded without invention, use `partial` with an empty array and describe the gap; do not pad the list.

Plan changes reference valid risk IDs; non-`proposed` dispositions require recorded human/owner decision evidence. A source entry describes actual available material, with locator and access level. `source_id` is not itself a truth guarantee. A failed validator is a failed **structural** gate, not a license to weaken the schema.

## Cross-skill interoperability

- **Mago:** consume hypotheses and recommended plan deltas as read-only input; only Mago authors canonical technical plans, validation plans and handoffs.
- **Skill Booster:** consume prospective regression and mitigation hypotheses; Booster alone changes/promotes skill candidates under its gates.
- **Decision Engine:** accept bounded evidence and uncertainty; decision criteria, status and approval authority remain with its caller.
- **Doubt-Driven Development:** examine specific claims/artifacts; this analysis supplies causal risk hypotheses, not reviewer verdicts.
- **Incident Postmortem Writer:** route already-observed failures there rather than rewriting them as imagined outcomes.

Default handoff is user-visible Markdown, optionally JSON. No direct imports or runtime dependencies on other skills; do not claim that merely listing a consumer constitutes an installed integration.
