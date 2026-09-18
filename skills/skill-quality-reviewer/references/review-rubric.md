# Skill Review Rubric

## Scoring policy

Use a 0-5 raw score per dimension, then apply the dimension weight.

| Raw score | Meaning |
|---:|---|
| 5 | Clear, coherent, integrated, current, and evidenced for the inspected scope. |
| 4 | Strong with bounded defects that do not impair common use. |
| 3 | Usable but has material gaps, ambiguity, legacy residue, or weak validation. |
| 2 | Common paths are fragile, historically coupled, or require undocumented assumptions. |
| 1 | The dimension is substantially broken, contradictory, or governed by obsolete behavior. |
| 0 | Missing, unusable, invalid, or incapable of representing the declared current capability. |

Weighted points = `(raw score / 5) * weight`. Round only the final total to one decimal place.

## Dimensions

| ID | Dimension | Weight | Primary review questions |
|---|---|---:|---|
| D1 | Purpose and ownership | 8 | Is there one coherent operational responsibility? Are owner, writers, consumers, target, and non-goals clear? |
| D2 | Activation and boundaries | 14 | Can common valid prompts trigger it? Are false positives, false negatives, ambiguity, and handoffs controlled? |
| D3 | Workflow and execution correctness | 14 | Are modes reachable, ordered, complete, and capable of producing their outputs without silent fallback? |
| D4 | Architecture and progressive loading | 9 | Is `SKILL.md` a control plane? Are modes/router/split decisions coherent? Are references shallow and purposeful? |
| D5 | Resource integration and consistency | 10 | Do files exist, agree, and participate in the workflow? Are there broken links, dead assets, stale examples, or orphan candidates? |
| D6 | Output contract and remediation usability | 9 | Are outputs auditable, feasible, consistent, and suitable for downstream correction? |
| D7 | Validation, evidence, and eval discipline | 10 | Are executed and planned checks separated? Do validators prove current behavior and explicit legacy rejection? |
| D8 | Documentation and calibration | 5 | Are difficult decisions, examples, terminology, and assumptions clear without historical or generic duplication? |
| D9 | Package hygiene and maintainability | 5 | Is the package parseable, clean, deterministic, and free of generated or obsolete operational residue? |
| D10 | Token efficiency and instruction clarity | 4 | Does each instruction change behavior? Is duplication controlled without deleting contracts or gates? |
| D11 | Legacy, compatibility, and structural noise | 12 | Is current behavior separated from history? Are migrations isolated, compatibility bounded, ownership preserved, and runtime peer coupling absent or justified? |

Total weight: 100.

## Defect taxonomy

### Activation defects

- common true-positive prompt omitted from the description;
- adjacent domain triggers false activation;
- body contains activation rules unavailable before activation;
- mode names or synonyms differ between frontmatter and workflow;
- ambiguous cases have no proceed/ask/handoff rule;
- a legacy or migration mode can activate from ordinary current requests.

### Workflow defects

- unreachable branch or missing entry condition;
- required step occurs after the decision that depends on it;
- circular handoff or recursive validation without closure;
- input is required but never requested, inferred, or generated;
- output requires evidence that no step collects;
- stop condition blocks a core valid path;
- mutation, review, packaging, or reporting authority is contradictory;
- current validation fails and the flow silently retries an old schema or alias;
- normal reads perform migration, dual lookup, or dual writes without an explicit adapter mode.

### Ownership defects

- a skill writes an artifact or decision owned by another role;
- ambiguous verbs such as "update status" or "set priority" omit owner and domain;
- technical completion automatically changes governance or release state;
- a downstream executor rewrites upstream requirements or acceptance criteria;
- one skill validates or mutates a peer by importing its implementation.

### Consistency defects

- the same term has incompatible meanings across files;
- examples, templates, evals, and instructions specify different outputs;
- a script CLI differs from the documented command;
- a validator enforces an outdated schema;
- a resource is renamed or moved without updating references;
- metadata advertises a broader or narrower capability than the package;
- current and old contracts are both described as authoritative;
- changelog text supplies the only copy of a current rule.

### Legacy and compatibility defects

- published versions are retroactively renumbered or treated as aliases;
- package version and ecosystem-contract version are conflated;
- old handoff envelopes, fields, states, paths, or IDs remain accepted in normal operation;
- compatibility uses broad ranges, partial-field matching, coercion, best effort, or default-to-current behavior;
- unknown versions or fields do not fail closed;
- migration code is not isolated from normal activation and execution;
- aliases conflate business, technical, execution, governance, or release semantics;
- old acceptance tests preserve behavior that should now be rejected;
- examples, templates, fixtures, or golden files still teach replaced behavior;
- direct runtime imports, script execution, or file reads couple peer skill packages;
- historical prose, completed transition notes, or obsolete equivalence tables remain in normal context;
- old, backup, copy, deprecated, or version-suffixed scripts remain without a current consumer;
- a duplicated contract lacks a canonical machine-readable source or equivalence validation.

### Evidence defects

- planned scenarios presented as measured results;
- static lint presented as behavioral proof;
- mutable fixtures or expected outputs undermine comparison;
- readiness claim lacks command output, supplied evidence, or explicit checklist basis;
- score deductions have no cited evidence;
- a finding states impact without a plausible failure path;
- a keyword match is presented as a confirmed legacy defect without tracing consumers;
- no-match search output is presented as proof that no historical coupling exists;
- a textual gate is treated as proof of structural or behavioral compatibility.

### Architecture defects

- unrelated operational roles are bundled without a router;
- modes require separate tools, owners, validators, and failure models but remain entangled;
- `SKILL.md` becomes a knowledge dump while branch rules remain hard to locate;
- critical behavior exists only in a deep reference chain;
- scripts or assets are ornamental and not integrated;
- one package is operationally dependent on another package's internal files;
- a shared contract has no package-independent canonical representation or equivalence gate.

### Validation defects

- keyword presence is used as a semantic gate;
- a validator passes after catching an exception;
- mandatory conditions are downgraded to warnings;
- producer and consumer are not exercised together when compatibility is claimed;
- tests accept unknown or legacy fields outside migration mode;
- expected outputs or hashes are regenerated automatically to make a change pass;
- mixed-version combinations are not explicitly accepted or rejected;
- migration tests omit negative isolation, failure atomicity, or loss reporting.

### Package defects

- invalid or ambiguous root;
- missing or malformed frontmatter;
- broken local references;
- syntax-invalid bundled scripts;
- placeholders remain in operational files;
- caches, generated reports, old archives, backups, or scaffold files are packaged;
- package instructions cannot produce the declared archive shape;
- generated files contain local machine paths or stale evidence.

### Documentation and context-efficiency defects

- repeated rules compete or subtly diverge;
- long background or historical prose obscures current decisions;
- local compression removes activation, authority, validation, stop, evidence, or output duties;
- every task loads references that apply to only one branch;
- examples duplicate rules without adding calibration value;
- changelog duplicates current documentation or acts as a second operational manual;
- old names, formats, and transitions remain in normal references without affecting current execution.

## Legacy classification scoring

Use `references/legacy-and-compatibility-audit.md` for classification. Apply these scoring effects without double-counting:

- `current`: no deduction when canonical and validated;
- `migration-only`: no deduction when every isolation gate passes; deduct for each material missing gate;
- `obsolete`: deduct when still reachable, packaged, documented as current, or tested as valid;
- `duplicate`: deduct according to drift or context cost, not repetition alone;
- `contradictory`: usually material; severity depends on reachability and authority impact;
- `noise`: usually minor unless it changes activation or hides current rules;
- `blocked`: do not guess a score from absence of evidence; record uncertainty and apply a gate when the missing evidence is decision-critical.

## Gate overrides

Apply after scoring:

- Any confirmed `BLOCKER` => verdict cannot exceed `REWORK_REQUIRED`.
- Any unresolved `MAJOR` affecting a common path => verdict cannot exceed `REWORK_REQUIRED`.
- Ambiguous skill root or missing essential current-purpose evidence => `NEEDS_MORE_CONTEXT` regardless of score.
- A decision-critical legacy item classified `blocked` because owner, consumer, or compatibility evidence is missing => verdict cannot exceed `NEEDS_MORE_CONTEXT` for a removal-readiness claim.
- Implicit legacy acceptance on the normal path, silent state or field translation, or unauthorized cross-owner writes => at most `REWORK_REQUIRED` when confirmed.
- Broken package validation required by the target's own contract => `REWORK_REQUIRED`.
- Missing behavioral execution => prohibit measured activation, robustness, compatibility, migration-isolation, or benchmark claims, but do not automatically fail a static review.
- A score of 85 or higher supports `READY` only when no gate blocks it.
- A score of 70-84.9 supports at most `READY_WITH_COMMENTS`.
- A score below 70 supports `REWORK_REQUIRED`, unless missing context makes `NEEDS_MORE_CONTEXT` more accurate.

## Scoring safeguards

- Do not deduct the full weight for one local issue.
- Do not duplicate one root defect across every dimension; identify the root cause and record secondary effects.
- Do not award full points solely because a section heading exists.
- Do not require scripts, assets, examples, or evals when they add no operational value; assess whether the absence weakens the declared capability.
- Treat deterministic preflight output and legacy-signal searches as evidence leads, not automatic scores.
- Do not reward deletion, lower token count, or fewer files unless current behavior, authority, and validation are preserved.
