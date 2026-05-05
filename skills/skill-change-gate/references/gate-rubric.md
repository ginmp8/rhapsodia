# Gate Rubric

Use this rubric to judge a candidate skill change. Separate mechanical evidence from reviewer judgment.

## Severity Model

| Severity | Meaning | Default decision |
|---|---|---|
| `blocking regression` | The candidate breaks loading, safety, core activation, local references, protected artifacts, validation truthfulness, packaging, or output contract. | fail |
| `material concern` | The candidate may reduce quality, maintainability, activation precision, evidence value, or context efficiency, but does not clearly break acceptance. | warning; fail under strict policy unless waived |
| `non-blocking trade-off` | The candidate changes style, compression, examples, or optional detail with acceptable rationale. | pass with record |
| `false positive` | The suspected issue is not real after inspection. | pass with rationale |
| `follow-up hypothesis` | A possible improvement that is outside the current candidate. | no decision impact |

## Gate Areas

### 1. Loading and package structure
Blocking examples:
- missing root `SKILL.md`;
- invalid or missing frontmatter fields;
- multiple root candidates with unclear target;
- unsafe archive/path layout;
- included secrets, credentials, `.git`, caches, old zips, or generated evidence.

Material examples:
- weak package hygiene that does not block loading;
- support directories included without clear consumers.

### 2. Activation and routing
Blocking examples:
- description no longer names the real trigger or target artifact;
- candidate broadens activation into unrelated work;
- non-activation boundaries are removed where they prevent false positives;
- adjacent skill handoffs become contradictory.

Material examples:
- fewer examples for ambiguous prompts;
- activation wording becomes less concrete but still usable.

### 3. Scope, authority, and protected paths
Blocking examples:
- candidate expands mutation authority beyond the target skill;
- blocked paths become editable without explicit authorization;
- evaluator fixtures, expected outputs, benchmark baselines, or generated evidence can be modified during an improvement candidate.

Material examples:
- allowed mutation scope is less visible;
- ownership or handoff rules become harder to follow.

### 4. Resource routing and local references
Blocking examples:
- referenced files are deleted or renamed without updating links;
- important scripts/templates/references lose declared consumers;
- branch-specific guidance required by the workflow becomes unreachable.

Material examples:
- useful resources remain but their loading condition is vague;
- package size increases without clear routing impact.

### 5. Safety, security, and governance
Blocking examples:
- unsafe shell execution, broad deletion, untrusted archive extraction, or path traversal is introduced;
- the skill can expose or write secrets;
- sensitive logging or credential handling becomes unsafe;
- no-fabrication or evidence boundaries are weakened.

Material examples:
- failure handling is less explicit;
- risk notes move to a less visible reference but remain reachable.

### 6. Validation, benchmark, and evidence discipline
Blocking examples:
- candidate claims validation, readiness, benchmark score, precision, recall, or improvement without evidence;
- validators are weakened to make a candidate pass;
- evaluator inputs change during a measured improvement candidate;
- failed gates are hidden or reframed as success.

Material examples:
- validation commands remain but output expectations are less specific;
- planned scenarios are not clearly separated from executed results.

### 7. Output contract and reporting
Blocking examples:
- required final sections are removed when the caller depends on them;
- pass/fail decisions become ambiguous;
- required citation, evidence, file-path, line-range, or command-output duties are deleted where relevant.

Material examples:
- report becomes longer or shorter in a way that may affect usability;
- optional examples no longer match the preferred output style.

### 8. Context efficiency and maintainability
Usually material or non-blocking, unless the candidate hides required control-plane behavior. Prefer warnings and follow-up hypotheses over blocking decisions.

## Decision Matrix

| Findings | Normal policy | Strict policy | Advisory policy |
|---|---|---|---|
| any blocking regression | fail | fail | fail visible |
| material concerns only | pass-with-warnings | fail unless waived | pass-with-warnings |
| non-blocking trade-offs only | pass | pass | pass |
| insufficient target or candidate evidence | insufficient-evidence | insufficient-evidence | advisory-only with limits |
| no findings and sufficient evidence | pass | pass | pass |

## Review Discipline

- Review the change, not the whole skill as if it were a fresh redesign.
- Penalize regressions introduced by the candidate more strongly than pre-existing issues.
- Do not require polish unrelated to the candidate to pass the gate.
- Keep benchmark improvement and quality acceptance separate.
- State when a finding is pre-existing, candidate-introduced, or unknown.
