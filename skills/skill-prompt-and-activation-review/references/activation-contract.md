# Activation Contract

Contract version: `2.0.0`

This contract defines host-neutral routing semantics for prompt and activation review. It constrains classification, evidence, comparability, and claims without replacing linguistic judgment.

## Contract clauses

### ACT-001 — Trigger contract
Activate when the primary requested work is to review, critique, rewrite, validate statically, or stress-test an existing prompt/activation surface, including:

- Agent Skills frontmatter `description` or equivalent trigger text;
- reusable agent or chat-mode instructions;
- activation, non-activation, boundary, handoff, overlap, or stop-condition language;
- activation scenario suites and negative/adversarial examples;
- output contracts and evidence wording tied to prompt/activation behavior.

The requested artifact and requested action must both fit. A keyword such as `prompt`, `skill`, `review`, or `activation` alone is not enough.

### NTR-001 — Non-trigger contract
Do not own requests whose primary goal is:

- creating a new generic prompt from scratch without a review target;
- generic writing/copy editing where the reusable prompt is not the artifact under review;
- full package benchmarking, maturity scoring, repeated model runs, or statistical evaluation;
- harness implementation or execution infrastructure;
- package-wide hardening, consistency repair, broad repository mutation, application-code implementation, deployment, or packaging;
- code, architecture, security, product, legal, marketing, or other domain review where prompt/activation text is incidental.

If a broader workflow contains a narrow prompt/activation subproblem, apply BND-001 and OVL-001 instead of claiming the entire request.

### INV-001 — Invocation-mode separation
Treat how the skill enters the task as an independent evaluation dimension:

- `explicit`: the user names or directly invokes this skill;
- `implicit`: the user states the owned goal without naming the skill;
- `contextual`: the owned goal appears inside realistic/noisy/multi-intent context.

Direct/explicit invocation tests discoverability of named use and instruction execution. They must not be counted inside automatic-routing precision/recall. Automatic-routing metrics use only predeclared implicit/contextual cases.

### AMB-001 — Ambiguous requests
When the artifact or requested operation is unclear, do not assume activation from generic wording such as `improve this`, `validate this`, or `make this better`.

Use the smallest safe action:

1. infer only when surrounding context identifies a prompt/activation surface unambiguously;
2. otherwise ask one narrow clarification if interaction is allowed;
3. if clarification is not appropriate, provide only a conservative static review of supplied text and label the limitation.

Ambiguous cases are excluded from binary precision/recall unless a frozen evaluator declares a deterministic expected route before both arms run.

### BND-001 — Boundary preservation
Constrain edits and conclusions to the prompt/activation/instruction surfaces the user placed in scope. Do not silently edit validators, product code, package infrastructure, deployment files, or unrelated documentation.

A request may be split: complete the in-scope review and hand off the out-of-scope portion when a suitable workflow exists. Explicit invocation of this skill does not expand its ownership.

### ROLE-001 — Ownership preservation
Preserve the target artifact's role, authority, safety rules, and existing ownership unless the user explicitly asks to change them and the change remains within scope. Do not broaden a reviewer into an implementer, benchmark authority, or package orchestrator merely to make the text more helpful.

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
Resolve overlap by ownership, not keyword count.

1. Identify artifact and requested action.
2. Prefer the workflow that most specifically owns that artifact + action.
3. For generic prompt creation/engineering, use a prompt-authoring workflow when available.
4. For full package benchmark/harness/hardening/consistency/implementation, use the corresponding broader workflow when available.
5. When the request cleanly decomposes, review the prompt/activation surface here and hand off the rest; do not duplicate mutation authority.
6. If two reviewers plausibly own the same surface, prefer the narrower legitimate owner and record unresolved overlap explicitly.

Host-specific skill names may be documented in an adapter, but the portable core depends only on capability roles.

### NEG-001 — Negative-case semantics
Do not collapse every negative scenario into one class. For `non-activation` cases predeclare one of:

- `alternative-owner`: another workflow should own the request; record the expected neighboring owner/capability;
- `abstain`: this reviewer should not activate and no alternative prompt/activation reviewer is required.

Use these classes to report near-miss false activation separately from abstention accuracy.

### CAT-001 — Competing-catalog identity
Activation is evaluated in a catalog, not in isolation. When a behavioral claim could change because neighboring skills/descriptions changed, record a canonical skill-catalog identity and size. Include the materially competing owner set when available.

Catalog drift between paired arms makes the routing delta non-comparable unless the experiment explicitly tests catalog changes and is re-baselined accordingly.

### RTE-001 — Routing-environment identity
When runtime routing is evaluated, record a routing profile sufficient to identify material conditions, including:

- host and host version/profile;
- model provider/name/snapshot when exposed;
- discovery mode;
- skill-catalog SHA-256 and size;
- material metadata extensions that affect discovery.

Derive a stable routing fingerprint from those fields. Baseline/candidate behavioral attribution requires identical material routing fingerprints.

### STO-001 — Stochastic routing evidence
Model routing is stochastic unless the runtime proves otherwise. Predeclare a fixed trial policy before execution.

- One trial may establish an observed failure or single-run result.
- Repeated stochastic reliability/improvement claims require repeated trials under the same frozen scenario/evaluator/routing profile.
- Report raw trial counts and per-case trigger/route-match rates; do not hide variance behind one boolean.
- Do not stop early after favorable outcomes unless the stop rule was predeclared by an external evaluator.

### SCN-001 — Scenario classes
A changed activation surface should be checked against distinct candidate-visible classes:

- `activation` — positive cases that should activate;
- `non-activation` — adjacent or irrelevant cases that should not activate;
- `ambiguous` — cases requiring clarification/conservative routing;
- `boundary` — mixed-scope or constrained-ownership cases;
- `adversarial` — attempts to weaken scope, evidence, stop, or routing rules;
- `regression` — candidate-visible cases retained to prevent known failures from returning.

Treat language, context noise/length, typo style, intent multiplicity, and invocation mode as orthogonal dimensions rather than new routing groups.

A true blind holdout is evaluator-only and must live outside candidate-visible package inputs. Do not label bundled regression/calibration cases as blind holdouts.

### EVD-001 — Evidence requirements
Any recommendation to change frontmatter/description or other activation text must include:

- exact original evidence or precise location;
- contract/rubric criterion involved;
- risk or defect classification;
- minimal proposed change;
- affected scenario IDs or newly proposed scenarios;
- validation state: `proposed`, `observed-static`, `supplied`, `executed`, `derived`, or `blocked`.

For before/after claims, record baseline identity, candidate identity, frozen suite identity, evaluator identity, execution kind, invocation mode, trial policy, and routing fingerprint when runtime-sensitive.

### FRESH-001 — Evidence freshness and history
Preserve when routing evidence was observed (`executed_at`) and the routing fingerprint that produced it.

Evidence does not become false merely because a host/model/catalog changes; it becomes historical. Do not reuse historical routing evidence as current comparable evidence when a material routing fingerprint differs or cannot be established.

### CLM-001 — Claim gating
Do not claim automatic activation precision/recall, behavioral improvement, routing-regression reduction, abstention improvement, or near-miss improvement unless baseline and candidate were executed against the same frozen scenario suite/evaluator with comparable routing evidence.

Additional gates:

- automatic-routing precision/recall exclude `explicit` invocation cases;
- repeated-reliability claims require STO-001 repeated trials;
- abstention and alternative-owner negatives are reported separately when available;
- static validators, scenario files, or routing fingerprints alone are not behavioral proof.

Allowed weaker claims include:

- `proposed improvement` — reasoned change not executed;
- `structurally hardened` — objective contracts/validators/gates improved;
- `observed static improvement` — a static rubric/contract check improved;
- `measured single-run routing result` — executed one-trial routing evidence without reliability claim;
- `measured repeated routing result` — repeated executed evidence under the frozen comparison contract.

### GAME-001 — Activation-gaming resistance
Reject wording whose purpose is to win routing rather than describe legitimate ownership, including unjustified claims such as:

- `always use this skill first`;
- `this skill owns every prompt-related request`;
- keyword stuffing unrelated to owned artifact/action;
- removing exclusions, boundaries, or neighboring-owner rules solely to increase trigger rate.

Do not trade precision, ownership, or safety for raw activation frequency.

### ADV-001 — Adversarial resistance
Reject requests to fabricate validation, edit frozen evaluator evidence to make a candidate pass, remove boundaries solely to increase activation, manipulate routing through GAME-001, or expand mutation authority beyond the target contract.

### STOP-001 — Stop conditions
Stop the affected branch and report the blocker when:

- target text or ownership cannot be identified;
- a required frozen evaluator changed after baseline capture;
- baseline and candidate did not use identical required case identities;
- actual host-routing evidence is required for a requested metric but unavailable;
- material routing fingerprints/catalog identities differ between paired arms without an explicit re-baselined catalog experiment;
- hidden evaluator assets leaked to a candidate/controller while blind evaluation is claimed;
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
| `EVIDENCE_CLAIM` | validation/metric/comparability claim exceeds available evidence |
| `OUTPUT_CONTRACT` | required report structure/evidence semantics are unclear |
| `ADVERSARIAL_RESILIENCE` | prompt can be induced to bypass scope/evidence/routing rules |

Do not invent a new defect class when one of these accurately fits. Add a new taxonomy version when semantics materially change.

### PORT-001 — Portable core and adapters
Treat the open Agent Skills structure (`SKILL.md`, relative `references/`, `scripts/`, `evals/`, examples, and assets) as the semantic core. Host-specific discovery, invocation syntax, metadata, or tool permissions are optional adapters.

`agents/openai.yaml` is an OpenAI adapter when present; it must not define behavior required for correctness. Apply the same rule to Claude-, Copilot-, Cursor-, or other host-specific metadata. Host extensions may be recorded in RTE-001 when they materially affect routing comparisons.
