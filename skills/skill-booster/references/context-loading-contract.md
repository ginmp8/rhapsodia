# Context Loading Contract

## At a Glance

Use this contract when auditing or optimizing an existing skill. Treat discovery and progressive loading as independent quality surfaces: a strong body cannot help if the skill is not selected, and a correct description cannot compensate for a control plane whose critical instructions are hidden below a partial read.

Evaluate three context surfaces:

- **Discovery surface:** `name` + `description` and competition with neighboring skills.
- **Control surface:** first 100 physical lines of `SKILL.md`.
- **Detail surface:** directly linked supporting Markdown, scripts, schemas, examples, and assets.

## Contents

- Discovery quality
- Top-100 control-plane quality
- Supporting Markdown previews
- One-level reference topology
- Optimization/evaluation rules
- Exceptions

## Discovery Quality

Evaluate metadata independently from task outcome.

Check:

- capability and user intent are explicit;
- trigger contexts are discriminative;
- plausible non-use boundaries are stated when neighboring skills overlap;
- descriptions are not inflated with implementation detail that reduces routing clarity;
- activation tests include positive, negative, ambiguous, boundary, and catalog-competition cases when relevant.

Do not infer discovery quality from an instruction-following benchmark that assumes the skill is already loaded.

## Top-100 Control-Plane Quality

When `SKILL.md` exceeds 100 lines, require the first 100 physical lines to expose:

1. purpose/scope;
2. activation or routing boundary;
3. mode/branch selection when material;
4. workflow/quick-start/process sufficient to begin;
5. critical constraints, rules, guardrails, or invariants;
6. direct pointers to branch-specific details.

Optimize by reordering, compressing, and moving branch detail outward. Do not delete semantics merely to satisfy the line budget.

## Supporting Markdown Previews

For every editable supporting `.md` over 100 physical lines, require an early `At a Glance`/summary followed by a `Contents`, `Table of Contents`, or `Section Map` within the first 40 lines. A partial preview must reveal the document purpose, major decisions, and section map before line 100.

Derive the contents list from the document's actual material `##` headings outside fenced code. Exclude the document title and preview headings (`At a Glance`/`Summary`/`Quick Reference`/`Overview` plus the contents heading itself). Every remaining H2 must appear exactly once, in document order, and the contents list must not name sections that do not exist. H3+ entries are optional unless the document explicitly needs a deeper map. Revalidate the list whenever headings change.

Treat missing preview structure or contents/heading drift as a structural validation failure for editable Markdown. Generated, vendor, or unsafe-to-rewrite Markdown may declare `<!-- context-preview-exception: generated -->`, `vendor`, or `unsafe-to-rewrite` within the first 40 lines; record the exception and surface it as a warning rather than silently skipping the file.

## One-Level Reference Topology

Prefer:

`SKILL.md -> supporting file`

- Required Markdown should be directly discoverable from `SKILL.md`.
- A reference-to-reference link may aid navigation only when both files are already directly reachable or the nested file is non-mandatory background.
- Do not accept hidden mandatory branches that require multiple Markdown hops.
- Preserve branch-local scripts/assets when direct Markdown discovery remains clear.

## Optimization and Evaluation Rules

Separate four evidence layers:

`metadata selection -> skill activation -> instruction following -> task outcome`

When context-loading changes are made:

- preserve a baseline snapshot;
- classify the change as repair, optimization, or experiment;
- validate Top-100 structure mechanically;
- rerun affected activation/instruction tests;
- use holdout/catalog-competition cases for promotion claims when metadata was tuned against visible prompts;
- reject changes that improve routing by erasing legitimate scope.

## Exceptions

Generated/vendor Markdown or unusually dense deterministic contracts may be exempt from early-summary formatting when rewriting would create risk. Record the exception and ensure the nearest editable control surface exposes the decision-critical summary.
