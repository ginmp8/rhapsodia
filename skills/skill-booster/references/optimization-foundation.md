# Optimization Foundation

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
