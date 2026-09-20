# Pre-Evolution Foundation

Use this contract before adding any evolutionary or multi-candidate search mode. The goal is to make the normal optimizer observable, attributable, and comparable first. This reference defines reusable state artifacts; it does not implement crossover, mutation search, population management, or automatic canonical-policy promotion.

## 1. Canonical phase model

Use six phases for the normal workflow:

1. `establish` - trust intake, target class, capability/runtime profile, inventory, portability, baseline, evaluator/source freeze.
2. `diagnose` - evidence providers inspect the frozen baseline and emit findings without mutating by default.
3. `select` - reconcile evidence, classify change intent, build/rank hypotheses, choose one bounded experiment.
4. `mutate` - exactly one declared mutation owner applies the selected transformation batch to an isolated candidate.
5. `evaluate` - run the cheapest sufficient evaluation level, then escalate only survivors; compare candidate with its parent/baseline using frozen evidence.
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

Build a capability map before material mutation when the target is complex, a comparison is requested, or capability loss would be costly. Store it outside the target unless the target itself owns such a contract.

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

Do not report an experiment as an optimization until the frozen comparison supports that claim. Required repairs may be accepted without claiming measured improvement.

## 5. Transformation registry

Represent candidate changes as semantic transformations rather than only diffs. Record one transformation entry per bounded causal change or inseparable batch:

- transformation id;
- change intent (`repair`, `optimization`, `experiment`);
- source hypothesis and evidence;
- parent candidate identities;
- affected capability ids and files;
- operation/mechanism summary;
- expected effect and evaluator refs;
- dependencies/conflicts;
- lifecycle status (`planned`, `applied`, `accepted`, `rejected`, `reverted`);
- evidence supporting the final status.

Do not invent causal certainty. When multiple edits cannot be separated, record them as one inseparable batch and state that attribution is limited.

Use `assets/templates/transformation-registry.json.template`.

## 6. Experiment registry

Record every evaluated candidate, including failed and rejected experiments. At minimum keep:

- experiment id;
- target identity and target class;
- parent candidate ids;
- candidate identity;
- transformation ids;
- evaluator/scenario identities;
- evaluation level reached;
- metrics/gates;
- result and decision;
- evidence refs;
- reason for rejection or acceptance.

Current-run history is first-class evidence. Cross-run history is advisory evidence only unless target class, capability surface, evaluator contract, and relevant environment are comparable. Never turn one target's outcome into a universal rule.

Use `assets/templates/experiment-registry.json.template`.

## 7. Evaluation ladder

Use staged evaluation to avoid spending expensive evidence on candidates that already fail cheap gates.

- `L0-structural`: package shape, references, identity, protected paths, schema/frontmatter, syntax.
- `L1-deterministic`: target validators/tests/static checks and deterministic contract checks.
- `L2-focused`: scenarios/metrics directly tied to the selected hypothesis and touched capabilities.
- `L3-harness`: broader scenario harness, isolation/leakage evidence, regression/adversarial coverage.
- `L4-benchmark`: full comparable benchmark against baseline/parent/control arms when improvement claims justify the cost.
- `L5-holdout`: evaluator-only/independent holdout for promotion claims vulnerable to overfitting.

Failing a required lower level blocks escalation. A candidate may stop early when the requested claim does not require higher levels. Use `assets/templates/evaluation-plan.json.template`.

## 8. Evidence-provider and mutation-owner separation

Default evidence providers to read-only or checklist/audit modes during `diagnose`. Examples include benchmark, harness, quality review, architecture/context review, activation/prompt review, consistency, documentation, security, testing analysis, cleanup analysis, and token analysis.

Exactly one declared owner mutates each transformation batch. Default owner is `skill-improver`; `reproducibility-engineer` may own a bounded batch when routed in apply mode; another specialist may own a batch only when explicitly delegated by the caller/orchestrator and when its local contract permits mutation.

A provider finding is evidence, not permission to edit. Do not let several specialists independently rewrite the same candidate before attribution and gates are recorded.

## 9. Ablation and attribution

Use ablation only when it can answer a real attribution question. Consider it when:

- a candidate contains multiple independent transformations and a strong improvement claim depends on knowing which mattered;
- a transformation repeatedly appears in high-performing candidates but causal contribution is unclear;
- one transformation is costly/risky and may be unnecessary.

Do not run combinatorial ablation by default. Prefer one-change experiments. When ablation is used, evaluate the full candidate and one-minus-transformation variants under the same frozen evaluator and record the result as separate experiments.

## 10. Promotion separation

Keep two promotion decisions distinct:

- `target promotion`: this candidate may replace the target baseline after its own gates pass.
- `workflow-policy promotion`: a strategy should influence the Booster's canonical policy only after evidence across multiple relevant targets/classes supports it.

A target win never automatically changes the Booster's canonical workflow.

## 11. Pre-evolution readiness gate

The Booster is ready to add an evolutionary mode only when the canonical workflow can already:

1. classify target class;
2. produce/consume a capability map where material;
3. classify each change as repair/optimization/experiment;
4. assign one mutation owner per transformation batch;
5. write transformation and experiment registries;
6. execute the evaluation ladder with frozen identities;
7. compare parent/baseline/candidate without collapsing hard gates into one score;
8. preserve rejected experiments and causal limitations;
9. use holdout/independent evaluation for promotion claims when overfitting risk is material;
10. keep target promotion separate from workflow-policy promotion.

Validate machine-readable artifacts with `scripts/validate_pre_evolution_state.py`. Passing this gate means the foundation is structurally ready; it is not evidence that an evolutionary search mode itself exists or works.
