# Context Loading Contract

## At a Glance

- **Purpose:** Define the discovery, Top-100, semantic-preview, and reference-depth contract used when creating or substantially redesigning a skill.
- **Load when:** Authoring `SKILL.md`, writing long supporting Markdown, or validating that an agent can decide what to load without reading deep reference chains.
- **Decision impact:** Requires the primary control plane in the first 100 lines of `SKILL.md`, requires decision-useful semantic previews for long references, and keeps navigation indexes separate from relevance/decision signals.

## Contents

- Discovery surface
- Top-100 control surface
- Semantic preview contract
- Navigation map contract
- Reference depth
- Exceptions
- Validation

## Discovery Surface

Treat `description` as a routing API, not as a catalog of implementation details.

Include:

- the capability/outcome;
- concrete trigger contexts or user intents;
- a meaningful non-use boundary when nearby skills overlap.

Prefer discriminative language over long specialist/host lists. Validate ambiguous and negative cases against neighboring skill descriptions when catalog competition is material.

## Top-100 Control Surface

If `SKILL.md` exceeds 100 lines, its first 100 physical lines must expose enough information to begin correctly without following another Markdown link.

Cover these semantic elements, using natural headings appropriate to the skill:

1. purpose or mission;
2. scope/activation/routing boundary;
3. mode or branch selection when material;
4. workflow, quick start, steps, process, or execution sequence;
5. critical rules, constraints, guardrails, requirements, or invariants;
6. direct resource pointers for branch details.

The first 100 lines may summarize detailed rules that are expanded later. Do not duplicate large procedures solely to satisfy this contract.

## Semantic Preview Contract

For every editable supporting `.md` over 100 physical lines, put `At a Glance`, `Summary`, `Quick Reference`, or `Overview` inside the first 40 lines. Before the navigation map, the preview must explicitly state:

- **Purpose:** what the document owns or explains;
- **Load when:** the workflow branch, decision, risk, or task state that makes it relevant;
- **Decision impact:** what decisions, invariants, contracts, outputs, or failure modes it changes or constrains.

Add **Do not load when** when a sibling reference could plausibly be confused with it. The required signals must be specific to the document. Boilerplate such as `Read this file when the workflow needs <title>`, a `Primary topics` line, or a copied section list is insufficient.

A semantic preview exists to answer `why should the active branch load this file?`; a navigation list answers only `where are its sections?`. Do not treat one as evidence for the other.

## Navigation Map Contract

After the semantic preview, put `Contents`, `Table of Contents`, or `Section Map` within the first 40 lines.

- derive entries from actual material `##` headings outside fenced code;
- exclude the document title and preview/navigation headings;
- include every remaining H2 exactly once and preserve document order;
- do not list headings that do not exist;
- revalidate whenever headings change;
- keep H3+ entries optional unless a deeper map is intentionally useful.

Missing semantic-preview signals, generic placeholder preview language, missing navigation structure, or contents/heading drift is a structural readiness failure for editable Markdown. Generated, vendor, or unsafe-to-rewrite Markdown may declare `<!-- context-preview-exception: generated -->`, `vendor`, or `unsafe-to-rewrite` within the first 40 lines; the validator must surface the exception as a warning.

## Reference Depth

Prefer one discovery hop:

`SKILL.md -> supporting file`

Rules:

- directly link every required Markdown resource from `SKILL.md`;
- do not make `reference A -> reference B` the only way to discover mandatory instructions;
- anchors and external URLs do not count as an extra package reference level;
- cross-links between already-directly-linked references are acceptable for navigation, but must not create hidden required branches;
- scripts/assets may be named by the directly linked control/reference file when they are branch-local deterministic helpers.

## Exceptions

A deviation is acceptable only when compression would materially reduce correctness or when a generated/vendor document cannot be safely rewritten. Record the exception and keep the decision-critical summary within the first 100 lines of the nearest editable control file.

## Validation

For packages created or redesigned by Skill Creator Juiced:

- fail readiness when a `SKILL.md` over 100 lines lacks early boundary, execution, and rule/control signals;
- fail editable supporting Markdown over 100 lines when required semantic-preview signals are missing, generic boilerplate is used, or the heading-derived navigation map is missing/stale;
- treat a valid navigation map as navigation evidence only, never as proof of semantic-preview quality;
- warn only for an explicit generated/vendor/unsafe-to-rewrite exception;
- warn when required Markdown is not directly discoverable from `SKILL.md` or when a deeper discovery chain appears;
- keep activation evaluation separate from instruction-following and outcome evaluation.
