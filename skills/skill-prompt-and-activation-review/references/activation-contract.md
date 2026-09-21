# Activation Contract

Contract version: `1.0.0`

This contract defines host-neutral routing semantics for prompt and activation review. It constrains classification and evidence without replacing linguistic judgment.

## Contract clauses

### ACT-001 — Trigger contract
Activate when the primary requested work is to review, critique, rewrite, validate statically, or stress-test an existing prompt/activation surface, including:

- Agent Skills frontmatter `description` or equivalent trigger text;
- reusable agent or chat-mode instructions;
- activation, non-activation, boundary, handoff, overlap, or stop-condition language;
- activation scenario suites and negative/adversarial examples;
- output contracts and evidence wording tied to prompt/activation behavior.

The requested artifact and requested action must both fit. A keyword such as `prompt`, `skill`, or `activation` alone is not enough.

### NTR-001 — Non-trigger contract
Do not own requests whose primary goal is:

- creating a new generic prompt from scratch without a review target;
- generic writing/copy editing where the reusable prompt is not the artifact under review;
- full package benchmarking, maturity scoring, repeated model runs, or statistical evaluation;
- harness implementation or execution infrastructure;
- package-wide hardening, consistency repair, broad repository mutation, application-code implementation, deployment, or packaging;
- code, architecture, security, product, legal, marketing, or other domain review where prompt/activation text is incidental.

If a broader workflow contains a narrow prompt/activation subproblem, apply BND-001 and OVL-001 instead of claiming the entire request.

### AMB-001 — Ambiguous requests
When the artifact or requested operation is unclear, do not assume activation from generic wording such as `improve this`, `validate this`, or `make this better`.

Use the smallest safe action:

1. infer only when the surrounding context identifies a prompt/activation surface unambiguously;
2. otherwise ask one narrow clarification if interaction is allowed;
3. if clarification is not appropriate, provide only a conservative static review of the text actually supplied and label the limitation.

Ambiguous cases are excluded from binary precision/recall calculations unless a frozen evaluator declares a deterministic expected route.

### BND-001 — Boundary preservation
Constrain edits and conclusions to the prompt/activation/instruction surfaces the user placed in scope. Do not silently edit validators, product code, package infrastructure, deployment files, or unrelated documentation.

A request may be split: complete the in-scope review and hand off the out-of-scope portion when a suitable workflow exists. Explicit invocation of this skill does not expand its ownership.

### ROLE-001 — Ownership preservation
Preserve the target artifact's role, authority, safety rules, and existing ownership unless the user explicitly asks to change them and the change remains within scope. Do not broaden a reviewer into an implementer or benchmark authority merely to make the text more helpful.

### FP-001 — False-positive criterion
A false positive is confirmed only when all are true:

1. the frozen scenario says this skill should not be the primary owner;
2. actual executed routing evidence shows the skill activated as an owner rather than only being referenced/read as evidence;
3. no split-handoff rule in the frozen evaluator permits that activation.

Static wording that merely appears broad is a `false-positive risk`, not a confirmed false positive.

### FN-001 — False-negative criterion
A false negative is confirmed only when all are true:

1. the frozen scenario says this skill should activate;
2. actual executed routing evidence shows it did not activate or incorrectly handed off the owned work;
3. the scenario is not classified ambiguous/conditional by the frozen evaluator.

Static omissions are `false-negative risks`, not confirmed false negatives.

### OVL-001 — Skill/workflow overlap
Resolve overlap by ownership, not by keyword count.

1. Prefer the workflow that most specifically owns the requested artifact plus action.
2. For generic prompt creation/engineering, use a prompt-authoring workflow when available.
3. For full package benchmark/harness/hardening/consistency/implementation, use the corresponding broader workflow when available.
4. When the request cleanly decomposes, review the prompt/activation surface here and hand off the rest; do not duplicate mutation authority.
5. If two reviewers plausibly own the same surface, prefer the narrower contract and record the overlap as `ACTIVATION_OVERLAP` until resolved by explicit package policy.

Host-specific skill names may be documented in an adapter, but the portable core depends only on these capability roles.

### SCN-001 — Scenario classes
A changed activation surface must be checked against distinct scenario classes:

- `activation` — positive cases that should activate;
- `non-activation` — negative adjacent cases that should not activate;
- `ambiguous` — cases requiring clarification/conservative routing;
- `boundary` — mixed-scope or constrained-ownership cases;
- `adversarial` — attempts to weaken scope, evidence, or stop rules;
- `holdout` — cases reserved from candidate authoring when stronger robustness claims are desired; bundled seed cases are candidate-visible and cannot serve as blind holdouts by themselves.

Do not substitute many paraphrases of one easy case for distinct coverage.

### EVD-001 — Evidence requirements
Any recommendation to change frontmatter/description or other activation text must include:

- exact original evidence or a precise location;
- the contract/rubric criterion involved;
- the risk or defect classification;
- the minimal proposed change;
- affected scenario IDs or newly proposed scenarios;
- validation state: `proposed`, `observed-static`, `supplied`, `executed`, or `blocked`.

For before/after claims, record baseline identity, candidate identity, frozen suite identity, evaluator identity, and execution kind.

### CLM-001 — Claim gating
Do not claim `activation precision`, `activation recall`, `behavioral improvement`, or `regression reduction` unless baseline and candidate were executed against the same frozen scenario suite and frozen evaluator with host-routing evidence sufficient for the metric.

Allowed weaker claims include:

- `proposed improvement` — reasoned change not executed;
- `structurally hardened` — objective contracts/validators/gates improved;
- `observed static improvement` — a static rubric/contract check improved;
- `measured behavioral result` — only when the required executed evidence exists.

Do not convert a static score or scenario file into behavioral evidence.

### ADV-001 — Adversarial resistance
Reject requests to fabricate validation, edit frozen evaluator evidence to make a candidate pass, remove boundaries solely to increase activation, or expand mutation authority beyond the target contract.

### STOP-001 — Stop conditions
Stop the affected branch and report the blocker when:

- target text or ownership cannot be identified;
- a required frozen evaluator changed after baseline capture;
- baseline and candidate did not use identical case identities;
- actual host-routing evidence is required for a requested metric but unavailable;
- the requested change would weaken safety/ownership or require mutation outside scope;
- two ownership contracts conflict and available evidence cannot resolve precedence.

### TAX-001 — Stable defect taxonomy
Use these defect codes in review reports:

| Code | Meaning |
|---|---|
| `TEXTUAL_CLARITY` | wording/order creates avoidable ambiguity |
| `ACTIVATION_FALSE_POSITIVE_RISK` | static evidence suggests likely over-triggering |
| `ACTIVATION_FALSE_NEGATIVE_RISK` | static evidence suggests likely under-triggering |
| `ACTIVATION_FALSE_POSITIVE` | executed frozen scenario confirms over-triggering |
| `ACTIVATION_FALSE_NEGATIVE` | executed frozen scenario confirms under-triggering |
| `ACTIVATION_AMBIGUITY` | expected routing is underspecified or context-dependent |
| `ACTIVATION_OVERLAP` | multiple workflows plausibly claim the same artifact/action |
| `BOUNDARY_OWNERSHIP` | scope, handoff, or mutation authority is unsafe/unclear |
| `EVIDENCE_CLAIM` | validation/metric claim exceeds available evidence |
| `OUTPUT_CONTRACT` | required report structure/evidence semantics are unclear |
| `ADVERSARIAL_RESILIENCE` | prompt can be induced to bypass scope/evidence rules |

Do not invent a new defect class when one of these accurately fits. Add a new taxonomy version when semantics materially change.

### PORT-001 — Portable core and adapters
Treat the open Agent Skills structure (`SKILL.md`, relative `references/`, `scripts/`, `evals/`, and assets) as the semantic core. Host-specific discovery, invocation syntax, metadata, or tool permissions are optional adapters.

`agents/openai.yaml` is an OpenAI adapter when present; it must not define behavior required for correctness. Apply the same rule to Claude-, Copilot-, Cursor-, or other host-specific metadata.
