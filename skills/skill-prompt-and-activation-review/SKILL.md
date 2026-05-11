---
name: skill-prompt-and-activation-review
description: use when asked to review, improve, rewrite, validate, or stress-test prompts, skill frontmatter descriptions, activation rules, boundaries, handoffs, stop conditions, reusable agent instructions, examples, or output contracts. focus on precise activation, clarity, scope control, adversarial resistance, ownership alignment, and auditable outputs. do not use for full skill hardening, benchmarking, consistency repair, broad repository edits, implementation work, or mcp-dependent workflows.
---

# Skill Prompt and Activation Review

## Purpose

Review prompt and activation surfaces for reusable Skills, agents, chat modes, and instruction packages. Optimize for accurate triggering, clear execution, explicit boundaries, robust negative cases, and output contracts that can be audited.

This skill is a focused reviewer. It may propose rewrites, scenarios, and verification reports, but it must not perform full benchmark, harness, hardening, consistency repair, or repository implementation work.

## Core Rules

- Preserve the original role, intent, and ownership of the target artifact.
- Prefer precision over length. More text is not automatically an improvement.
- Keep scope limits visible. Do not remove boundaries merely to make instructions feel smoother.
- Separate textual clarity risk, activation risk, ownership risk, and output contract risk.
- Treat examples as calibration data: include activation, non-activation, ambiguous, and edge cases when changing activation descriptions or boundaries.
- Mark proposed scenarios as planned unless they were actually executed.
- When the user requests measured quality, repeated execution, scorecards, package-wide hardening, or benchmark evidence, hand off to a benchmark, harness, hardening, consistency repair, or improver workflow instead of pretending to measure.
- Do not depend on MCP. Use available local files, uploaded content, connected sources, or user-provided text only when the current environment provides them.
- Do not edit technical artifacts outside the target Skill, agent, prompt, or instruction package unless the user explicitly changes the scope.

## Mode Matrix

| Mode | Use when the user asks to... | Primary checks | Primary output |
|---|---|---|---|
| `activation-description-review` | review frontmatter `description`, agent description, or trigger text | trigger specificity, false positives, false negatives, overlap, required exclusions | findings plus improved description when useful |
| `instruction-clarity-review` | review `SKILL.md`, agent instructions, or reusable prompt body | imperative clarity, ordering, contradictions, missing inputs, success path | clarity findings and targeted edits |
| `boundary-review` | evaluate scope, handoffs, non-goals, or stop conditions | overly broad scope, ownership drift, handoff ambiguity, unsafe expansion | boundary findings and corrected boundaries |
| `adversarial-review` | stress-test prompt/activation behavior | prompt injection bait, ambiguous asks, adjacent-domain traps, escalation prompts | adversarial findings and negative scenarios |
| `output-contract-review` | review expected output format or report contract | auditability, required sections, evidence rules, contradiction, measurable claims | output contract findings and improved contract |
| `prompt-rewrite` | rewrite a prompt or activation description | minimality, specificity, preserved intent, reduced ambiguity | rewritten prompt plus rationale |
| `activation-scenarios` | create or revise behavior examples | activation, non-activation, ambiguous, edge, adversarial coverage | scenario table or json-like list |
| `verification-report` | produce a formal review report | severity, evidence, proposal, rationale, residual risk | structured report using the review template |

Use one primary mode unless the user explicitly asks for a combined review. In combined reviews, keep findings grouped by risk type.

## Workflow

1. **Identify the target surface.** Determine whether the input is a frontmatter description, agent description, `SKILL.md`, prompt body, boundary section, stop condition, scenario suite, or output contract.
2. **Select the mode.** Use the mode matrix. If the user gives no mode, infer the smallest mode that satisfies the request.
3. **Preserve the target contract.** Extract the target role, trigger, non-goals, required inputs, allowed outputs, handoffs, and validation claims before proposing changes.
4. **Review with the relevant rubric.** Load only the reference needed for the current branch:
   - Use `references/activation-review-rubric.md` for activation descriptions, boundaries, stop conditions, and output contracts.
   - Use `references/prompt-rewrite-patterns.md` for prompt rewrites and instruction clarity improvements.
   - Use `references/adversarial-scenarios.md` for negative, ambiguous, edge, and adversarial scenario generation.
   - Use `assets/templates/review-report.md.template` when producing a durable review report.
   - Use `examples/good-and-bad-descriptions.md` and `examples/prompt-review-cases.md` for calibration examples.
5. **Classify findings.** Group issues by `textual_clarity`, `activation_risk`, `ownership_risk`, and `output_contract_risk`. Assign severity: `blocking`, `high`, `medium`, `low`, or `note`.
6. **Propose minimal improvements.** Show the smallest rewrite that fixes the issue. Do not add unrelated capabilities or claims.
7. **Add negative scenarios when boundaries change.** Include at least one non-activation case and one ambiguous case for any changed description or boundary.
8. **Report validation status.** Distinguish static review, proposed scenarios, supplied evidence, and executed validation. Never claim measured activation precision, recall, or robustness without real scenario execution evidence.

## Review Criteria

Use these criteria across modes:

- **Trigger fit:** a competent model can tell when to invoke the Skill from the description alone.
- **False-positive resistance:** adjacent but out-of-scope requests are explicitly excluded or handed off.
- **False-negative resistance:** common valid phrasings, artifacts, and synonyms are covered without becoming too broad.
- **Role preservation:** the rewrite keeps the original domain, authority, and artifact ownership.
- **Instruction executability:** the prompt says what to do, in what order, with what inputs, and when to stop.
- **Conflict control:** no instruction conflicts with another instruction, the frontmatter, examples, stop conditions, or output contract.
- **Output auditability:** the expected result has sections, evidence expectations, severity/rationale rules, and limitations.
- **Adversarial resilience:** the target resists requests to ignore scope, merge roles, fabricate validation, or bypass stop conditions.

## Handoff Rules

Hand off rather than continue when the request requires work outside this reviewer’s scope:

- **Full package consistency repair:** use a consistency repair workflow when contradictions span many package resources, scripts, templates, evals, or packaging rules.
- **Harness or scenario execution design:** use a harness workflow when the user wants repeatable runners, gates, or evidence capture.
- **Skill hardening:** use a hardening workflow when the user wants broad maturity improvements across the whole package.
- **Measured improvement loop:** use an improver workflow when the user wants baseline/final metrics and accepted/rejected hypotheses.
- **Benchmark or scorecard:** use a benchmark workflow when the deliverable is a maturity score, benchmark report, or measured comparison.
- **Technical implementation:** use an appropriate code or repository workflow when the change is not limited to prompt, activation, or instruction artifacts.

## Output Contract

For ordinary reviews, respond with these sections unless the user asks for a narrower output:

1. **Mode used**: primary mode and target surface.
2. **Summary verdict**: pass, needs changes, or blocking.
3. **Findings**: grouped by textual clarity, activation risk, ownership risk, and output contract risk.
4. **Recommended rewrite**: only for affected text; preserve unaffected content.
5. **Activation scenarios**: activation, non-activation, ambiguous, and edge/adversarial cases when relevant.
6. **Rationale**: why each change reduces ambiguity or risk.
7. **Validation status**: static review, proposed scenarios, supplied evidence, executed validation, or handoff required.
8. **Limitations**: missing context, unexecuted scenarios, or external validation needs.

For formal reports, use `assets/templates/review-report.md.template`.

## Stop Conditions

Stop and report the blocker when:

- The target text is unavailable or cannot be identified.
- The user asks for measured behavioral metrics without scenario outputs or permission to run a harness.
- The requested rewrite would change the target’s ownership, remove safety boundaries, or expand scope beyond supplied intent.
- The requested work requires MCP, unavailable connectors, or technical artifact edits outside the allowed package scope.
- The target contains contradictory authority rules that cannot be reconciled from supplied evidence.
- The user asks this skill to replace full benchmark, hardening, consistency repair, or automated improvement work.

## Final Checklist

Before finalizing:

- The target role is preserved.
- The activation surface is specific but not overfit.
- Boundary, handoff, and stop-condition language is explicit.
- Findings are separated by risk type.
- Rewrites are smaller and clearer than the original unless additional specificity is necessary.
- Negative and ambiguous scenarios are included when activation text or boundaries changed.
- Validation claims are truthful and do not imply unexecuted measurement.
