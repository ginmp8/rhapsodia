@skill-booster

Optimize the target skill package completely using the full Skill Booster workflow.

TARGET_SKILL_PATH: @TARGET_SKILL

Primary goal:
Perform a complete, evidence-based optimization of the target skill. Improve its activation precision, package architecture, workflow clarity, output contract, consistency, documentation, validation reliability, security posture, package hygiene, and token efficiency.

Required orchestration:
Use every optimization specialist pass available in the Skill Booster workflow. Do not skip a pass silently. For each pass, either run/invoke the specialist skill when available, or apply its local checklist and mark the pass status explicitly.

Required specialist sequence:
1. skill-creator-juiced
2. skill-benchmark
3. skill-harness
4. skill-hypothesis-discovery
5. skill-improver
6. skill-change-gate
7. skill-package-architecture-review
8. context-architect
9. skill-prompt-and-activation-review
10. prompt-architect
11. skill-consistency-repair
12. documentation-quality
13. karpathy-guidelines
14. security-and-governance-review
15. skill-testing-and-validation
16. skill-cleanup-and-simplification
17. skill-token-efficient
18. skill-testing-and-validation again after token compression
19. skill-hardening
20. final skill-change-gate
21. final skill-benchmark
22. final skill-improver closure
23. final skill-token-efficient closure pass

Hypothesis discovery rule:
Run skill-hypothesis-discovery after baseline benchmark/harness evidence exists and before skill-improver applies candidate patches. The discovery pass must generate evidence-backed hypotheses, not random mutations. Prefer 5-10 candidate hypotheses, deduplicate and rank them, select the top 3-5, and recommend the next 1-3 hypotheses to test in the current optimization cycle.

If a high-confidence bounded hypothesis is already supplied by the user, skill-hypothesis-discovery may validate, refine, rank, or challenge it instead of generating a broad backlog. If the benchmark is saturated, discovery must propose auxiliary metrics, evidence-gathering hypotheses, or no-mutation recommendations rather than forcing cosmetic changes.

Important ordering rule:
Run skill-token-efficient after the skill behavior, architecture, documentation, consistency, safety, and validation gates are stable. Treat step 17 as the main token-compression pass. Treat step 23 as the final token-efficiency closure pass.

Final token-efficiency rule:
Run step 23 preferably in audit/validate mode to confirm there is no remaining avoidable token waste. If step 23 applies any mutation, re-run the minimum required validation and package checks before claiming the optimized skill is ready. Do not let the final token-efficiency pass remove or weaken activation rules, safety constraints, validation gates, output contracts, stop conditions, specialist routing requirements, hypothesis-discovery rules, or evidence duties.

Mode:
Use full optimization mode. Do not stop after audit-only or plan-only unless a hard blocker prevents safe mutation.

Mutation policy:
Only edit files inside the target skill package. Do not edit .git, secrets, credentials, benchmark fixtures, expected outputs, generated evidence reports, old zip files, unrelated repositories, or files explicitly marked read-only.

Evaluation policy:
Before editing, establish a baseline. Freeze the evaluator, scenarios, fixtures, expected outputs, and scoring contract before mutation. Do not change the benchmark or evaluation criteria during candidate patches. Separate measured results from planned, derived, inferred, checklist-based, and advisory findings.

Discovery and hypothesis policy:
Do not apply random changes. Every candidate hypothesis must come from one of:
- benchmark findings;
- harness gaps;
- validation failures;
- activation or non-activation risks;
- architecture findings;
- consistency issues;
- documentation gaps;
- security/governance findings;
- cleanup or package hygiene findings;
- token-efficiency waste;
- user-supplied goals or observed failures.

For each hypothesis, record:
- hypothesis id;
- evidence signal;
- expected improvement;
- likely files affected;
- validation method;
- required evaluator/gate;
- risk;
- confidence;
- testability;
- recommendation: test-now, defer, gather-evidence, reject, or no-mutation.

Optimization method:
Apply bounded patches. Prefer one clear hypothesis per patch. Use the hypothesis-discovery backlog as the primary source of candidate hypotheses unless the user supplied a clearer bounded hypothesis.

For each meaningful change, record:
- hypothesis or required repair id;
- files changed;
- expected improvement or blocker removed;
- validation method;
- skill-change-gate decision;
- accept/reject/revert decision;
- evidence.

Separate optional improvement hypotheses from required repairs. A rejected hypothesis must be reverted or excluded from the final package unless the same file change is independently required to fix a blocking validation, security, packaging, consistency, or safety issue. In that case, record it as a required repair, not as an accepted improvement hypothesis.

Change-gate policy:
Run skill-change-gate after candidate changes from skill-improver and again before final benchmark/closure. A better benchmark score does not override a blocking regression in activation, scope boundaries, local references, safety, validation, packaging, evidence discipline, or output contract.

Required outputs:
At the end, provide:
1. target skill name and path;
2. initial inventory;
3. baseline benchmark/audit result;
4. hypothesis discovery result, including number of candidate hypotheses generated, top hypotheses selected, deferred/rejected hypotheses, and no-mutation rationale if applicable;
5. specialist pass matrix with status for every required specialist;
6. accepted hypotheses;
7. rejected or reverted hypotheses;
8. deferred hypotheses;
9. required repairs kept even without measured improvement;
10. files changed;
11. blocked paths protected;
12. validation commands and pass/fail/not-run results;
13. before/after comparison;
14. skill-change-gate and final skill-change-gate result;
15. final benchmark result;
16. final token-efficiency result from step 23;
17. remaining risks and assumptions;
18. next recommended improvement or no-mutation recommendation;
19. packaged skill.zip path or link, only if validation and package checks pass.

Package requirement:
If validation passes, package the optimized target skill as skill.zip. Do not return only a patch or partial folder. If packaging fails, report the exact blocker and do not claim the package is ready.

Truthfulness requirement:
Do not claim that a specialist pass, hypothesis discovery, benchmark, validation, security review, scenario test, token reduction, change gate, or package check was executed unless it was actually run or explicitly applied as a checklist. Mark unavailable or skipped passes honestly as blocked, not-run, not-applicable, planned, advisory, or applied-by-checklist.

Do not claim measured improvement from skill-hypothesis-discovery alone. Discovery produces candidate hypotheses and recommendations; only evaluator results, benchmark runs, scenario results, validators, or supplied evidence can support measured improvement claims.