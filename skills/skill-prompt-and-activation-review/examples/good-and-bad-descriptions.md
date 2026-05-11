# Good and Bad Activation Descriptions

## Example 1: Too broad

Bad:

> use when asked to improve skills.

Problems:

- Activates for full hardening, benchmark, consistency repair, and implementation requests.
- Does not name prompt, activation, boundary, or output-contract surfaces.
- Has high false-positive risk.

Better:

> use when asked to review, improve, rewrite, validate, or stress-test prompts, skill frontmatter descriptions, activation rules, boundaries, handoffs, stop conditions, reusable agent instructions, examples, or output contracts. focus on precise activation, clarity, scope control, adversarial resistance, ownership alignment, and auditable outputs. do not use for full skill hardening, benchmarking, consistency repair, broad repository edits, implementation work, or mcp-dependent workflows.

## Example 2: Too implementation-oriented

Bad:

> use this skill to fix skill packages, update scripts, edit examples, run tests, and package improved artifacts.

Problems:

- Claims package-level ownership.
- Overlaps with hardening, harness, consistency repair, and benchmark workflows.
- Makes prompt review look like implementation work.

Better:

> use this skill to review prompt, activation, boundary, stop-condition, scenario, and output-contract text inside a skill or reusable instruction package. propose focused rewrites and scenarios; hand off package-wide edits, validators, benchmarks, and packaging to the appropriate workflow.

## Example 3: Missing non-activation boundary

Bad:

> use when asked to validate a prompt.

Problems:

- Could imply measured validation without execution evidence.
- Does not distinguish static review from scenario execution.

Better:

> use when asked to statically review or rewrite a prompt and propose validation scenarios. if the user asks for measured prompt performance, repeated execution, scorecards, or evidence-backed benchmark results, hand off to a harness or benchmark workflow.

## Example 4: Good short form

Good:

> use when asked to review or rewrite skill activation descriptions, reusable prompt instructions, boundaries, stop conditions, scenarios, or output contracts for clarity, precise triggering, and scope control. do not use for full package hardening, benchmark scoring, repository implementation, or measured validation without scenario evidence.

Why it works:

- Names the target surfaces.
- Names quality goals.
- Excludes adjacent workflows.
- Avoids overclaiming validation.
