# Skill Review Rubric

## Scoring policy

Use a 0-5 raw score per dimension, then apply the dimension weight.

| Raw score | Meaning |
|---:|---|
| 5 | Clear, coherent, integrated, and evidenced for the inspected scope. |
| 4 | Strong with bounded defects that do not impair common use. |
| 3 | Usable but has material gaps, ambiguity, or weak validation. |
| 2 | Common paths are fragile or require undocumented assumptions. |
| 1 | The dimension is substantially broken or contradictory. |
| 0 | Missing, unusable, or invalid for the declared capability. |

Weighted points = `(raw score / 5) * weight`. Round only the final total to one decimal place.

## Dimensions

| ID | Dimension | Weight | Primary review questions |
|---|---|---:|---|
| D1 | Purpose and ownership | 8 | Is there one coherent operational responsibility? Are owner, target, and non-goals clear? |
| D2 | Activation and boundaries | 16 | Can common valid prompts trigger it? Are false positives, false negatives, ambiguity, and handoffs controlled? |
| D3 | Workflow and execution correctness | 16 | Are modes reachable, ordered, complete, and capable of producing their outputs? |
| D4 | Architecture and progressive loading | 10 | Is `SKILL.md` a control plane? Are modes/router/split decisions coherent? Are references shallow and purposeful? |
| D5 | Resource integration and consistency | 12 | Do files exist, agree, and participate in the workflow? Are there broken links, dead assets, stale examples, or orphan candidates? |
| D6 | Output contract and remediation usability | 10 | Are outputs auditable, feasible, consistent, and suitable for downstream use? |
| D7 | Validation, evidence, and eval discipline | 12 | Are executed and planned checks separated? Do validators prove the properties claimed? Are scenarios representative? |
| D8 | Documentation and calibration | 6 | Are difficult decisions, examples, terminology, and assumptions clear without duplicating obvious knowledge? |
| D9 | Package hygiene and maintainability | 5 | Is the package parseable, clean, deterministic, and free of generated noise or hidden setup? |
| D10 | Token efficiency and instruction clarity | 5 | Does each instruction change behavior? Is duplication controlled without deleting contracts or gates? |

Total weight: 100.

## Defect taxonomy

### Activation defects

- common true-positive prompt omitted from the description;
- adjacent domain triggers false activation;
- body contains activation rules unavailable before activation;
- mode names or synonyms differ between frontmatter and workflow;
- ambiguous cases have no proceed/ask/handoff rule.

### Workflow defects

- unreachable branch or missing entry condition;
- required step occurs after the decision that depends on it;
- circular handoff or recursive validation without closure;
- input is required but never requested, inferred, or generated;
- output requires evidence that no step collects;
- stop condition blocks a core valid path;
- mutation, review, packaging, or reporting authority is contradictory.

### Consistency defects

- the same term has incompatible meanings across files;
- examples, templates, evals, and instructions specify different outputs;
- a script CLI differs from the documented command;
- a validator enforces an outdated schema;
- a resource is renamed or moved without updating references;
- metadata advertises a broader or narrower capability than the package.

### Evidence defects

- planned scenarios presented as measured results;
- static lint presented as behavioral proof;
- mutable fixtures or expected outputs undermine comparison;
- readiness claim lacks command output, supplied evidence, or explicit checklist basis;
- score deductions have no cited evidence;
- a finding states impact without a plausible failure path.

### Architecture defects

- unrelated operational roles are bundled without a router;
- modes require separate tools, owners, validators, and failure models but remain entangled;
- `SKILL.md` becomes a knowledge dump while branch rules remain hard to locate;
- critical behavior exists only in a deep reference chain;
- scripts or assets are ornamental and not integrated.

### Package defects

- invalid or ambiguous root;
- missing or malformed frontmatter;
- broken local references;
- syntax-invalid bundled scripts;
- placeholders remain in operational files;
- caches, generated reports, old archives, or scaffold files are packaged;
- package instructions cannot produce the declared archive shape.

### Context-efficiency defects

- repeated rules compete or subtly diverge;
- long background prose obscures decisions;
- local compression removes activation, validation, stop, evidence, or output duties;
- every task loads references that apply to only one branch;
- examples duplicate rules without adding calibration value.

## Gate overrides

Apply after scoring:

- Any confirmed `BLOCKER` => verdict cannot exceed `REWORK_REQUIRED`.
- Any unresolved `MAJOR` affecting a common path => verdict cannot exceed `REWORK_REQUIRED`.
- Ambiguous skill root or missing essential purpose evidence => `NEEDS_MORE_CONTEXT` regardless of score.
- Broken package validation required by the target's own contract => `REWORK_REQUIRED`.
- Missing behavioral execution => prohibit measured activation, robustness, or benchmark claims, but do not automatically fail a static review.
- A score of 85 or higher supports `READY` only when no gate blocks it.
- A score of 70-84.9 supports at most `READY_WITH_COMMENTS`.
- A score below 70 supports `REWORK_REQUIRED`, unless missing context makes `NEEDS_MORE_CONTEXT` more accurate.

## Scoring safeguards

- Do not deduct the full weight for one local issue.
- Do not duplicate one root defect across every dimension; identify the root cause and record secondary effects.
- Do not award full points solely because a section heading exists.
- Do not require scripts, assets, examples, or evals when they add no operational value; assess whether the absence weakens the declared capability.
- Treat deterministic preflight output as evidence, not an automatic score.
