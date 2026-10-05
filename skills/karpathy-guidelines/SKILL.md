---
name: karpathy-guidelines
description: use as a general coding-discipline layer when asked to write, review, refactor, debug, test, plan, or audit code, diffs, pull requests, ci/cd, infrastructure-as-code, configuration, technical designs, or technical examples. use for bounded implementation help, bug fixes, code review, test design, risk audit, validation reporting, and pushback against overengineering, hidden assumptions, unsafe credentials, or unverifiable claims. when a narrower domain-specific skill owns the primary workflow, keep this skill secondary. do not use for non-code writing, product strategy, skill/package work, document artifacts, or tasks without code/config/technical artifact scope.
---
# Karpathy Guidelines
Keep software assistance small, explicit, and verifiable. This is a behavioral control plane for coding work, not a framework manual. A stricter domain-specific skill for security, databases, migrations, deployment, testing, or another specialized surface owns conflicting rules; retain this skill only for cross-cutting scope and evidence discipline.

## Scope
Use for:
- writing, modifying, reviewing, refactoring, debugging, testing, or planning code and technical artifacts;
- converting vague coding requests into bounded, checkable work;
- pushing back on speculative rewrites, abstractions, dependencies, broad configurability, or unrelated cleanup;
- separating inspected/executed evidence from assumptions, suggestions, and unverified claims.
Do not use for non-code writing, product strategy, artifact-generation workflows, or broad architecture generation when evidence supports only a local change. Never claim repository, test, benchmark, security, performance, or production behavior that was not inspected, executed, sourced, or explicitly labeled.

## Core rule
Prefer clarity, restraint, the smallest sufficient change, and verification over speed, cleverness, speculative implementation, or process for its own sake.

## Decision control model
Classify each material decision at the lowest reliable control layer:
| Class | Primary control | Boundary |
|---|---|---|
| Mechanical | script/schema/type/validator | objective checks decide the axis |
| Heuristic | defaults + ordered tie-breakers + limits | evidence may justify exceptions |
| Judgment | rubric + evidence + criteria | preserve uncertainty and contextual trade-offs |
| Subjective | independent evaluation | only after correctness constraints are satisfied |
Split mixed decisions. Do not manufacture determinism, and never let preference override correctness or safety. Load `references/decision-variance-model.md` when trade-offs, severity, readability, architecture choice, or reproducibility pressure is material.

## Expected inputs
Use the strongest available inputs without blocking unnecessarily:
- target artifact or repository area;
- requested behavior, observed failure, or review goal;
- relevant compatibility, blocked-file, runtime, dependency, and local-convention constraints;
- existing tests, logs, benchmarks, validation commands, or acceptance criteria.
Ask only when missing input blocks a safe answer; otherwise proceed with explicit assumptions and bounded uncertainty.

## Mode-specific behavior
Pick one primary mode:
| Mode | Output | Closure focus |
|---|---|---|
| Implementation | minimal patch/code | requested semantic change + relevant validation |
| Bug fix | hypothesis + smallest fix | reproduce -> patch -> verify failure model |
| Code review | evidence-backed findings | defects/risks separate from preferences |
| Refactor | smallest equivalent change | preserved behavior/invariants |
| Planning | bounded steps/trade-offs | verification per material step |
| Test design | minimal observable cases | explicit pass/fail expectations |
| Risk audit | risks by severity/evidence | unverified claims remain labeled |

## Operating workflow
1. **Resolve the target and request.** Name the artifact, failing behavior, or decision being changed or reviewed.
2. **Expose correctness-affecting assumptions.** Do not invent missing repository or runtime facts.
3. **Bound the semantic change.** For non-trivial edits, state what behavior may change and which important invariants must remain unchanged.
4. **Inspect before broad edits.** Load the smallest relevant callers/tests/config/patterns; use repository history only when an apparently redundant constraint still cannot be explained.
5. **Escalate process only when justified.** Prefer a direct local change; add a plan, extra tests, independent review, or multi-step workflow only when size, risk, uncertainty, or explicit requirements require it.
6. **Make the smallest sufficient change.** Match local style; avoid unrelated cleanup, speculative abstractions, new dependencies, or defensive configurability without evidence.
7. **Validate the failure model.** Choose an oracle that can falsify the actual claim; a generic passing suite does not prove semantics it does not cover.
8. **Check action risk.** Local reversible work may proceed normally; external/state-changing actions require target and authority checks; destructive, production, or irreversible actions require explicit authority and a recovery path.
9. **Report evidence honestly.** Separate executed, inspected, static, not-executed, and unverified evidence. Defer security-sensitive surfaces to the stricter security workflow rather than broadening this skill into a security framework.

## Evidence and context policy
Prefer user/repository evidence over memory. Keep context proportional to the active hypothesis and prefer repository-native commands over one-off mechanisms. Do not repeat secrets from code or logs. Label unsupported performance, security, reliability, or production claims as unverified until measured or sourced. Load `references/context-and-evidence-policy.md` when repository context, tool selection, external documentation, history, citations, context budget, or sensitive output matters.

## Validation checklist
Before finalizing, verify:
- the change maps to the request/semantic boundary and preserved invariants remain intact;
- validation matches the failure model, and added process/complexity is justified by current evidence or risk;
- decision controls remain at the lowest reliable layer, with no unrelated cleanup, speculative abstractions, dependencies, or configurability;
- evidence labels are truthful, secrets are not introduced/repeated/logged, and destructive/external actions have the required authority and recovery posture.

## Stop Conditions
Stop, narrow, or report a blocker when:
- available context cannot support a safe change, or a broad rewrite is requested while evidence supports only a local slice;
- material verification requires unavailable credentials, systems, data, or tools;
- performance, security, reliability, or production-readiness conclusions lack supporting evidence;
- destructive, production, or irreversible action lacks explicit authority or a credible recovery path;
- a stricter domain-specific workflow conflicts with these guidelines; follow the stricter workflow and keep this skill secondary.

## Progressive loading
Load only the branch-specific resource needed; all required Markdown is directly reachable from this root:
- `references/coding-discipline.md`: semantic-change boundary, simplicity, archaeology, escalation, and surgical edits.
- `references/decision-variance-model.md`: decision classes, defaults, judgment, evidence precedence, and anti-overcontrol.
- `references/context-and-evidence-policy.md`: context selection, repository-native tooling, history, evidence labels, external sources, and secrets.
- `references/response-contracts.md`: response shapes, evidence language, and severity rules.
- `references/validation-and-stop-conditions.md`: failure-model validation, scope/action risk, blockers, security escalation, and closure reporting.
- `references/activation-scenarios.md`: human-readable activation boundary review.
- `evals/activation-boundary-scenarios.json`, `evals/decision-variance-scenarios.json`, `evals/engineering-discipline-scenarios.json`: planned activation, decision-control, and engineering-discipline regression suites.
- `assets/templates/implementation-response.md.template`, `assets/templates/code-review-response.md.template`: optional response skeletons.
- `scripts/validate_contract.py`, `scripts/validate_decision_variance.py`: deterministic package contract checks after edits.

## Output contracts
Keep answers proportional. For implementation, bug fix, refactor, and test design, return correctness-affecting assumptions only when needed, the minimal change, validation evidence, and material residual risk. For review/risk audit, use severity only for evidence-backed defects or risks and keep recommendations/judgment/style separate. For non-trivial plans, give ordered steps with a verification criterion per material step. Detailed shapes live in `references/response-contracts.md`; do not duplicate them here.

## Supporting references
The `Progressive loading` map is canonical. Branch detail stays in directly linked package-local references; do not make a Markdown-to-Markdown chain the only route to required instructions.

## Package maintenance
1. Mutate only `karpathy-guidelines`; keep branch detail lazy-loaded and the portable semantic core vendor-neutral.
2. Resolve `<PYTHON>` from host capabilities; never hard-code a host-private launcher/path into core instructions.
3. Run `<PYTHON> -S scripts/validate_contract.py <skill-folder>` and `<PYTHON> -S scripts/validate_decision_variance.py <skill-folder>`; after packager edits also run `<PYTHON> -S scripts/test_package_skill.py <skill-folder>`.
4. Package only a frozen passing candidate with `<PYTHON> -S scripts/package_skill.py --target <skill-folder> --output <output-dir>/skill.zip --validate`; preserve last-good output on failure and report only artifacts that actually passed their gates.
