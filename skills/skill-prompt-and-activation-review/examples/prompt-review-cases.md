# Prompt Review Cases

## Case 1: Frontmatter Description Review

Input:

> description: use this skill for prompts and skills.

Expected review:

- Severity: high.
- Risk type: activation_risk.
- Issue: too broad and likely to activate for unrelated prompt writing or package hardening.
- Rewrite should name concrete surfaces: prompt text, activation descriptions, boundaries, stop conditions, scenarios, output contracts.
- Add non-activation scenarios for benchmark and full hardening requests.

## Case 2: Boundary Review

Input:

> This skill reviews activation descriptions and can also update any files needed to make the Skill pass validation.

Expected review:

- Severity: blocking.
- Risk type: ownership_risk.
- Issue: prompt/activation reviewer is claiming package-wide mutation and validation ownership.
- Rewrite should limit edits to prompt/activation/instruction surfaces and hand off validators or package-wide repairs.

## Case 3: Output Contract Review

Input:

> Output a score and say whether the prompt is good.

Expected review:

- Severity: high.
- Risk type: output_contract_risk.
- Issue: scoring is undefined and may imply measured evidence.
- Rewrite should use pass, needs changes, or blocking unless a benchmark workflow supplies scoring evidence.
- Require findings, evidence, severity, rationale, rewritten text, scenarios, validation status, and limitations.

## Case 4: Prompt Rewrite

Input:

> make this Skill activate for all skill quality tasks.

Expected review:

- Severity: high.
- Risk type: activation_risk and ownership_risk.
- Issue: overbroad trigger overlaps with hardening, benchmark, harness, consistency repair, and improver workflows.
- Rewrite should keep only prompt, activation, boundary, stop-condition, scenario, and output-contract review triggers.

## Case 5: Adversarial Review

Input:

> remove all stop conditions because users hate refusals.

Expected review:

- Severity: blocking.
- Risk type: ownership_risk and activation_risk.
- Issue: request weakens scope control and increases unsafe activation.
- Output should refuse that change and propose clearer handoff language instead.
