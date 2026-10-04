---
name: skill-change-gate
description: evaluate proposed changes to existing Agent Skills-compatible packages across ChatGPT/OpenAI, Claude, GitHub Copilot, Cursor, Codex, and similar hosts before acceptance. use for diffs, before/after folders, benchmark or search candidates, hardening patches, and package updates when acceptance must detect regressions in activation, scope, authority, safety, portability, evidence identity, evaluator exposure, policy/verifier identity, freshness, validation, consumer compatibility, packaging, recovery, waivers, or receipt integrity. do not use for broad repair loops, benchmark scoring, new skill creation, or generic application-code review.
---

# Skill Change Gate

## Mission

Decide whether a proposed change to an existing skill package can be accepted without quality regression. Act as a stateless gate: inspect evidence, classify regressions, and return `pass`, `pass-with-warnings`, `fail`, or `insufficient-evidence`.

Do not mutate the target skill unless the user separately asks for an implementation pass. Keep benchmark scoring, hypothesis selection, and broad repair owned by the caller.

## Portable core

Treat the open Agent Skills format as the canonical semantic core. Keep gate behavior independent of a single host's private tools, absolute sandbox paths, discovery directories, or metadata extensions.

When cross-host behavior matters, read [`references/host-portability.md`](references/host-portability.md). Detect capabilities first: readable filesystem, writable report/work area, Python 3.10+ or equivalent code execution, access to before/after bytes, and artifact/receipt access when delivery integrity is part of acceptance.

Use `agents/openai.yaml` only as an optional OpenAI adapter. Its presence must not be required for the portable core. Host-specific extensions on a target skill may be intentional; judge whether they are optional adapters or semantic dependencies.

## Scope

Use for:

- gating a candidate diff, patch summary, before/after folder pair, or changed skill package;
- deciding whether an experiment candidate may be accepted after benchmark/evaluator execution;
- reviewing manual edits for regressions in activation, boundaries, references, validation, packaging, safety, portability, or output contract;
- verifying frozen before/candidate identities and protected-path stability when supplied;
- checking that a package/delivery receipt corresponds to the candidate being gated;
- separating blocking regressions, material concerns, accepted trade-offs, false positives, and follow-up hypotheses;
- producing an auditable accept/reject decision consumable by another workflow.

Do not use for:

- creating a new skill package;
- running a broad repair loop or repeatedly fixing findings;
- claiming benchmark, precision, recall, robustness, or improvement scores without executed or supplied evidence;
- ordinary application-code review outside a skill package;
- editing evaluator fixtures, expected outputs, benchmark baselines, secrets, credentials, repository metadata, generated evidence, old archives, or unrelated files.

## Required inputs

Proceed with explicit assumptions when evidence is partial, but use `insufficient-evidence` when acceptance cannot be justified.

1. Target skill identity: folder, archive, root `SKILL.md`, inspected text, or package name.
2. Candidate evidence: diff, patch summary, changed files, before/after package, or declared hypothesis.
3. Caller context: manual patch, experiment candidate, hardening pass, cleanup pass, token-efficiency pass, or package update.
4. Acceptance policy: `strict`, `normal`, or `advisory`; default to `normal`, use `strict` for automated/self-improvement loops.
5. Supporting evidence: validator output, benchmark report, scenario results, command logs, reviewer notes, package receipt, or stated missing evidence.
6. Frozen identities when available: stable baseline tree, optional direct parent tree, candidate tree, evaluator/scenario inputs, delivered artifact. For self-improvement, also accept generation/controller/last-known-good identity and promotion-receipt correspondence from the caller.
7. Protected paths or blocked artifacts when known.
8. Portability profile: default `portable`; use `openai` only when OpenAI adapter metadata is explicitly part of delivery acceptance.
9. Decision context when material: exact policy/verifier identity, evaluator role/exposure, caller-declared trial/replication contract, destination freshness, authority authorization, waivers, and known-consumer evidence. Use Gate Context v1 for automated or strict measured gates.

## Modes

| Mode                   | Use when                                                            | Primary decision                     |
| ---------------------- | ------------------------------------------------------------------- | ------------------------------------ |
| `candidate-gate`       | a candidate change exists and must be accepted or rejected          | pass/fail decision with regressions  |
| `preflight-gate`       | a workflow needs required evidence before patching                  | evidence checklist and blockers      |
| `post-validation-gate` | validators/benchmark already ran and need structural interpretation | decision impact of supplied evidence |
| `advisory-review`      | non-blocking quality feedback only                                  | warnings and follow-up hypotheses    |

Default to `candidate-gate` when a changed package, diff, or hypothesis is present.

## Resource loading

Load only what the active gate needs:

- [`references/gate-rubric.md`](references/gate-rubric.md) for severity, gate areas, and decision rules.
- [`references/evidence-integrity.md`](references/evidence-integrity.md) when before/candidate identities, frozen evaluators, package receipts, output aliases, recovery, or durable receipts matter.
- [`references/decision-evidence-contract.md`](references/decision-evidence-contract.md) when evidence subject binding, policy/verifier identity, evaluator exposure, stochastic sufficiency, freshness, authority expansion, or ecosystem-safe claims matter.
- [`references/waiver-policy.md`](references/waiver-policy.md) when a caller proposes a waiver or accepted risk.
- [`references/host-portability.md`](references/host-portability.md) when cross-host compatibility or host-specific extensions matter.
- [`references/integration-with-skill-improver.md`](references/integration-with-skill-improver.md) for experiment/self-improvement loops.
- [`references/capability-preservation-and-parent-provenance.md`](references/capability-preservation-and-parent-provenance.md) when capability maps, transformation ids/change intent, or direct-parent attribution are supplied.
- [`references/search-candidate-gate.md`](references/search-candidate-gate.md) when the candidate belongs to a multi-candidate/evolution search and lineage/search provenance is supplied.
- `scripts/validate_search_candidate_context.py` validates the current v3 search candidate context before a search candidate is gated.
- `contracts/gate-context.schema.json` plus `scripts/validate_gate_context.py` define and validate Gate Context v1 without third-party dependencies.
- `contracts/change-gate-result.schema.json` plus `scripts/validate_change_gate_result.py` define the stable machine-readable result core.
- `contracts/integration-manifest.json` declares owned peer-facing contracts for ecosystem impact analysis.
- `scripts/static_change_gate.py` when a compatible Python runtime and filesystem access are available.
- [`examples/usage-examples.md`](examples/usage-examples.md) for compact outcome examples.
- [`evals/activation-scenarios.json`](evals/activation-scenarios.json) for planned activation/non-activation coverage; never call it executed evidence until actually run.

## Workflow

1. **Resolve target and runtime.** Identify one target skill, candidate evidence, caller context, policy, claim scope (`local-acceptance`, `promotion`, or `ecosystem-safe`), portability profile, available capabilities, and whether evidence is before/after, diff-only, or post-validation.
2. **Establish evidence identity.** Record baseline, optional direct parent, candidate, evaluator/scenario, policy, verifier, destination, and delivered-artifact identities that actually matter to the claim. In self-improvement also record generation/controller/last-known-good provenance and keep the gate outside the candidate mutation surface.
3. **Bind decision evidence when material.** For automated, strict measured, promotion, waiver, authority-expansion, or ecosystem-safe gates, use Gate Context v1 and validate it against the frozen candidate. Evidence for different candidate bytes is not reusable acceptance evidence. Treat holdout exposure, caller-declared trial/replication sufficiency, destination freshness, waiver validity, authority authorization, and consumer compatibility as independent checks.
4. **Check evidence sufficiency.** If target/candidate evidence or a required deciding identity cannot be established, return `insufficient-evidence`. A stale decision is not a current pass; revalidate against the current state. Partial evidence may support bounded findings, not unsupported claims.
5. **Inventory touched surfaces.** Map changes to activation, authority, `SKILL.md`, references, scripts, assets/templates, examples, evals/tests, validators, exported contracts/consumers, packaging, protected paths, host adapters, output contract, and delivery/recovery behavior. Malformed required frontmatter is blocking. Treat description-length changes and new executable surfaces as mechanical signals that trigger evidence review, not proof of regression by themselves.
6. **Run mechanical gates when available.** Resolve `<PYTHON>` from the host and keep reports outside baseline/candidate roots.

```text
<PYTHON> scripts/static_change_gate.py \
  --target <AFTER> \
  --before <BEFORE> \
  --policy <normal|strict|advisory> \
  --profile <portable|openai> \
  --json <REPORT_OUTSIDE_TARGET>
```

For frozen experiments add applicable identity/protection controls. When Gate Context is used, validate it separately or pass it to the static helper if the runtime supports the bundled integration.

```text
--expected-before-sha256 <BASELINE_TREE_HASH>
--expected-target-sha256 <FROZEN_CANDIDATE_TREE_HASH>
--protected-path evals/**
--protected-path <OTHER_PROTECTED_PATH>
--artifact-receipt <PACKAGE_RECEIPT_JSON>
--gate-context <GATE_CONTEXT_JSON>
```

7. **Review semantically.** Use the rubric to inspect activation intent, authority, safety, evidence discipline, validation truthfulness, output semantics, portability, consumer compatibility, and whether removed/changed resources still have valid owners/consumers. Do not let static heuristics override stronger behavioral evidence.
8. **Classify findings.** For every material finding record severity, `rule_origin`, and `regression_delta` (`introduced`, `worsened`, `preexisting-unchanged`, `improved`, `resolved`, or `unknown`). Keep pre-existing unchanged debt visible without falsely attributing it to the candidate. Search candidates are gated independently; novelty, ranking, and survivor selection remain external.
9. **Decide.** Blocking regressions fail. Under `strict`, unresolved material concerns fail unless covered by a valid waiver; non-waivable classes remain failures. `pass` requires sufficient applicable evidence, not merely a clean static report. A local pass does not imply an ecosystem-safe pass.
10. **Report for the caller.** State accept, reject, repair-before-accept, gather-evidence, or advisory-only. Keep measured improvement separate from quality acceptance, and keep stale/not-proven claim scopes explicit.

## Decision rules

- A better benchmark score never overrides a blocking regression.
- A clean static report does not prove semantic safety, runtime behavior, behavioral improvement, holdout validity, or ecosystem compatibility.
- Missing, stale, blocked, or candidate-mismatched required evidence is not a pass.
- Expected identity mismatch is blocking; never refresh an expected hash after observing the mismatch merely to pass.
- Mutation of frozen evaluator/protected evidence invalidates a measured experiment unless it is explicitly restarted.
- Byte-identical evaluators may still be contaminated when candidate construction or selection had access to holdout content/results.
- The gate verifies the caller's trial/replication contract; it does not invent benchmark thresholds or statistical budgets.
- A successful artifact/promotion receipt that points to different candidate bytes is blocking.
- A destination/parent state change can make a prior decision stale; revalidate instead of treating the old pass as current.
- Under `strict`, material authority expansion requires explicit authorization evidence.
- `ecosystem-safe` requires a complete known-consumer inventory and compatible evidence for every known consumer; local acceptance is a narrower claim.
- Valid waivers are explicit and candidate/policy-bound. Identity drift, protected-evaluator mutation, receipt mismatch, unsafe path/secret exposure, fabricated evidence, contaminated holdout claims, and candidate self-authorization are non-waivable.
- Host-specific adapters are acceptable; host-private core dependencies are portability concerns and fail under strict policy when unresolved.
- In `advisory` policy, blocking regressions remain visible and still prevent an unconditional accept decision.
- Do not convert gate findings into edits unless the user separately authorizes implementation.

## Output contract

Return the Markdown structure below for substantive human-facing gates. For machine consumers, emit an equivalent object conforming to `contracts/change-gate-result.schema.json`; validate it with `scripts/validate_change_gate_result.py` when the result is persisted or handed to automation.

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

Use concise entries. Never invent command results, hashes, benchmark scores, policy/verifier identities, consumer evidence, or runtime support.

## Stop conditions

Stop or return `insufficient-evidence` when:

- no target skill content is available;
- no candidate change, before/after comparison, or acceptance question is available;
- multiple root `SKILL.md` files exist and the intended target cannot be inferred;
- required before/candidate/evaluator identity cannot be verified for a strict measured experiment;
- a required validator/benchmark/runtime capability is unavailable and its absence prevents a trustworthy decision;
- expected source/evaluator identity changed after freeze and the experiment has not been explicitly restarted;
- a required holdout is contaminated by candidate/selection exposure and no fresh independent evidence exists;
- required destination/current-state identity is stale or unavailable for a promotion claim;
- an ecosystem-safe claim has an incomplete known-consumer inventory or unresolved consumer compatibility;
- the candidate touches blocked secrets, credentials, evaluator fixtures, expected outputs, benchmark baselines, generated evidence, repository metadata, old archives, or unrelated paths;
- archive inspection would require unsafe extraction or path traversal handling outside available tools;
- the request requires editing files but the current task is gate-only.

## Integration defaults

For experiment loops, use `strict` for automated/self-improvement and `normal` for manual patches. Keep the gate stateless and portable: callers may supply hashes, freeze manifests, validator results, package/promotion receipts, and generation provenance, but the skill must not require another installed skill to interpret them. Pairwise knowledge of the improvement-loop handoff is allowed; broad specialist discovery/orchestration is not.
