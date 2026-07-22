# Review Scenarios

## Scenario 1: Activation text hides the real trigger

**Observed package**

- Frontmatter says the skill "helps with documents".
- The body supports only legal memorandum review.
- Non-activation cases are absent.

**Calibrated result**

- 🟠 `MAJOR`, confirmed activation defect.
- Impact: broad false positives and missing common legal-review terms.
- Smallest fix: narrow the description to legal memorandum artifacts and add adjacent document exclusions.
- Do not recommend a package redesign unless other evidence shows mixed ownership.

## Scenario 2: Unreferenced example file

**Observed package**

- `examples/legacy-output.md` is not linked from `SKILL.md`.
- No script consumes it.
- Its content may still be intentionally retained for maintainers.

**Calibrated result**

- Start as 🟣 `QUESTION`, not a confirmed orphan defect.
- Confirm whether it is intentionally retained or stale.
- Upgrade to 🟡 `MINOR` only when its stale instructions can mislead maintenance or packaging.

## Scenario 3: Validator proves less than the report claims

**Observed package**

- A script validates JSON schema and file existence.
- The skill claims 100% activation accuracy and production readiness.
- No live or supplied behavioral evaluation exists.

**Calibrated result**

- 🟠 `MAJOR`, confirmed evidence-discipline defect.
- The validator may remain useful; the defect is the unsupported claim.
- Smallest fix: relabel results as structural coverage and add planned or executed behavioral evaluation before metrics.

## Scenario 4: Large but cohesive skill

**Observed package**

- `SKILL.md` is long but owns one regulated workflow.
- Modes share inputs, vocabulary, validators, outputs, and owner.
- Detailed tables are already in references.

**Calibrated result**

- Do not penalize size alone.
- Record a token-efficiency finding only when duplication, branch pollution, or context competition has evidence.

## Scenario 5: Security request

**User request**

"Audit this skill for exposed secrets and unsafe shell commands."

**Calibrated result**

- Do not activate this skill as the primary reviewer.
- Route to a dedicated security-and-governance or secure-code-review skill.
- This skill may later validate the quality of that review report, but it does not own the security judgment.
