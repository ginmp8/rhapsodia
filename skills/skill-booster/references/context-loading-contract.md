# Context Loading Contract

## At a Glance

- **Purpose:** Define how Skill Booster evaluates discovery, Top-100 control-plane quality, semantic previews, and reference depth for an existing skill.
- **Load when:** Auditing or optimizing activation/context loading, changing long Markdown, or deciding whether required knowledge is discoverable without deep reference chains.
- **Decision impact:** Separates routing quality from instruction quality, requires decision-useful previews for long references, and makes stale/vague previews or hidden mandatory reference chains blocking structural findings.

## Contents

- Discovery quality
- Top-100 control-plane quality
- Semantic preview contract
- Navigation map contract
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

## Semantic Preview Contract

For every editable supporting `.md` over 100 physical lines, require an early `At a Glance`, `Summary`, `Quick Reference`, or `Overview` inside the first 40 lines. Before the navigation map, the preview must include these explicit signals:

- **Purpose:** what knowledge, control, or contract the document owns;
- **Load when:** the branch, decision, risk, or task state that makes the document relevant;
- **Decision impact:** the consequential decisions, invariants, contracts, outputs, or failure modes that reading the document changes or constrains.

Add **Do not load when** when confusion with a nearby reference is plausible. Keep each required signal specific enough to distinguish the document from sibling references. Generic text such as `Read this file when the workflow needs <title>`, `Primary topics: ...`, or a copied heading list does not satisfy the semantic-preview requirement.

The semantic preview is the information-scent surface. A perfect navigation index cannot compensate for a vague preview.

## Navigation Map Contract

After the semantic preview, place `Contents`, `Table of Contents`, or `Section Map` within the first 40 lines. Treat it only as navigation.

Derive entries from the document's actual material `##` headings outside fenced code. Exclude the document title and preview/navigation headings. Every remaining H2 must appear exactly once, in document order, and the map must not name sections that do not exist. H3+ entries are optional unless a deeper map is intentionally needed. Revalidate the map whenever headings change.

Missing semantic-preview signals, generic filler preview language, missing navigation structure, or contents/heading drift is a structural validation failure for editable Markdown. Generated, vendor, or unsafe-to-rewrite Markdown may declare `<!-- context-preview-exception: generated -->`, `vendor`, or `unsafe-to-rewrite` within the first 40 lines; record the exception and surface it as a warning rather than silently skipping the file.

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
- validate Top-100 and semantic-preview structure mechanically;
- review semantic specificity rather than treating mechanical labels as proof of quality;
- rerun affected activation/instruction tests;
- use holdout/catalog-competition cases for promotion claims when metadata was tuned against visible prompts;
- reject changes that improve routing by erasing legitimate scope.

## Exceptions

Generated/vendor Markdown or unusually dense deterministic contracts may be exempt from semantic-preview formatting when rewriting would create risk. Record the exception and ensure the nearest editable control surface exposes the decision-critical summary.
