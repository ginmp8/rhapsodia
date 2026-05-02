# Response Contracts

Use this reference when a coding response needs stricter structure than a brief direct answer.

## Implementation, bug fix, refactor, and test design

Return this shape when the task changes or proposes code:

1. **Assumptions**: only correctness-affecting assumptions.
2. **Minimal change**: patch, code, or exact edit. Avoid broad rewrites.
3. **Validation evidence**: split executed checks from suggested checks.
4. **Residual risks**: only material risks that remain after the answer.

Use `../assets/templates/implementation-response.md.template` when a reusable skeleton helps, but remove empty sections in the final answer.

## Code review and risk audit

Rank findings by severity and evidence:

- Critical: likely security issue, data loss, financial/legal impact, or production outage.
- High: likely functional bug, broken compatibility, or severe operational risk.
- Medium: maintainability, performance, observability, or reliability concern with plausible impact.
- Low: style, naming, readability, or small cleanup that should not distract from the main change.

Use `../assets/templates/code-review-response.md.template` when a reusable skeleton helps. Do not inflate severity to make a review appear more useful.

Every finding should include:

- evidence from a visible artifact or measured output;
- concrete impact;
- the smallest fix or mitigation;
- a validation gap when the finding is plausible but not proven.

## Planning

For non-trivial plans, every step must have a verification criterion. Prefer sequence over breadth:

1. establish target behavior;
2. inspect or reproduce;
3. apply the smallest slice;
4. validate;
5. name remaining risks.

Do not turn a local coding question into a roadmap. Keep options only when a trade-off changes the implementation materially.

## Evidence language

Use precise closure labels:

- **Executed**: the command, test, inspection, or check was actually run in the current session.
- **Inspected**: the file, diff, config, or documentation was actually read in the current session.
- **Not executed**: the check was not run; include the exact command or observation that would verify it when useful.
- **Static reasoning**: no runtime check was available; name the files, functions, or constraints used for reasoning.
- **Unverified**: the claim is plausible but unsupported by available evidence.

Do not present a suggested check as completed evidence.
