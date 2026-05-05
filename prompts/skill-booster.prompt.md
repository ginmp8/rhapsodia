@skill-booster

Optimize the target skill package using the full Skill Booster workflow.

TARGET_SKILL_PATH: @TARGET_SKILL

Goal:
Perform evidence-based optimization of the target skill: activation precision, architecture, workflow clarity, output contract, consistency, docs, validation, security, hygiene, and token efficiency.

Mode:
Full optimization. Do not stop at audit/plan unless blocked. Only edit files inside the target skill package.

Required specialist sequence:
1 skill-creator-juiced
2 skill-benchmark
3 skill-harness
4 skill-hypothesis-discovery
5 skill-improver
6 skill-change-gate
7 skill-package-architecture-review
8 context-architect
9 skill-prompt-and-activation-review
10 prompt-architect
11 skill-consistency-repair
12 documentation-quality
13 karpathy-guidelines
14 security-and-governance-review
15 skill-testing-and-validation
16 skill-cleanup-and-simplification
17 skill-token-efficient
18 skill-testing-and-validation after compression
19 skill-hardening
20 final skill-change-gate
21 final skill-benchmark
22 final skill-improver closure
23 final skill-token-efficient closure audit

For each pass:
Run the specialist when available; otherwise apply its checklist. Mark status explicitly as run, checklist, blocked, not-applicable, or not-run. Do not skip silently.

Baseline and evaluation:
Before edits, establish baseline benchmark/harness evidence. Freeze evaluator, scenarios, fixtures, expected outputs, and scoring before mutation. Do not change evaluation criteria during patches. Separate measured results from inferred, advisory, checklist-based, or planned findings.

Hypothesis rules:
Run skill-hypothesis-discovery after baseline/harness and before skill-improver patches. Generate 5-10 evidence-backed hypotheses from benchmark findings, harness gaps, validation failures, activation risks, architecture, consistency, docs, security, hygiene, token waste, user goals, or observed failures. Deduplicate, rank, select top 3-5, and recommend next 1-3 to test.

Each hypothesis must record:
id, evidence signal, expected improvement, files affected, validation method, required gate, risk, confidence, testability, and recommendation: test-now, defer, gather-evidence, reject, or no-mutation.

Patch policy:
Apply bounded patches, preferably one hypothesis per patch. Record for each meaningful change: hypothesis/repair id, files changed, expected improvement or blocker removed, validation method, change-gate decision, accept/reject/revert decision, and evidence. Revert rejected hypotheses unless the change is independently required as a blocking repair.

Protected paths:
Do not edit .git, secrets, credentials, benchmark fixtures, expected outputs, generated evidence, old zips, unrelated repositories, or read-only files.

Token efficiency:
Run main token compression only after behavior, architecture, docs, consistency, safety, and validation gates are stable. Run final token-efficiency pass preferably in audit/validate mode. If it mutates anything, rerun minimum required validation/package checks. Never weaken activation, safety, validation, output contracts, stop conditions, routing, hypothesis rules, or evidence duties for brevity.

Change gates:
Run skill-change-gate after candidate changes and again before final benchmark/closure. Benchmark improvement never overrides blocking regressions in activation, scope, references, safety, validation, packaging, evidence discipline, or output contract.

Final outputs:
Report:
1 target skill name/path
2 initial inventory
3 baseline benchmark/audit result
4 hypothesis discovery summary
5 specialist pass matrix
6 accepted hypotheses
7 rejected/reverted hypotheses
8 deferred hypotheses
9 required repairs kept without measured improvement
10 files changed
11 protected paths respected
12 validation commands and pass/fail/not-run results
13 before/after comparison
14 change-gate and final change-gate results
15 final benchmark result
16 final token-efficiency result
17 remaining risks/assumptions
18 next recommended improvement or no-mutation recommendation
19 skill.zip path/link only if validation and package checks pass

Packaging:
If validation passes, package optimized target as skill.zip. If packaging fails, report the exact blocker and do not claim readiness.

Truthfulness:
Do not claim any specialist pass, benchmark, harness, validation, security review, scenario test, token reduction, change gate, or package check was executed unless actually run or explicitly applied as checklist. Do not claim measured improvement from hypothesis discovery alone.