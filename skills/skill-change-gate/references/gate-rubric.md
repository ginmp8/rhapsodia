# Gate Rubric

Use this rubric to judge a candidate skill change. Separate mechanical evidence, behavioral evidence, runtime evidence, and reviewer judgment.

## Severity model

| Severity | Meaning | Default decision |
|---|---|---|
| `blocking regression` | Candidate breaks loading, safety, core activation, evidence identity, protected artifacts, validation truthfulness, packaging/delivery integrity, portable core behavior, or required output contract. | fail |
| `material concern` | Candidate may reduce quality, maintainability, activation precision, evidence value, portability, recoverability, or context efficiency without a proven hard break. | warning; fail under strict policy unless waived |
| `non-blocking trade-off` | Candidate changes style, compression, examples, optional host adapters, or optional detail with acceptable rationale. | pass with record |
| `false positive` | Suspected issue is disproven by inspected evidence. | pass with rationale |
| `follow-up hypothesis` | Possible improvement outside the current candidate. | no decision impact |

## Gate areas

### 1. Loading and portable package structure

Blocking examples:

- missing root `SKILL.md`;
- invalid required frontmatter;
- package directory name does not match `SKILL.md:name` under the portable profile;
- unsafe archive/path layout or symlink escape;
- included secrets, credentials, repository metadata, dependency/vendor trees, or nested archives that violate the package contract.

Material examples:

- weak hygiene that does not block loading;
- support directories included without clear consumers;
- optional host metadata is present but stale or unvalidated for that host.

### 2. Activation and routing

Blocking examples:

- description no longer names the real trigger or target artifact;
- candidate broadens activation into unrelated work;
- non-activation boundaries that prevent harmful false positives are removed;
- adjacent skill handoffs become contradictory.

Material examples:

- fewer examples for ambiguous prompts;
- activation wording becomes less concrete but remains usable.

### 3. Scope, authority, and protected paths

Blocking examples:

- candidate expands mutation authority beyond the target skill;
- blocked paths become editable without explicit authorization;
- frozen evaluator fixtures, expected outputs, benchmark baselines, or generated evidence can be changed during a measured candidate;
- supplied protected paths differ between before and after without explicit experiment restart.

Material examples:

- allowed mutation scope becomes less visible;
- ownership/handoff rules become harder to follow.

### 4. Resource routing and local references

Blocking examples:

- referenced files are removed/renamed without updating consumers;
- important scripts/templates/references lose declared consumers;
- required branch-specific guidance becomes unreachable;
- a local reference escapes the skill package.

Material examples:

- useful resources remain but their loading condition is vague;
- package grows without a clear routing benefit.

### 5. Safety, security, and governance

Blocking examples:

- unsafe shell execution, broad deletion, untrusted archive extraction, or path traversal is introduced;
- skill can expose or overwrite secrets/protected evidence;
- sensitive logging or credential handling becomes unsafe;
- no-fabrication or evidence boundaries are weakened.

Material examples:

- failure handling becomes less explicit;
- risk notes remain valid but move to a less visible location.

### 6. Evidence identity and experiment integrity

Blocking examples:

- expected before/candidate tree identity does not match inspected bytes;
- evaluator/scenario inputs drift after freeze;
- candidate is accepted against a different baseline than the one measured;
- a package receipt identifies candidate bytes different from the frozen candidate;
- a failing/missing evidence source is silently replaced with a fresh one after seeing the result.

Material examples:

- candidate identity is available but external evaluator identity cannot be mechanically verified;
- artifact receipt reports success but omits candidate/source identity.

Use `references/evidence-integrity.md` when these checks apply.

### 7. Validation, benchmark, and claim discipline

Blocking examples:

- candidate claims validation/readiness/improvement without executed or supplied evidence;
- validator or threshold is weakened to make the candidate pass;
- failed gates are hidden or reframed as success;
- static checks are presented as proof of behavioral/runtime/perceptual quality.

Material examples:

- validation commands remain but expected outcomes are less explicit;
- planned scenarios are not clearly separated from executed results.

### 8. Delivery, output-path safety, recovery, and receipts

Blocking examples:

- output path can alias an input, protected file, evaluator, or sibling receipt and mutate it;
- validation/preflight failure can overwrite the last-good artifact where preservation is part of the contract;
- multi-output commit can leave a mixed old/new state without rollback/recovery semantics;
- failed rollback destroys the remaining recovery evidence;
- success receipt is emitted before or for bytes different from the committed artifact.

Material examples:

- receipt schema is not versioned even though automation consumes it;
- recovery locations are underspecified but no destructive failure mode is demonstrated;
- durable flush/atomic-write behavior is unclear for large machine-readable receipts.

### 9. Host portability and compatibility

Blocking examples under a cross-host/portable requirement:

- semantic core requires one host's private tool identifier, URI, absolute sandbox path, or proprietary invocation mechanism;
- correctness depends on a host-only metadata file/frontmatter extension that other compatible hosts may ignore;
- scripts require an undeclared runtime/dependency unavailable across the declared support envelope and no safe fallback exists;
- target removes intentional compatibility behavior without migration evidence.

Material examples:

- host adapter is correct but not clearly separated from the portable core;
- installation/discovery guidance is stale or host-specific without affecting package semantics;
- optional host extension narrows behavior only on that host and the trade-off is intentional.

Product names in descriptive text are not portability defects by themselves.

### 10. Output contract and reporting

Blocking examples:

- required final sections disappear when callers depend on them;
- pass/fail becomes ambiguous;
- required evidence identity, citation, file path, line range, command result, or missing-evidence duties are deleted where relevant.

Material examples:

- report becomes materially harder to consume;
- optional examples no longer match the preferred format.

### 11. Context efficiency and maintainability

Usually material/non-blocking unless required control-plane behavior becomes hidden. Prefer progressive references over bloating `SKILL.md`. Do not block merely because a different decomposition would be aesthetically cleaner.

## Decision matrix

| Findings | Normal policy | Strict policy | Advisory policy |
|---|---|---|---|
| any blocking regression | fail | fail | fail visible |
| material concerns only | pass-with-warnings | fail unless waived | pass-with-warnings |
| non-blocking trade-offs only | pass | pass | pass |
| insufficient target/candidate evidence | insufficient-evidence | insufficient-evidence | advisory-only with limits |
| no findings and sufficient evidence | pass | pass | pass |

## Review discipline

- Review the change, not the entire skill as a redesign exercise.
- Penalize candidate-introduced regressions more strongly than pre-existing issues.
- Do not require unrelated cleanup to pass the gate.
- Keep benchmark improvement and quality acceptance separate.
- Keep host adapter quality and portable-core quality separate.
- Keep source identity, evaluator identity, candidate identity, and artifact identity separate.
- State when a finding is pre-existing, candidate-introduced, or unknown.
