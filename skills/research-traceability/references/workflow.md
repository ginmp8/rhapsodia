# Workflow

## At a Glance

Use this file for the detailed execution order behind the six-phase control plane in `SKILL.md`. Preserve evidence identity before interpretation, convert the frozen corpus into atomic findings and testable requirements, freeze evaluators before related mutation when feasible, apply only reverse-justified changes, validate structure and semantics separately, then freeze/package exact passing bytes.

For Agent Skills over 100 lines, preserve the decision-critical control plane in the first 100 physical lines and keep required Markdown directly reachable from `SKILL.md`. This is a context-loading quality gate, not proof that the content is semantically correct.

## Contents

1. Intake and mode selection
2. Freeze input identities
3. Register sources
4. Extract atomic findings
5. Disposition every finding
6. Derive requirements
7. Map existing coverage and context loading
8. Define evaluation before candidate mutation
9. Plan and apply changes
10. Baseline vs candidate comparison
11. Mechanical validation
12. Semantic review
13. Repair
14. Freeze and deliver

## 1. Intake and mode selection

Select `create`, `improve`, `audit`, or `refresh` from the user's requested outcome. Resolve one target and one bounded research corpus.

If research is not complete but the user explicitly requested an end-to-end research-and-change workflow, complete the research first and freeze its output before extracting findings.

## 2. Freeze input identities

For local mutable evidence, use `scripts/snapshot_evidence.py`. For repositories, prefer an immutable revision/object identity. For live web evidence, record source URL, publication/update date, retrieval date when available, and the frozen research report/result that interpreted it.

In `improve` and `refresh`, freeze the target baseline before mutation. Preserve pre-existing evaluators as protected evidence.

## 3. Register sources

Create `S-*` records. Prefer primary/official evidence for factual behavior. Use independent evidence where operational experience, trade-offs, or controversy matters.

Do not infer source authority from popularity alone.

## 4. Extract atomic findings

Create `F-*` records from the frozen corpus.

Perform a second extraction pass whose only purpose is to detect:
- missed findings;
- duplicate findings;
- compound findings that should split;
- qualifiers lost during paraphrase;
- disagreements hidden by synthesis.

Do not add a finding merely to justify a desired implementation.

## 5. Disposition every finding

Assign one disposition and rationale. `Finding accounting` is the fraction of findings with explicit disposition; final work requires 100%.

For `rejected`, `not-applicable`, `uncertain`, and `conflict`, preserve enough rationale to explain why the finding did not become implementation.

## 6. Derive requirements

Translate findings into `R-*` requirements. Merge multiple findings only when they support the same operational behavior without losing meaningful qualifiers.

A requirement should say what the target skill must achieve, not prematurely dictate a file edit.

## 7. Map existing coverage

For existing targets, trace current files/instructions/scripts/evals before editing. Also map context-loading topology before mutation:
- inspect the discovery metadata separately from the loaded body;
- if `SKILL.md` exceeds 100 lines, identify whether purpose/scope, routing, material modes, usable workflow, critical constraints, and direct resource pointers are visible in the first 100 physical lines;
- for supporting Markdown over 100 lines, check for an early summary plus contents/index;
- verify required Markdown is directly reachable from `SKILL.md` rather than hidden behind mandatory multi-hop chains.

If a requirement is already satisfied:
- mark the finding `already-covered`;
- create a `C-*` record of kind `existing` pointing to the current target;
- still create an evaluation link so coverage is verified rather than assumed.

Treat context-loading structure as a quality surface, not as evidence that the underlying instructions are semantically correct.

## 8. Define evaluation before candidate mutation

For each final requirement, create one or more `E-*` records before implementing the change whenever feasible.

Freeze evaluator files or scenario definitions before candidate mutation. If a new evaluator must be changed after candidate results are visible, record why and re-baseline rather than silently tailoring the oracle.

## 9. Plan and apply changes

Create `C-*` records and apply only the smallest coherent target mutation.

Rules:
- every change must satisfy at least one requirement;
- preserve unrelated target behavior;
- avoid new abstractions unless the traceable requirement needs them;
- use scripts/schemas for deterministic mechanics and prose/rubrics for judgment;
- keep `SKILL.md` as the compact control plane and move branch detail to progressive references;
- do not hard-code research examples into general behavior unless they are part of the domain contract.

## 10. Baseline vs candidate comparison

In `improve` and `refresh`, compare the frozen baseline vs candidate with identical frozen evaluator inputs when behavioral execution is available. Keep environment/tool identity comparable when it can change the result.

Do not call a repair a measured improvement when only static validation ran. If paired execution is unavailable, report `not-run` for the behavioral delta and continue only with claims supported by structural or semantic-review evidence.

## 11. Mechanical validation

Run:

```text
<PYTHON> scripts/validate_traceability.py <workspace>/traceability.json --phase final --json-output <workspace>/reports/trace-validation.json
<PYTHON> scripts/validate_target_skill.py --target <target> --json-output <workspace>/reports/target-validation.json
```

Use `--phase audit` in audit mode.

Also run target-owned validators/tests. Structural validation does not establish behavioral correctness.

## 12. Semantic review

Apply [semantic-review.md](semantic-review.md). Prefer a reviewer or fresh context that did not author the candidate. Review the exact frozen corpus, traceability file, baseline target, candidate target, and frozen evaluators.

Reject a trace link that is structurally present but semantically false.

## 13. Repair

Use one diagnostic -> one smallest supported change -> same validator -> adjacent gates.

If two consecutive repairs do not improve the same objective diagnostic set, stop that branch and report the unresolved issue.

Do not delete findings, weaken requirements, lower evaluator thresholds, or modify frozen expected outcomes merely to obtain a pass.

## 14. Freeze and deliver

After the final pass:
- freeze the candidate;
- verify frozen evidence manifests;
- do not edit candidate bytes;
- package only the frozen candidate when requested;
- emit package and receipt hashes;
- preserve last-good outputs on failure.
