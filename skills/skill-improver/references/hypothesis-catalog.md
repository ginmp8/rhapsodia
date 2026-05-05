# Hypothesis Catalog

Use one specific, observed-weakness hypothesis per iteration. Prefer user-supplied hypotheses and `skill-hypothesis-discovery` backlogs over this built-in catalog. Use this catalog only as a fallback or as seed taxonomy for discovery.


## Discovery handoff

Before using built-in hypotheses, check whether the user supplied a hypothesis or backlog. If not, and there is benchmark, harness, validation, reviewer, or user-feedback evidence, use `skill-hypothesis-discovery` to generate 5-10 candidates, rank them, and select the next 1-3 testable hypotheses.

Discovery output must be treated as planning evidence until `skill-improver` tests a candidate against the frozen evaluator and `skill-change-gate` accepts the result. Do not generate random mutations. A good discovery outcome may be `no mutation recommended` or `gather evidence` when the target is already strong or evidence is thin.

## Trigger and activation

### H001 - Frontmatter trigger specificity
Mechanism: clearer description improves activation precision/recall.
Changes: make description action-oriented; include concrete triggers, target inputs/outputs, and negative boundaries.
Evidence: activation score improves; false positives do not increase.

### H002 - Negative activation boundaries
Mechanism: exclusions reduce accidental activation.
Changes: add non-goals to description when routing-relevant; add body-level refusal/delegation rules.
Evidence: negative prompts stop activating or redirect correctly.

## Workflow

### H010 - Deterministic step order
Mechanism: sequential workflow improves output conformance.
Changes: numbered steps, branch decision points, finalization criteria.
Evidence: outputs follow required structure more often.

### H011 - Mode selection matrix
Mechanism: explicit modes reduce ambiguity.
Changes: map user intent to mode, inputs, outputs, validators.
Evidence: ambiguous prompts choose the expected path more often.

### H012 - Severity-gated review loop
Mechanism: reviewer findings become safer and more actionable when routed by severity before mutation.
Changes: classify findings as critical, major, or minor; fix critical and major findings before polish; evaluate minor findings for functional value, false-positive risk, and activation/output impact before editing.
Evidence: critical and major findings reach zero, minor decisions are explicitly accepted or rejected, and validation confirms no safety, activation, or output gate regressed.

### H013 - Evidence-backed hypothesis backlog
Mechanism: candidate selection improves when hypotheses are derived from benchmark, harness, validation, architecture, activation, security, cleanup, or token-efficiency evidence instead of round-robin or random selection.
Changes: load a supplied backlog or run/apply `skill-hypothesis-discovery`; select the highest-ranked bounded hypothesis with validation available; record deferred and rejected hypotheses.
Evidence: every tested candidate has an evidence signal, expected effect, validation method, and rollback/change-gate rule; random or cosmetic candidates are not tested.

## Output

### H014 - Structural change gate
Mechanism: candidate acceptance becomes safer when metric gains are checked against structural regressions before acceptance.
Changes: add or tighten change-gate policy, record blocking regressions, material concerns, accepted trade-offs, and decision impact.
Evidence: candidates with metric gains but blocking regressions are rejected; accepted candidates preserve activation, safety, validation, references, packaging, and output contracts.

### H020 - Output contract
Mechanism: mandatory sections reduce incomplete/inconsistent responses.
Changes: required final structure, artifact naming/path rules, evidence/citation rules when applicable.
Evidence: output conformance improves.

### H021 - Examples
Mechanism: examples calibrate style, granularity, and edge decisions.
Changes: add one positive, one negative, one ambiguous example.
Evidence: qualitative conformance and edge handling improve.

## Validation

### H030 - Validation checklist
Mechanism: explicit gates catch invalid outputs before final answer.
Changes: closing checklist, pass/fail criteria, required scripts when available.
Evidence: fewer failed gates.

### H031 - Deterministic validator
Mechanism: repeatable script replaces fragile manual checks.
Changes: check frontmatter, required files, schema, or report structure.
Evidence: evaluator confirms validation support.

## Context efficiency

### H040 - Move details to references
Mechanism: compact `SKILL.md` improves context efficiency without capability loss.
Changes: move long rubrics/examples to `references/`; keep `SKILL.md` as control plane.
Evidence: context-efficiency score improves.

### H041 - Integrate or remove unused resources
Mechanism: resources become trustworthy when connected to workflow; truly unused files are removed.
Diagnosis: classify each weak resource as operational template, script input/output, explanatory reference, example, fixture, or unused scaffold before deleting.
Changes: integrate useful templates/references/examples/scripts via workflow references, loading rules, writer/validator coverage, or package checks; preserve `assets/templates/` for repeatable skeletons rendered/copied/filled by a declared workflow; move explanatory-only content to `references/`; delete placeholders, duplicates, obsolete files, unreferenced assets, or stale examples only after confirming no behavior depends on them.
Evidence: resource, maintainability, or validation score improves without reducing output quality, workflow clarity, or reusable artifact coverage; removals have rationale and preserved resources have consumers/gates.

## Safety and robustness

### H050 - Safety boundaries
Mechanism: better handling of unsafe/out-of-scope/unsupported requests.
Changes: non-goals, escalation/clarification rules, unknown-preservation rules.
Evidence: edge-case prompts improve.

### H051 - Rollback/failure handling
Mechanism: safer partial-failure behavior.
Changes: stop conditions, recovery rules, no-fabrication rules.
Evidence: robustness score improves.

### H052 - Graceful loop cancellation
Mechanism: long-running loops are safer when cancellation is explicit and preserves accepted target changes.
Changes: add stop-file checks between iterations, document cancellation commands, and state what happens to accepted, rejected, and in-flight candidates.
Evidence: cancellation path is documented, helper script compiles, runner accepts the stop-file option, and package validation still passes.
