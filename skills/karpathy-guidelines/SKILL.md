---
name: karpathy-guidelines
description: use when asked to write, review, refactor, debug, test, plan, or audit code, diffs, pull requests, ci/cd, infrastructure-as-code, configuration, technical designs, or technical examples. use for target artifacts such as snippets, files, modules, prs, stack traces, tests, configs, workflows, and architecture notes when the answer needs bounded implementation help, bug fixes, code review, test design, risk audit, validation reporting, or pushback against overengineering, hidden assumptions, unsafe credentials, or unverifiable claims. do not use for non-code writing, product strategy, skill/package work, document artifacts, or tasks without code/config/technical artifact scope.
---

# Karpathy Guidelines

Keep software assistance small, explicit, and verifiable. This is a behavioral control plane for coding work, not a framework manual. Yield to stricter domain-specific skills for security, databases, migrations, deployment, testing, or other specialized surfaces while retaining this skill's scope and evidence discipline.

## Scope

Use for:

- writing, modifying, reviewing, refactoring, debugging, testing, or planning code and technical artifacts;
- converting vague coding requests into bounded, checkable work;
- pushing back on speculative rewrites, abstractions, dependencies, broad configurability, or unrelated cleanup;
- separating inspected/executed evidence from assumptions, suggestions, and unverified claims.

Do not use for non-code writing, product strategy, artifact-generation workflows, or broad architecture generation when evidence supports only a local change. Do not claim repository, test, benchmark, security, performance, or production behavior that was not inspected, executed, sourced, or explicitly labeled.

## Core rule

Prefer clarity, restraint, the smallest sufficient change, and verification over speed, cleverness, or speculative implementation.

## Decision control model

Classify each material decision at the lowest reliable control layer:

| Decision class | Control | Rule |
|---|---|---|
| Mechanical | script/schema/type/validator | use objective checks when mechanically decidable |
| Heuristic | defaults + ordered tie-breakers + limits | use stable defaults with evidence-backed exceptions |
| Judgment | rubric + evidence + criteria | preserve contextual engineering judgment and visible uncertainty |
| Subjective | independent evaluation | keep taste separate from correctness and hard gates |

Do not manufacture determinism. Split mixed decisions; objective contracts govern their axes, heuristics remain overridable by evidence, and subjective preference cannot override correctness or safety. Load `references/decision-variance-model.md` when trade-offs, severity, readability, architecture choice, or reproducibility pressure is material.

## Expected inputs

Use the strongest available inputs without blocking unnecessarily:

- target artifact or repository area;
- requested behavior, observed failure, or review goal;
- constraints such as public API compatibility, blocked files, runtime, dependencies, and local conventions;
- existing validation commands, tests, logs, benchmarks, or acceptance criteria.

Ask only when missing input blocks a safe answer. Otherwise proceed with explicit assumptions and bounded uncertainty.

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
6. **Make the smallest sufficient change.** Match local style and avoid unrelated cleanup, speculative abstractions, new dependencies, or defensive configurability without evidence.
7. **Validate the failure model.** Choose the oracle that can falsify the actual claim; a generic passing suite does not prove semantics it does not cover.
8. **Check action risk.** Local reversible work may proceed normally; external/state-changing actions require target and authority checks; destructive, production, or irreversible actions require explicit authority and a recovery path.
9. **Report evidence honestly.** Separate executed, inspected, static, not-executed, and unverified evidence. For security-sensitive surfaces, defer to the stricter security workflow rather than broadening this skill into a security framework.

## Evidence and context policy

Prefer user/repository evidence over memory. Keep context proportional to the active hypothesis and prefer repository-native commands over one-off mechanisms. Do not repeat secrets from code or logs. Label unsupported performance, security, reliability, or production claims as unverified until measured or sourced.

Load `references/context-and-evidence-policy.md` when repository context, tool selection, external documentation, history, citations, context budget, or sensitive output matters.

## Progressive loading

Load only the branch-specific resource needed:

- `references/coding-discipline.md`: semantic-change boundary, simplicity, archaeology, escalation, and surgical edits.
- `references/decision-variance-model.md`: mechanical/heuristic/judgment/subjective control and anti-overcontrol rules.
- `references/context-and-evidence-policy.md`: context selection, repository-native tooling, history, evidence labels, external sources, and secrets.
- `references/response-contracts.md`: response shapes and severity rules.
- `references/validation-and-stop-conditions.md`: failure-model validation, action risk, blockers, security escalation, and closure reporting.
- `references/activation-scenarios.md`: human-readable activation boundary review.
- `evals/activation-boundary-scenarios.json`: canonical planned activation/regression suite.
- `evals/decision-variance-scenarios.json`: planned decision-control regression suite.
- `evals/engineering-discipline-scenarios.json`: planned research-derived semantic-scope, validation, risk, tooling, and escalation suite.
- `assets/templates/implementation-response.md.template` or `assets/templates/code-review-response.md.template`: optional response skeletons.
- `scripts/validate_contract.py` and `scripts/validate_decision_variance.py`: deterministic package contract checks after edits.

## Output contracts

Keep answers proportional. For implementation, bug fix, refactor, and test design, return correctness-affecting assumptions only when needed, the minimal change, validation evidence, and material residual risk. For review/risk audit, use severity only for evidence-backed defects or risks and keep recommendations/judgment/style separate. For non-trivial plans, give ordered steps with a verification criterion per material step.

Detailed response shapes live in `references/response-contracts.md`; do not duplicate them here.

## Validation checklist

Before finalizing coding work, verify:

- proposed changes map to the request and the semantic change boundary;
- important preserved invariants were not silently changed;
- validation matches the failure model and does not overclaim from a weaker oracle;
- added process/complexity is justified by current evidence or risk;
- decision controls remain at the lowest reliable layer;
- unrelated cleanup, speculative abstractions, dependencies, or configurability were not added;
- evidence is labeled truthfully and secrets are not introduced, repeated, or logged;
- destructive/external actions have the required authority and recovery posture.

## Stop Conditions

Stop, narrow, or report a blocker when:

- available context cannot support a safe change;
- a broad rewrite is requested but evidence supports only a localized slice;
- verification requires unavailable credentials, systems, data, or tools and the missing evidence is material;
- performance, security, reliability, or production-readiness conclusions are requested without the evidence needed to support them;
- destructive, production, or irreversible action lacks explicit authority or a credible recovery path;
- a stricter domain-specific workflow conflicts with these guidelines. Follow the stricter workflow and keep this skill secondary.

## Supporting references

The canonical support map is the `Progressive loading` section above; branch detail remains in package-local references rather than duplicated in the root.

## Package maintenance

When editing this skill package:

1. mutate only `karpathy-guidelines`; keep branch detail in lazy-loaded resources;
2. resolve `<PYTHON>` from host capabilities and keep the semantic core vendor-neutral;
3. run `<PYTHON> -S scripts/validate_contract.py <skill-folder>`, `<PYTHON> -S scripts/validate_decision_variance.py <skill-folder>`, and after packager edits `<PYTHON> -S scripts/test_package_skill.py <skill-folder>`;
4. package only a frozen passing candidate with `<PYTHON> -S scripts/package_skill.py --target <skill-folder> --output <output-dir>/skill.zip --validate`;
5. preserve last-good output on failure and report only artifacts that actually passed their gates.
