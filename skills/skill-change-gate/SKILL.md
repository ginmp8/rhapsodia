---
name: skill-change-gate
description: evaluate proposed changes to existing Agent Skills-compatible packages across ChatGPT/OpenAI, Claude, GitHub Copilot, Cursor, Codex, and similar hosts before acceptance. use when reviewing a diff, before/after skill folder, benchmark candidate, hardening patch, package update, or skill-improver hypothesis to detect blocking regressions in activation, scope, safety, portability, evidence identity, protected evaluators, validation, packaging, output-path safety, recovery, or receipt integrity. do not use for broad repair loops, benchmark scoring, new skill creation, or generic application-code review.
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

## Modes

| Mode | Use when | Primary decision |
|---|---|---|
| `candidate-gate` | a candidate change exists and must be accepted or rejected | pass/fail decision with regressions |
| `preflight-gate` | a workflow needs required evidence before patching | evidence checklist and blockers |
| `post-validation-gate` | validators/benchmark already ran and need structural interpretation | decision impact of supplied evidence |
| `advisory-review` | non-blocking quality feedback only | warnings and follow-up hypotheses |

Default to `candidate-gate` when a changed package, diff, or hypothesis is present.

## Resource loading

Load only what the active gate needs:

- [`references/gate-rubric.md`](references/gate-rubric.md) for severity, gate areas, and decision rules.
- [`references/evidence-integrity.md`](references/evidence-integrity.md) when before/candidate identities, frozen evaluators, package receipts, output aliases, recovery, or durable receipts matter.
- [`references/host-portability.md`](references/host-portability.md) when cross-host compatibility or host-specific extensions matter.
- [`references/integration-with-skill-improver.md`](references/integration-with-skill-improver.md) for experiment/self-improvement loops.
- [`references/capability-preservation-and-parent-provenance.md`](references/capability-preservation-and-parent-provenance.md) when capability maps, transformation ids/change intent, or direct-parent attribution are supplied.
- [`references/search-candidate-gate.md`](references/search-candidate-gate.md) when the candidate belongs to a multi-candidate/evolution search and lineage/search provenance is supplied.
- `scripts/static_change_gate.py` when a compatible Python runtime and filesystem access are available.
- [`examples/usage-examples.md`](examples/usage-examples.md) for compact outcome examples.
- [`evals/activation-scenarios.json`](evals/activation-scenarios.json) for planned activation/non-activation coverage; never call it executed evidence until actually run.

## Workflow

1. **Resolve target and runtime.** Identify one target skill, candidate evidence, caller context, policy, portability profile, available capabilities, and whether evidence is before/after, diff-only, or post-validation.
2. **Establish evidence identity.** Record supplied baseline/candidate/evaluator identities before interpretation. In self-improvement, also record generation/controller provenance and verify that the gate runs outside the candidate mutation surface when that evidence is supplied. If acceptance depends on frozen evidence but identity cannot be established, use `insufficient-evidence`. Read `references/evidence-integrity.md` for strict experiments or delivery gates.
3. **Check evidence sufficiency.** If no target content or candidate evidence exists, stop with `insufficient-evidence`. Partial evidence may support bounded findings, not unsupported acceptance.
4. **Inventory touched surfaces.** Map changes to activation, `SKILL.md`, references, scripts, assets/templates, examples, evals/tests, validators, packaging, protected paths, host adapters, output contract, and delivery/recovery behavior. When a capability map is supplied, map each touched surface to affected capability ids and classify preservation/regression using `references/capability-preservation-and-parent-provenance.md`.
5. **Run the static helper when available.** Resolve `<PYTHON>` from the host instead of assuming an executable name. Keep the JSON report outside both candidate and baseline roots.

```text
<PYTHON> scripts/static_change_gate.py \
  --target <AFTER> \
  --before <BEFORE> \
  --policy <normal|strict|advisory> \
  --profile <portable|openai> \
  --json <REPORT_OUTSIDE_TARGET>
```

For frozen experiments, add applicable evidence controls:

```text
--expected-before-sha256 <BASELINE_TREE_HASH>
--expected-target-sha256 <FROZEN_CANDIDATE_TREE_HASH>
--protected-path evals/**
--protected-path <OTHER_PROTECTED_PATH>
--artifact-receipt <PACKAGE_RECEIPT_JSON>
```

Treat helper output as mechanical evidence, not the full decision.
6. **Review semantically.** Use the rubric to inspect activation intent, authority, safety, evidence discipline, validation truthfulness, output semantics, compatibility, and whether removed/changed resources still have valid owners/consumers.
7. **Review portability.** Under `portable`, fail or warn when core semantics depend on one host's private runtime. Optional host adapters are acceptable when ignoring them leaves the core workflow intact.
8. **Classify findings.** Mark each as blocking regression, material concern, non-blocking trade-off, false positive, or follow-up hypothesis. For search candidates, gate each candidate independently using `references/search-candidate-gate.md`; do not choose survivors, rank peers, or waive a regression because another candidate is worse. State whether it is candidate-introduced, pre-existing, or unknown when material.
9. **Decide.** Blocking regressions fail. Under `strict`, unresolved material concerns also fail unless explicitly waived. `pass` requires sufficient applicable evidence, not merely a clean static report.
10. **Report for the caller.** State accept, reject, repair-before-accept, gather-evidence, or advisory-only. Keep measured improvement separate from quality acceptance.

## Decision rules

- A better benchmark score never overrides a blocking regression.
- A clean static report does not prove semantic safety, runtime behavior, or behavioral improvement.
- Missing evidence is not a pass.
- Expected identity mismatch is blocking; do not silently refresh the expected hash after a mismatch.
- Mutation of a frozen evaluator/protected path invalidates a measured experiment unless the experiment is explicitly restarted.
- A successful artifact receipt that points to different candidate bytes is blocking.
- In self-improvement, a promotion receipt that points to different bytes, a mutable controller/evaluator, or a gate executed inside the candidate mutation surface is blocking under `strict` policy.
- Host-specific adapters are acceptable; host-private core dependencies are portability concerns and fail under strict policy when unresolved.
- In `advisory` policy, blocking regressions remain visible and still prevent an unconditional accept decision.
- Do not convert gate findings into edits unless the user separately authorizes implementation.

## Output contract

Return this structure for every substantive gate:

```markdown
## Skill Change Gate Result

- target:
- mode:
- policy:
- portability profile:
- status: pass | pass-with-warnings | fail | insufficient-evidence
- decision for caller: accept | reject | repair-before-accept | gather-evidence | advisory-only

### Evidence identities
- stable baseline tree:
- direct parent tree: `<same-as-baseline | identity | not-supplied>`
- candidate tree:
- transformation ids / change intent: `<not-supplied | values>`
- search id / candidate id / lineage ref: `<not-applicable | supplied values>`
- evaluator/protected evidence:
- artifact/receipt correspondence:
- self-improvement generation/controller/promotion receipt: `<not-applicable | supplied evidence>`

### Evidence inspected
- target evidence:
- candidate evidence:
- commands/results:
- runtime capabilities:
- missing evidence:

### Capability preservation
| capability | classification | evidence | decision impact |
|---|---|---|---|

### Findings
| severity | area | origin | finding | decision impact |
|---|---|---|---|---|

### Portability
- portable core:
- optional host adapters:
- host-specific dependencies:

### Accepted trade-offs and false positives
- 

### Required fixes before accept
- 

### Follow-up hypotheses
- 
```

Use concise entries. Never invent command results, hashes, benchmark scores, or runtime support.

## Stop conditions

Stop or return `insufficient-evidence` when:

- no target skill content is available;
- no candidate change, before/after comparison, or acceptance question is available;
- multiple root `SKILL.md` files exist and the intended target cannot be inferred;
- required before/candidate/evaluator identity cannot be verified for a strict measured experiment;
- a required validator/benchmark/runtime capability is unavailable and its absence prevents a trustworthy decision;
- expected source/evaluator identity changed after freeze and the experiment has not been explicitly restarted;
- the candidate touches blocked secrets, credentials, evaluator fixtures, expected outputs, benchmark baselines, generated evidence, repository metadata, old archives, or unrelated paths;
- archive inspection would require unsafe extraction or path traversal handling outside available tools;
- the request requires editing files but the current task is gate-only.

## Integration defaults

For experiment loops, use `strict` for automated/self-improvement and `normal` for manual patches. Keep the gate stateless and portable: callers may supply hashes, freeze manifests, validator results, package/promotion receipts, and generation provenance, but the skill must not require another installed skill to interpret them. Pairwise knowledge of the improvement-loop handoff is allowed; broad specialist discovery/orchestration is not.
