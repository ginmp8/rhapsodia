---
name: skill-change-gate
description: evaluate proposed changes to existing Agent Skills-compatible packages across ChatGPT/OpenAI, Claude, GitHub Copilot, Cursor, Codex, and similar hosts before acceptance. use for diffs, before/after folders, benchmark or search candidates, hardening patches, and package updates when acceptance must detect regressions in activation, Top-100/context loading, scope, authority, safety, portability, evidence identity, evaluator exposure, policy/verifier identity, freshness, validation, consumer compatibility, packaging, recovery, waivers, or receipt integrity. do not use for broad repair loops, benchmark scoring, new skill creation, or generic application-code review.
---

# Skill Change Gate

## Mission

Decide whether one proposed change to an existing skill package can be accepted without quality regression. Remain a stateless, read-only gate: inspect candidate-bound evidence, classify regressions, and return `pass`, `pass-with-warnings`, `fail`, or `insufficient-evidence`.

Do not mutate the target unless the user separately authorizes an implementation pass. Benchmark scoring, hypothesis selection, broad repair, candidate ranking, and promotion execution remain caller-owned.

## Activation and Routing

Use this skill when there is an existing skill candidate, diff, patch summary, before/after pair, experiment/search candidate, or package update that needs an accept/reject decision.

Gate these surfaces when material: activation/routing, Top-100 control-plane quality, scope/authority, local references, safety, portability, evidence identity and exposure, validation claims, consumer compatibility, packaging/recovery, waivers, and delivery receipts.

Do not use for net-new skill creation, iterative repair, generic repository/code review, evaluator tuning, benchmark scoring, or unsupported improvement claims. A gate finding may recommend repair, but this skill does not perform it.

## Modes

| Mode | Use when | Primary result |
|---|---|---|
| `candidate-gate` | changed candidate/diff exists | acceptance decision with regressions |
| `preflight-gate` | required evidence must be known before patching | evidence checklist/blockers |
| `post-validation-gate` | validators/benchmark already ran | interpretation of supplied evidence |
| `advisory-review` | caller requests non-blocking review | warnings/follow-up hypotheses |

Default to `candidate-gate` when a changed package, diff, or hypothesis is present. Default policy is `normal`; use `strict` for automated/self-improvement loops and `advisory` only when the caller explicitly wants non-blocking guidance.

## Top-100 Context-Loading Gate

Treat context loading as an acceptance surface, separate from task outcome. For any candidate `SKILL.md` longer than 100 physical lines, the first 100 must expose enough control-plane knowledge to begin correctly:

1. purpose/scope and discriminative activation or routing boundary;
2. mode/branch selection when materially different paths exist;
3. workflow/quick-start sufficient to start the task safely;
4. critical rules, invariants, guardrails, or decision conditions;
5. direct pointers to branch-specific supporting resources;
6. no contradiction between the first 100 lines and deeper instructions.

For editable supporting `.md` files over 100 lines, require an early `At a Glance`/summary plus a `Contents`/section map within the first 40 lines, unless an explicit generated/vendor/unsafe-to-rewrite exception is recorded. The map must reflect the document's real material `##` headings.

Prefer one-level discovery: `SKILL.md -> supporting file`. A Markdown-to-Markdown chain may aid navigation, but must not be the only route to required instructions. Treat Top-100/preview failures as `portable-package-policy`, not as claims about the Agent Skills specification.

## Core Gate Invariants

- Missing, stale, blocked, contaminated, or candidate-mismatched required evidence is never a pass.
- A better benchmark score never overrides a blocking regression.
- Static success does not prove semantic safety, runtime behavior, behavioral improvement, holdout validity, or ecosystem compatibility.
- Expected identity mismatch is blocking; never refresh an expected hash after seeing the mismatch merely to pass.
- Frozen evaluator/protected-evidence mutation invalidates a measured experiment unless the experiment is explicitly restarted.
- Byte-identical holdouts can still be contaminated by candidate-generation or selection exposure.
- Artifact/promotion receipts must bind to the exact gated candidate bytes.
- Under `strict`, unresolved material concerns fail unless validly waived; non-waivable classes always fail.
- `ecosystem-safe` requires complete known-consumer inventory plus compatible evidence for every known consumer.
- Host-specific adapters are allowed; host-private semantic-core dependencies are portability regressions under a portable requirement.
- Do not convert findings into edits unless implementation is separately authorized.

## Workflow at a Glance

1. Resolve one target, candidate evidence, caller context, policy, claim scope (`local-acceptance`, `promotion`, `ecosystem-safe`), portability profile, and runtime capabilities.
2. Establish the identities that matter: baseline, optional direct parent, candidate, evaluator/scenarios, policy/verifier, destination/current state, artifact/receipt, and self-improvement/search provenance when supplied.
3. Bind strict/automated/promotion/waiver/authority-expansion/ecosystem decisions with Gate Context v1 when applicable; evidence for different bytes is not reusable acceptance evidence.
4. Check evidence sufficiency and freshness before interpreting results; return `insufficient-evidence` when acceptance cannot be justified.
5. Inventory touched surfaces, including Top-100/context loading, activation, authority, references, scripts, assets, evals/tests, validators, exported contracts, packaging, protected paths, host adapters, output contract, and recovery.
6. Run available mechanical gates with reports outside baseline/candidate roots; mechanical findings are evidence, not the final semantic decision.
7. Review semantically with the rubric; prefer stronger behavioral/current-state evidence over weak heuristics.
8. Classify each material finding by severity, `rule_origin`, and `regression_delta` (`introduced`, `worsened`, `preexisting-unchanged`, `improved`, `resolved`, `unknown`).
9. Decide for the requested claim scope; local acceptance never silently implies ecosystem-safe acceptance.
10. Report `accept`, `reject`, `repair-before-accept`, `gather-evidence`, or `advisory-only` with explicit missing/stale evidence.

## Direct Resource Map

- [`references/gate-rubric.md`](references/gate-rubric.md): severity, gate areas, Top-100/context-loading rules, and decision matrix.
- [`references/evidence-integrity.md`](references/evidence-integrity.md): identities, frozen evidence, receipts, aliases, recovery, durable evidence.
- [`references/decision-evidence-contract.md`](references/decision-evidence-contract.md): candidate binding, policy/verifier identity, exposure, stochastic sufficiency, freshness, authority, ecosystem claims.
- [`references/waiver-policy.md`](references/waiver-policy.md): waiver validity and non-waivable classes.
- [`references/host-portability.md`](references/host-portability.md): portable core and optional host adapters.
- [`references/integration-with-skill-improver.md`](references/integration-with-skill-improver.md): measured/self-improvement loops.
- [`references/capability-preservation-and-parent-provenance.md`](references/capability-preservation-and-parent-provenance.md): capability state, regression attribution, parent/baseline distinction.
- [`references/search-candidate-gate.md`](references/search-candidate-gate.md): multi-candidate/evolution lineage and candidate-local gating.

## Portable Core

Treat the open Agent Skills format as the canonical semantic core. Keep gate behavior independent of a single host's private tools, absolute sandbox paths, discovery directories, or metadata extensions.

Detect capabilities first: readable filesystem, writable report/work area, Python 3.10+ or equivalent code execution, access to before/after bytes, and artifact/receipt access when delivery integrity is part of acceptance. Use `agents/openai.yaml` only as an optional OpenAI adapter; its presence must not be required for portable semantics.

## Required Inputs

Proceed with explicit assumptions when evidence is partial, but use `insufficient-evidence` when acceptance cannot be justified.

1. Target skill identity: folder, archive, root `SKILL.md`, inspected text, or package name.
2. Candidate evidence: diff, patch summary, changed files, before/after package, or declared hypothesis.
3. Caller context: manual patch, experiment candidate, hardening, cleanup, token-efficiency, search/evolution, or package update.
4. Acceptance policy: `strict`, `normal`, or `advisory`.
5. Supporting evidence: validator output, benchmark/scenario results, command logs, reviewer notes, package receipt, or explicitly missing evidence.
6. Frozen identities when available: stable baseline, optional direct parent, candidate, evaluator/scenario inputs, policy/verifier, destination/current state, delivered artifact; for self-improvement include generation/controller/last-known-good provenance.
7. Protected paths or blocked artifacts when known.
8. Portability profile: default `portable`; use `openai` only when OpenAI adapter metadata is explicitly part of delivery acceptance.
9. Decision context when material: evaluator role/exposure, trial/replication contract, authority authorization, waivers, known consumers, and claim scope. Use Gate Context v1 for automated or strict measured gates.

## Resource Loading

Load only the branch-relevant files from the Direct Resource Map. Also use:

- `scripts/static_change_gate.py` for portable mechanical package/change checks when compatible execution is available;
- `contracts/gate-context.schema.json` + `scripts/validate_gate_context.py` for Gate Context v1;
- `contracts/change-gate-result.schema.json` + `scripts/validate_change_gate_result.py` for persisted/automated result validation;
- `contracts/integration-manifest.json` for owned peer-facing contracts;
- `scripts/validate_search_candidate_context.py` for current v3 search-candidate context;
- [`examples/usage-examples.md`](examples/usage-examples.md) for compact outcomes;
- [`evals/activation-scenarios.json`](evals/activation-scenarios.json) as planned activation/non-activation coverage only; never call it executed evidence until actually run.

## Detailed Mechanical Gate

Resolve `<PYTHON>` from the host and keep generated reports outside baseline/candidate roots.

```text
<PYTHON> scripts/static_change_gate.py \
  --target <AFTER> \
  --before <BEFORE> \
  --policy <normal|strict|advisory> \
  --profile <portable|openai> \
  --json <REPORT_OUTSIDE_TARGET>
```

For frozen experiments add applicable identity/protection controls:

```text
--expected-before-sha256 <BASELINE_TREE_HASH>
--expected-target-sha256 <FROZEN_CANDIDATE_TREE_HASH>
--protected-path evals/**
--protected-path <OTHER_PROTECTED_PATH>
--artifact-receipt <PACKAGE_RECEIPT_JSON>
--gate-context <GATE_CONTEXT_JSON>
```

Validate Gate Context separately when used, or pass it to the static helper when supported. Search candidates additionally validate the current search-candidate context before gating.

## Detailed Decision Rules

- The gate verifies the caller's trial/replication contract; it does not invent universal benchmark thresholds or statistical budgets.
- A destination/parent state change can make a prior decision stale; revalidate current state instead of treating the old pass as current.
- Under `strict`, material authority expansion requires explicit authorization evidence.
- Valid waivers are explicit and candidate/policy-bound. Identity drift, protected-evaluator mutation, receipt mismatch, unsafe path/secret exposure, fabricated evidence, contaminated holdout claims, and candidate self-authorization are non-waivable.
- In `advisory` policy, blocking regressions remain visible and still prevent unconditional accept.
- Pre-existing unchanged debt remains visible but is not falsely attributed to the candidate; policy may still independently block promotion on inherited critical debt.
- Search candidates are gated independently. Novelty, ranking, survivor selection, and generation continuation remain external.
- Top-100/context-loading signals require semantic interpretation: missing early control-plane knowledge is material by default and blocking when it makes required routing, authority, safety, or execution behavior unreachable/incorrect.

## Output Contract

Return the structure below for substantive human-facing gates. For machine consumers, emit an equivalent object conforming to `contracts/change-gate-result.schema.json`; validate persisted/automated results with `scripts/validate_change_gate_result.py`.

```markdown
## Skill Change Gate Result

- target:
- mode:
- policy:
- claim scope: local-acceptance | promotion | ecosystem-safe
- portability profile:
- status: pass | pass-with-warnings | fail | insufficient-evidence
- decision for caller: accept | reject | repair-before-accept | gather-evidence | advisory-only
- freshness: fresh | stale | not-applicable | unknown

### Evidence identities
- stable baseline tree:
- direct parent tree: `<same-as-baseline | identity | not-supplied>`
- candidate tree:
- policy identity:
- verifier identity:
- evaluator/scenario identity and role:
- evaluator exposure / holdout status:
- destination/current-state identity:
- artifact/receipt correspondence:
- transformation/search/self-improvement provenance: `<not-applicable | supplied values>`

### Evidence inspected
- target/candidate evidence:
- commands/results:
- required evidence binding/sufficiency:
- waivers:
- known-consumer evidence:
- runtime capabilities:
- missing/stale evidence:

### Capability preservation
| capability | classification | evidence | decision impact |
| ---------- | -------------- | -------- | --------------- |

### Findings
| severity | area | origin | regression delta | rule origin | finding | decision impact |
| -------- | ---- | ------ | ---------------- | ----------- | ------- | --------------- |

### Portability
- portable core:
- optional host adapters:
- host-specific dependencies:

### Accepted trade-offs, valid waivers, and false positives
-

### Required fixes or evidence before accept
-

### Follow-up hypotheses
-
```

Use concise entries. Never invent command results, hashes, benchmark scores, policy/verifier identities, consumer evidence, runtime support, or Top-100 compliance that was not inspected.

## Stop Conditions

Stop or return `insufficient-evidence` when:

- no target skill content or no candidate change/acceptance question is available;
- multiple root `SKILL.md` files exist and the intended target cannot be inferred;
- strict measured acceptance cannot verify required baseline/candidate/evaluator/policy identity;
- a required validator/benchmark/runtime capability is unavailable and its absence prevents a trustworthy decision;
- expected source/evaluator identity changed after freeze and the experiment was not explicitly restarted;
- required holdout evidence is contaminated and no fresh independent evidence exists;
- promotion depends on stale/unavailable destination/current-state identity;
- an `ecosystem-safe` claim has incomplete known-consumer evidence;
- the candidate touches blocked secrets, credentials, evaluator fixtures, expected outputs, benchmark baselines, generated evidence, repository metadata, old archives, or unrelated paths;
- archive inspection would require unsafe extraction/path handling outside available tools;
- the request requires edits but the active task is gate-only.

## Integration Defaults

For experiment loops, use `strict` for automated/self-improvement and `normal` for manual patches. Keep the gate stateless and portable: callers may supply hashes, manifests, validator results, package/promotion receipts, and provenance, but the skill must not require another installed skill to interpret them. Pairwise knowledge of the improvement-loop handoff is allowed; broad specialist discovery/orchestration is not.
