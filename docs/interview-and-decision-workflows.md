# Interview and decision workflows

## Overview

- **Purpose:** Choose the right new RhapsodIA 0.17.0 skill for questioning, documenting and validating engineering decisions.
- **Load when:** Preparing an interview, drafting domain documentation, mapping a large uncertain initiative, reviewing a Git diff or conducting an agent-session retrospective.
- **Decision impact:** Keeps elicitation, planning, governance, coding and review authority distinct while providing clear invocation examples.

## Contents

- Quick selection
- Decision interviews
- Documentation and long-running work
- Review and retrospectives
- Ownership, compatibility and license

## Quick selection

| User goal | Skill | Output |
|---|---|---|
| Challenge assumptions about a proposal | `grilling` (or alias `grill-me`) | Recommended answers, resolved choices and unanswered questions |
| Interview and record technical choices | `grill-with-docs` | Interview summary and user-approved glossary/ADR drafts |
| Clarify domain concepts and invariants | `domain-modeling` | Ubiquitous language, context scenarios and candidate ADRs |
| Map an uncertain multi-session effort | `wayfinder` | Durable decision map and its unblocked frontier |
| Review a PR against requirements and standards | `code-review` | Two independent axes; source-linked findings |
| Improve the next engineering session | `retro` | Evidence-backed improvement candidates and owners |

## Decision interviews

**Grilling** owns an interactive dependency tree. Each round contains up to five answerable questions with a recommended choice whose acceptance means "yes." Facts that tools can establish should be investigated, not asked of the user. The default run is bounded; an explicit deep session may extend the budget. Grilling must not interpret its own advice as an approved decision.

**Grill Me** is the explicit alias, not another interview implementation. Use it to invoke Grilling directly; it reports a missing dependency rather than silently creating a new questioning workflow.

## Documentation and long-running work

**Grill with Docs** composes Grilling and Domain Modeling. The user must settle each decision before canonical documents are changed. Existing Mago-owned technical specs and ADRs are handed to Mago for validation and authorship; independently authorized documents can be written by the agreed owner.

**Domain Modeling** handles `GLOSSARY.md`, `GLOSSARY-MAP.md`, scenarios and candidate ADRs. It preserves existing terminology and presents conflicts instead of renaming files automatically.

**Wayfinder** is for a destination that cannot be resolved in one session. It records decision dependencies, resolved choices and not-yet-specifiable fog in a Markdown map or an authorized tracker. These are decision tickets, not implementation work packages. Never make a roadmap from them by silently assigning priority or deadlines.

## Review and retrospectives

**Code Review** freezes the compared refs, then separately inspects coding standards and the original spec. It can be used as a narrow specialist by [Audit Spec Implementation](../skills/audit-spec-implementation/SKILL.md) when supported. Lint output and code smells do not prove runtime correctness; an adequate oracle must do that.

**Retro** reviews an actual execution session and proposes better tests, environment checks, navigation references and instructions. Candidate improvements can be routed to Software Improvement Loop or Skill Booster. Raw logs and secrets do not become reusable Graph lessons.

## Ownership, compatibility and license

Nomia owns governance, Mago owns technical planning, Magia owns implementation. The new skills do not change internal schema/contract identities or permissions. Parallel subagents are optional; report actual availability and whether independent review ran. Each new skill includes an exact pinned upstream reference and the original MIT license (Matt Pocock); RhapsodIA adaptations are independently maintained.
