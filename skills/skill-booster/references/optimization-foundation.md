# Optimization Foundation

## At a Glance

- **Purpose:** Define the canonical optimization control model shared by direct repair, single-candidate optimization, and explicit evolutionary search.
- **Load when:** Choosing target class, change intent, execution strategy, evaluation depth, or promotion evidence for a material optimization.
- **Decision impact:** Determines direct-repair vs candidate/search routing, transformation ownership, the staged evaluation ladder, evaluator/holdout isolation, and the evidence required before promotion.

## Contents

- 1. Canonical phase model
- 2. Target classes
- 3. Capability map
- 4. Change-intent taxonomy
- 5. Strategy gate
- 6. Transformation registry
- 7. Experiment registry is conditional
- 8. Evaluation ladder
- 9. Evidence-provider and transformation-owner separation
- 10. Ablation and attribution
- 11. Promotion separation
- 12. Search-strategy isolation invariants
- 13. Resumable run-state and strategy evidence
- 14. Evaluation contamination and promotion holdout
- 15. Promotion attestation
- 16. Research-backed optimization


Use this contract for canonical optimization regardless of search strategy. The core optimizer must stay observable, attributable, comparable, and fully usable without evolutionary search. Evolution is an optional strategy layered on top of this foundation, not a prerequisite for it.

## 1. Canonical phase model

Use six phases for the normal workflow:

1. `establish` - trust intake, target class, capability/runtime profile, inventory, portability, baseline, evaluator/source freeze.
2. `diagnose` - evidence providers inspect the frozen baseline and emit findings without editing by default.
3. `select` - reconcile evidence, classify change intent, choose a bounded change, and select an execution strategy.
4. `transform` - exactly one declared transformation owner applies the selected change to an isolated candidate.
5. `evaluate` - run the cheapest sufficient evaluation level and compare against the frozen baseline/control evidence.
6. `prove` - hardening, final gates, benchmark/holdout when required, final freeze, portability closure, package, and receipts.

The pass ledger may contain repeated specialists, but every pass must map to one of these phases. Do not treat the raw pass count as the architecture.

## 2. Target classes

Classify the target before optimization. Use the narrowest useful class:

- `deterministic-tool`: objective package/tool/action behavior with strong mechanical validation potential.
- `code-engineering`: code-oriented skill where tests, build, static analysis, and behavioral scenarios dominate.
- `research-analytic`: evidence-grounded analysis where traceability and output conformance are enforceable but conclusions retain bounded judgment.
- `orchestration-meta`: router/controller/meta-skill where ownership, handoffs, evaluator isolation, and recursion controls dominate.
- `subjective-design`: perceptual/editorial/design work where independent qualitative review remains material.
- `mixed-other`: none of the above cleanly fits; state why.

Target class is a routing input, not a quality score. Historical results from one class must not automatically become policy for another.

## 3. Capability map

Build a capability map before material transformation when the target is complex, a comparison is requested, or capability loss would be costly. Store it outside the target unless the target itself owns such a contract.

Each capability should identify:

- stable capability id and name;
- capability kind;
- current owner/authority;
- implementing resources;
- known consumers;
- validators/evaluators;
- evidence refs and confidence/status;
- invariants that must survive optimization.

The capability map is semantic evidence. File presence alone does not prove a capability exists or works.

Use `assets/templates/capability-map.json.template` as the interchange shape.

## 4. Change-intent taxonomy

Every selected change is exactly one of:

- `repair`: fixes a demonstrated defect or broken contract. Success means the defect is removed without regression; a higher score is optional.
- `optimization`: seeks a predeclared measurable improvement on an active metric while preserving hard gates.
- `experiment`: tests a plausible bounded hypothesis where improvement is not yet established.

Do not force a repair into experimental semantics. Do not report an experiment as an optimization until the frozen comparison supports that claim.

## 5. Strategy gate

Choose the least complex strategy that can answer the problem:

- `direct-repair`: use for a demonstrated defect with a sufficiently known correction and deterministic/focused validation.
- `single-candidate`: use for a bounded optimization or experiment with a clear hypothesis and evaluator.
- `evolutionary-search-eligible`: mark only when several materially different solutions are plausible, interactions are difficult to predict, the evaluator is sufficiently discriminating, and a bounded search budget is justified.

`evolutionary-search-eligible` is only an eligibility result. It must not activate evolutionary execution. Enter `evolutionary-optimization` only when the user explicitly requests it or an already-approved plan requires it. Otherwise continue with the canonical single-candidate path.

Repairs should normally use `direct-repair`; do not create populations, search state, or lineage merely to fix a known defect.

### Instruction/control freedom budget

When instruction design is part of the selected change, classify the affected behavior before adding constraints:

- `high`: intentional exploration, synthesis, taste, or expert judgment; constrain objectives, evidence, safety, and output contracts without prescribing the reasoning path;
- `medium`: bounded judgment; prefer rubrics, templates, examples, tie-breakers, schemas with flexible fields, or parameterized helpers;
- `low`: objective, fragile, repetitive, security-sensitive, or must-always-hold behavior; prefer executable/schema/gate enforcement and minimize model discretion.

Do not reduce freedom merely to increase superficial consistency. Do not preserve high prompt freedom where failures are objective and a stronger portable control layer can remove them.

## 6. Transformation registry

Represent accepted/planned target changes as semantic transformations rather than only diffs. Record one transformation entry per bounded causal change or inseparable batch:

- transformation id;
- change intent (`repair`, `optimization`, `experiment`);
- source hypothesis when one exists, otherwise defect/evidence reference;
- baseline/control identity as needed for comparison;
- affected capability ids and files;
- operation/mechanism summary;
- expected effect and evaluator refs;
- dependencies/conflicts;
- lifecycle status (`planned`, `applied`, `accepted`, `rejected`, `reverted`);
- evidence supporting the final status.

Do not invent causal certainty. When multiple edits cannot be separated, record them as one inseparable batch and state that attribution is limited.

Use `assets/templates/transformation-registry.json.template`.

## 7. Experiment registry is conditional

Create `assets/templates/experiment-registry.json.template` only when the run actually performs an experiment, compares multiple candidate alternatives, or needs to retain rejected/inconclusive experimental evidence.

A deterministic repair does not require an experiment registry. A straightforward single-candidate optimization does not require one unless the run is explicitly being treated as an experiment.

When an experiment registry exists, retain candidate identity, transformation refs, evaluator/scenario identity, evaluation level, metrics/gates, result/decision, evidence refs, and rejection/acceptance rationale. Cross-run history is advisory unless target class, capability surface, evaluator contract, and relevant environment are comparable.

## 8. Evaluation ladder

Use staged evaluation to avoid spending expensive evidence on changes that already fail cheap gates.

- `L0-structural`: package shape, references, identity, protected paths, schema/frontmatter, syntax.
- `L1-deterministic`: target validators/tests/static checks and deterministic contract checks.
- `L2-focused`: scenarios/metrics directly tied to the selected change and touched capabilities.
- `L3-harness`: broader scenario harness, isolation/leakage evidence, regression/adversarial coverage.
- `L4-benchmark`: full comparable benchmark when an improvement claim justifies the cost.
- `L5-holdout`: independent/evaluator-only holdout for promotion claims exposed to overfitting risk.

Failing a required lower level blocks escalation. A candidate may stop early when the requested claim does not require higher levels. Use `assets/templates/evaluation-plan.json.template`.

The evaluation-plan template may carry fields consumed by an optional search adapter. Canonical optimization must ignore search-only fields unless evolutionary mode is active; their presence must never make evolutionary readiness a completion requirement.

## 9. Evidence-provider and transformation-owner separation

Default evidence providers to read-only or checklist/audit modes during `diagnose`. Examples include benchmark, harness, quality review, architecture/context review, activation/prompt review, consistency, documentation, security, testing analysis, cleanup analysis, and token analysis.

Exactly one declared owner changes each transformation batch. Default owner is `skill-improver`; `reproducibility-engineer` may own a bounded batch when routed in apply mode; another specialist may own a batch only when explicitly delegated by the caller/orchestrator and when its local contract permits changes.

A provider finding is evidence, not permission to edit. Do not let several specialists independently rewrite the same candidate before attribution and gates are recorded.

## 10. Ablation and attribution

Use ablation only when it answers a real attribution question. Do not run combinatorial ablation by default. Prefer one-change evaluations when practical.

## 11. Promotion separation

Keep two promotion decisions distinct:

- `target promotion`: this candidate may replace the target baseline after its own gates pass.
- `workflow-policy promotion`: a strategy should influence the Booster's canonical policy only after evidence across multiple relevant targets/classes supports it.

A target win never automatically changes the Booster's canonical workflow.

## 12. Search-strategy isolation invariants

The canonical optimizer must remain valid when no search controller is installed. Downstream specialists used by the canonical path should receive generic concepts such as baseline, transformation, candidate, evaluator, evidence, accept/reject, and capability impact. Search-controller-specific metadata belongs at the optional adapter boundary.

Evolutionary readiness is not a quality gate for canonical optimization. Search-specific state is created only after explicit entry into the evolutionary branch.

Validate canonical machine-readable artifacts with `scripts/validate_optimization_state.py`. For ordinary canonical work, validate capability map, transformation registry, and evaluation plan when material; add an experiment registry only when one was actually produced.

## 13. Resumable run-state and strategy evidence

For long, interrupted, or complete optimization, keep an external canonical run-state bound to baseline, current candidate, evaluator set, source set, phase, material findings, finite budgets, and invalidated evidence. Validate it before resume; never silently refresh an identity after drift.

Before each material transformation, persist a strategy decision. `direct-repair` needs a demonstrated defect; `single-candidate` must record why direct repair is insufficient; `evolutionary-search` must record why a single candidate is insufficient, a finite search budget, stop conditions, and explicit evolutionary authorization. Strategy complexity is evidence-driven, not a quality signal.

## 14. Evaluation contamination and promotion holdout

Track evaluator sets separately from evaluation levels. Record each evaluator identity, role, freeze state, and whether its feedback was visible to the transformer. If candidate generation or repair used feedback from an evaluator intended to support promotion, mark the run contaminated for that claim. A contaminated promotion requires a frozen `promotion-holdout` evaluator that remained hidden from transformation plus required `L5-holdout` evidence. Never reclassify an exposed development evaluator as a blind holdout.

## 15. Promotion attestation

After all final gates and freeze verification, bind the promoted target to one attestation containing controller, baseline, candidate, evaluator/source-set, run-state, validation, final change-gate, portability, traceability when applicable, integration, and package identities. Target promotion remains separate from workflow-policy promotion.

## 16. Research-backed optimization

When a bounded research corpus materially determines target changes, freeze or identify that corpus before deriving requirements. Account for every extracted finding, preserve reverse justification from every substantive change to a requirement/finding, define deciding evaluations before mutation when feasible, and report trace completeness as corpus-bounded rather than universal knowledge completeness.
