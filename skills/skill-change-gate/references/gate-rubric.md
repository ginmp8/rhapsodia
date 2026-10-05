# Gate Rubric

## At a Glance

Judge one candidate skill change without redesigning the whole package. Separate structural, context-loading, behavioral, runtime, delivery, and reviewer evidence. Blocking regressions fail; material concerns fail under `strict` unless validly waived; mechanical signals require semantic interpretation.

Top-100/context-loading quality is a first-class gate surface: long `SKILL.md` files must expose the control plane early, long editable supporting Markdown must preview its purpose and real section map, and required instructions should be directly discoverable from `SKILL.md`. Treat these rules as `portable-package-policy`, not as Agent Skills specification claims.

## Contents

- Severity model
- Finding metadata
- Gate areas
- Decision matrix
- Review discipline

Use this rubric to judge one candidate skill change. Separate structural, context-loading, behavioral, runtime, delivery, and reviewer evidence. Review the candidate change, not the entire package as a redesign exercise.

## Severity model

| Severity | Meaning | Default decision |
|---|---|---|
| `blocking regression` | Candidate or deciding evidence violates a hard invariant: loading, safety, core activation, protected evidence, evidence identity, validation truthfulness, delivery integrity, required compatibility, or portable-core correctness. | fail |
| `material concern` | Candidate may reduce quality, activation precision, maintainability, portability, recoverability, evidence value, or compatibility without a proven hard break. | warning; fail under strict unless validly waived |
| `non-blocking signal` | Mechanical change worth semantic/evaluator review but not proof of regression by itself. | no automatic failure |
| `non-blocking trade-off` | Intentional bounded change with sufficient rationale/evidence. | pass with record |
| `false positive` | Suspected issue disproven by inspected evidence. | pass with rationale |
| `follow-up hypothesis` | Possible improvement outside the current candidate. | no decision impact |

## Finding metadata

For every material finding record:

- `rule_origin`: for example `agent-skills-spec`, `portable-package-policy`, `security-policy`, `experiment-policy`, `delivery-integrity-policy`, or another explicit local source;
- `regression_delta`: `introduced`, `worsened`, `preexisting-unchanged`, `improved`, `resolved`, or `unknown`.

Do not attribute pre-existing unchanged debt to the candidate. Do not label an internal packaging convention as an Agent Skills specification requirement unless the specification establishes it.

## Gate areas

### 1. Loading and portable package structure

Blocking examples:

- missing root `SKILL.md` or malformed required frontmatter;
- required portable name/identity contract is broken;
- unsafe archive/path layout or symlink escape;
- secrets, credentials, repository metadata, dependency/vendor trees, or nested archives violate the selected package/security policy.

Material examples include weak hygiene, unreachable support resources, or stale optional host metadata.

### 1A. Capability preservation and parent drift

Blocking examples:

- required capability is `regressed` or `removed-breaking` without authorization;
- direct-parent/baseline identity contradicts the transformation record under strict policy;
- a required affected capability remains `unproven` when acceptance depends on it.

Do not infer semantic capability loss from file deletion alone. Trace owner, consumers, validators, and replacement behavior when a capability map is supplied.

### 2. Activation and routing

Blocking examples:

- description/routing no longer represents the real trigger or artifact;
- activation broadens into unrelated work;
- a material non-activation boundary is removed;
- adjacent handoffs become contradictory.

Text length, example count, or wording compression are only signals. When the activation surface changed materially, prefer executed or supplied activation/non-activation/ambiguous-routing evidence over length heuristics.

### 2A. Top-100 control plane and context loading

For any `SKILL.md` over 100 physical lines, inspect the first 100 separately from the full file. Under the portable package policy, those lines should expose purpose/scope, activation/routing, material mode selection, a usable workflow/quick start, critical rules/invariants, and direct branch-resource pointers.

Material concerns include:

- a workflow/mode/rules section exists but is hidden entirely below line 100;
- the first 100 lines are mostly narrative/background and do not let an agent begin correctly;
- required branch guidance is available only through a multi-hop Markdown chain;
- an editable supporting `.md` over 100 lines lacks an early summary plus `Contents`/section map within the first 40 lines;
- the supporting document's contents map drifts from its real material `##` headings.

Escalate to blocking when context-loading loss makes a required safety, authority, routing, evidence-integrity, or execution condition unreachable or contradicts the deeper source. Otherwise classify the issue as material; under `strict`, unresolved material context-loading regressions fail.

Generated/vendor/unsafe-to-rewrite Markdown may declare an explicit early exception. Do not mistake a local Top-100 policy for a requirement of the Agent Skills specification.

### 3. Scope, authority, and protected paths

Blocking examples:

- mutation authority expands beyond target scope;
- blocked paths become writable without authorization;
- frozen evaluator fixtures, expected outputs, benchmark baselines, or generated evidence can be altered during a measured candidate;
- protected path sets drift without explicit experiment restart;
- under strict policy, a material authority expansion (tool permission, executable action, network/filesystem mutation, secret access, or runtime dependency) lacks explicit authorization evidence.

New/changed scripts or host permission metadata are mechanical authority signals, not automatic proof of unsafe behavior.

### 4. Resource routing and local references

Blocking examples:

- referenced resources are removed/renamed without valid consumers being updated;
- required branch-specific guidance becomes unreachable;
- a local reference escapes the skill package.

Material examples include package growth with no routing benefit or resources whose consumers are unclear.

### 5. Safety, security, and governance

Blocking examples:

- unsafe shell execution, broad deletion, path traversal, or untrusted extraction is introduced;
- secrets/protected evidence can be exposed or overwritten;
- credential/sensitive logging handling becomes unsafe;
- no-fabrication/evidence boundaries are weakened.

### 6. Evidence subject, policy, and experiment integrity

Blocking examples:

- expected baseline/candidate identity differs from inspected bytes;
- deciding evidence identifies candidate bytes different from the gated candidate;
- candidate is accepted against a different baseline than the one measured;
- frozen evaluator/scenario inputs drift;
- required evidence is failed, blocked, not-run, or silently replaced after results are known;
- strict measured acceptance cannot identify the deciding policy/verifier when exact identity is material;
- artifact/promotion receipt identifies different candidate bytes.

Use `references/decision-evidence-contract.md` and `references/evidence-integrity.md`.

### 6A. Evaluator exposure and stochastic sufficiency

Blocking examples:

- an evaluator declared as holdout was exposed to candidate construction or selection;
- the caller declared holdout evidence required but none is supplied;
- completed trials are below the caller-declared required trial count;
- independent replication was declared required but not completed.

The gate verifies the caller's evaluation contract; it does not invent universal trial counts, score thresholds, or significance rules.

### 6B. Freshness and TOCTOU

Blocking for a current promotion claim:

- expected destination/parent state differs from the observed state and the decision has not been revalidated;
- required destination/current-state evidence is missing.

Treat this as stale evidence, not proof that the candidate itself is bad.

### 7. Validation, benchmark, and claim discipline

Blocking examples:

- readiness/improvement claims lack executed or supplied evidence appropriate to the claim;
- validator, threshold, fixture, or scoring contract is weakened to obtain a pass;
- failed gates are hidden/reframed as success;
- static evidence is presented as behavioral/runtime/perceptual proof.

### 8. Delivery, output-path safety, recovery, and receipts

Blocking examples:

- output aliases an input, protected file, evaluator, or sibling receipt;
- failure can overwrite last-good output when preservation is part of the contract;
- multi-output commit can leave mixed state without recovery semantics;
- rollback destroys remaining recovery evidence;
- success receipt precedes commit or refers to different bytes.

Machine-readable receipts consumed by automation should be versioned and candidate-bound.

### 9. Host portability and compatibility

Blocking under a portable/cross-host requirement:

- semantic core requires one host's private tool identifier, URI, absolute sandbox path, or proprietary invocation;
- correctness depends on a host-only adapter/metadata field other hosts may ignore;
- scripts require undeclared unavailable runtimes/dependencies without fallback;
- intentional compatibility behavior is removed without migration evidence.

Optional adapters are acceptable when ignoring them leaves the portable semantic core intact.

### 9A. Consumer compatibility and ecosystem claims

Local candidate acceptance and ecosystem compatibility are separate claims.

An `ecosystem-safe` claim is blocking when:

- the known-consumer inventory is incomplete;
- a known consumer is incompatible;
- a known consumer remains unverified for a changed public contract.

A local candidate may still be locally acceptable when the broader ecosystem claim is `not-proven`; do not silently widen the claim.

### 10. Output contract and reporting

Blocking examples:

- status/decision becomes ambiguous;
- required evidence identities, missing-evidence duties, or claim scope disappear;
- automation-facing result changes incompatibly without contract/version handling.

For machine consumption use `contracts/change-gate-result.schema.json`.

### 11. Waivers

A valid waiver is explicit, authorized, candidate-bound, policy-bound, scoped to named findings, and preserved in the audit trail. Read `references/waiver-policy.md`.

Non-waivable classes remain failures: identity drift, protected evaluator mutation, receipt/candidate mismatch, unsafe path/secret exposure, fabricated required evidence, contaminated holdout claims, and candidate self-authorization.

### 12. Context efficiency and maintainability

Usually material/non-blocking unless required control-plane behavior becomes hidden. Prefer progressive disclosure over bloating `SKILL.md`, but do not move selection, workflow, invariants, or branch routing out of the first 100 lines merely to reduce token count. Prefer direct `SKILL.md -> supporting file` discovery for required Markdown. Do not fail merely because a different decomposition is aesthetically cleaner.

## Decision matrix

| Findings | Normal policy | Strict policy | Advisory policy |
|---|---|---|---|
| any blocking regression | fail | fail | fail visible |
| material concerns only | pass-with-warnings | fail unless valid waiver | pass-with-warnings |
| non-blocking signals/trade-offs only | pass | pass | pass |
| insufficient/stale required evidence | insufficient-evidence | insufficient-evidence | advisory-only with limits |
| no findings and sufficient evidence | pass | pass | pass |

## Review discipline

- Penalize `introduced`/`worsened` findings more strongly than `preexisting-unchanged` debt.
- Record resolved/improved baseline findings positively without turning them into an unrelated improvement score.
- Keep benchmark improvement and quality acceptance separate.
- Keep host-adapter quality and portable-core quality separate.
- Keep source, evaluator, policy/verifier, candidate, destination, artifact, and receipt identities separate.
- Keep local acceptance and ecosystem-safe claims separate.
