# Activation Review Rubric

Use this rubric for `activation-description-review`, `boundary-review`, `output-contract-review`, and any review that touches trigger behavior.

## 1. Activation Description Checks

A strong activation description lets the model decide whether to load the skill without reading `SKILL.md` body content.

Check for:

- **artifact type:** names the target artifact: Skill, agent, prompt, frontmatter description, chat mode, reusable instruction, output contract, scenario suite, or stop condition.
- **action verbs:** uses review, improve, rewrite, validate, stress-test, clarify, or produce scenarios.
- **trigger specificity:** includes common user phrasings and artifact names without becoming a generic prompt-writing skill.
- **scope boundary:** excludes full benchmark, hardening, consistency repair, repository implementation, and broad package mutation.
- **handoff signal:** says when another workflow owns the work.
- **no tool dependency:** does not require MCP or a specific external server.
- **lowercase frontmatter style:** when reviewing ChatGPT Skill frontmatter, preserve lowercase description conventions unless the target platform requires otherwise.

## 2. False Positive Review

Flag a false-positive risk when the description would activate for:

- generic writing improvement not related to prompts, Skills, agents, or reusable instructions;
- code review or architecture review where prompt/activation text is not the target;
- benchmark, scorecard, maturity audit, or measured comparison requests;
- broad package hardening or consistency repair;
- implementation tasks outside the prompt or Skill package;
- social, email, product, legal, or marketing writing tasks that merely use the word "prompt" informally.

## 3. False Negative Review

Flag a false-negative risk when the description omits likely valid triggers, such as:

- `frontmatter description`, `description`, `activation`, `trigger`, `when to use`, `boundaries`, `non-goals`, `handoff`, `stop conditions`;
- `output contract`, `report format`, `expected output`, `success criteria`;
- `agent instructions`, `chat mode`, `system prompt`, `copilot prompt`, `reusable instructions`;
- `negative examples`, `activation scenarios`, `non-activation`, `edge cases`, `adversarial prompts`.

## 4. Boundary and Ownership Checks

Review whether the target clearly states:

- what it owns;
- what it does not own;
- which artifacts it may edit;
- which artifacts are read-only evidence;
- when to stop;
- which workflow should take over when the request expands.

Ownership risk examples:

- a reviewer Skill that starts claiming benchmark authority;
- a prompt rewrite agent that edits application code;
- an activation reviewer that removes stop conditions to sound more helpful;
- a hardening workflow that edits scenario expected outputs to pass.

## 5. Output Contract Checks

An output contract is reviewable when it defines:

- required sections;
- severity scale;
- evidence or rationale expectations;
- what counts as measured evidence;
- how to mark unverified or proposed scenarios;
- residual risks and limitations;
- handoff or stop-condition reporting.

Flag output contract risk when:

- the output asks for a score but no evidence source exists;
- severity is named but not defined;
- findings do not require rationale;
- the format mixes critique, rewrite, and validation claims without separating them;
- the contract permits fabricated metrics, unverifiable pass/fail claims, or silent scope changes.

## 6. Severity Guidance

- **blocking:** current text can cause unsafe scope expansion, fabricated validation, wrong workflow ownership, or severe activation confusion.
- **high:** likely false positives/false negatives, contradictory rules, missing stop conditions, or unclear output evidence.
- **medium:** ambiguity that can cause inconsistent results but has a local fix.
- **low:** style, redundancy, mild wording, or missing helpful examples.
- **note:** observation with no required change.

## 7. Review Output Shape

For each finding, include:

- `id`
- `risk_type`: textual_clarity, activation_risk, ownership_risk, or output_contract_risk
- `severity`
- `evidence`
- `issue`
- `proposed_change`
- `rationale`
- `validation_needed`: none, static review, scenario review, harness, benchmark, or human decision
