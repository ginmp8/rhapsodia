# Context Loading Contract

## At a Glance

Use this contract when creating or substantially redesigning a skill. It separates the skill into three context surfaces so discovery is cheap, initial execution is reliable, and detailed knowledge is loaded only when needed.

- **Discovery surface:** frontmatter `name` + `description`.
- **Control surface:** the first 100 physical lines of `SKILL.md`.
- **Detail surface:** directly linked references, scripts, examples, schemas, and assets.

The goal is not to force every skill into identical headings. The goal is to ensure a partial read exposes the information needed to decide and begin correctly.

## Contents

- Discovery surface
- Top-100 control surface
- Supporting Markdown
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

## Supporting Markdown

For every editable supporting `.md` file over 100 physical lines:

- put `At a Glance`, `Summary`, `Quick Reference`, or `Overview` near the top;
- immediately follow it with `Contents`, `Table of Contents`, or `Section Map`, with both headings inside the first 40 lines;
- derive the contents entries from the document's actual material `##` headings outside fenced code;
- exclude the document title and preview headings themselves;
- include every remaining H2 exactly once, preserve document order, and do not list sections that do not exist;
- revalidate the contents list whenever headings change; H3+ entries remain optional unless a deeper map is intentionally needed;
- expose the document purpose, decision criteria, and major sections before line 100;
- keep deep examples, schemas, and long rationale later.

Missing preview structure or contents/heading drift is a structural readiness failure for editable Markdown, not merely an editorial warning. Generated, vendor, or unsafe-to-rewrite Markdown may declare `<!-- context-preview-exception: generated -->`, `vendor`, or `unsafe-to-rewrite` within the first 40 lines; the validator must surface the exception as a warning.

For shorter Markdown, the same preview-first pattern is preferred when it improves scanning but is not mandatory.

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
- fail editable supporting Markdown over 100 lines when the early summary/heading-derived contents contract is missing or stale; warn only for an explicit generated/vendor/unsafe-to-rewrite exception;
- warn when required Markdown is not directly discoverable from `SKILL.md` or when a deeper discovery chain appears;
- keep activation evaluation separate from instruction-following and outcome evaluation.
