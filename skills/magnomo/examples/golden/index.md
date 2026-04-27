# Magnomo Golden Examples

These examples demonstrate intended Magnomo patterns without turning governance artifacts into implementation plans.

## Directory Structure

```text
.github/skills/magnomo/examples/golden/
|- index.md
|- validation-commands.md
|- 01-delivery-intake-github-issue/
|  |- input.md
|  |- ops.yaml
|  |- status.md
|  |- expectations.md
|- 02-delivery-triage-stakeholders/
|  |- input.md
|  |- ops.yaml
|  |- stakeholder-brief.md
|  |- status.md
|  |- expectations.md
|- 03-replanned-demand-preserved-history/
|  |- input.md
|  |- ops.yaml
|  |- replanning.md
|  |- status.md
|  |- expectations.md
|- 04-portfolio-multiple-specs/
|  |- input.md
|  |- portfolio.yaml
|  |- portfolio.md
|  |- expectations.md
|- 05-roadmap-large-initiative/
|  |- input.md
|  |- roadmap.yaml
|  |- roadmap.md
|  |- adr-records.md
|  |- feature-map.yaml
|  |- expectations.md
|- 06-roadmap-to-spec-handoff-mago/
|  |- input.md
|  |- roadmap.yaml
|  |- feature-map.yaml
|  |- expectations.md
|- 07-feature-report-after-delivery/
|  |- input.md
|  |- input-magia-execution-evidence.yaml
|  |- feature-report.md
|  |- internal-notes.md
|  |- expectations.md
|- 08-release-notes-stakeholders/
|  |- input.md
|  |- release-notes.md
|  |- internal-notes.md
|  |- expectations.md
|- 09-rfc-proposal-roadmap-handoff/
|  |- input.md
|  |- rfc-proposals.md
|  |- expectations.md
|- 10-adr-record-roadmap-decision/
   |- input.md
   |- adr-records.md
   |- expectations.md
```

## What Each Example Proves

1. Delivery intake from a GitHub issue: preserve source context while leaving owner, stakeholders, target date, and priority unknown until triage.
2. Delivery triage with stakeholders and owners: turn intake into owned delivery metadata and a business-facing brief.
3. Replanned demand with preserved history: update current delivery state while keeping append-only replan history.
4. Portfolio view across multiple specs: summarize multiple deliveries, blockers, risks, and replans without adding execution source-of-truth fields.
5. Roadmap for a large initiative: decompose an initiative into feature candidates without writing Mago PRD, task, or validation-plan content.
6. Roadmap-to-spec handoff for Mago: hand off a ready feature as upstream evidence for Mago while keeping Magnomo ownership clear.
7. Feature report after delivery: use supplied execution evidence as input and produce human-readable delivery reporting.
8. Release notes for stakeholders: communicate user impact and rollout without exposing internal notes or claiming unsupported availability.
9. RFC proposal for roadmap handoff: capture an undecided governance proposal with RACI, assumptions, criteria, options, recommendation, and pending outcome.
10. ADR record for roadmap decision: capture an accepted governance decision as append-only history with context, alternatives, impact, links, and supersession state.

## Validation

Use `scripts/validate_golden_examples.py --skill-root <skill-root>` as the canonical single-command gate for this directory. The expanded command list lives in [validation-commands.md](validation-commands.md) for reviewability, but package readiness should rely on the runner so new validators and paths are checked consistently.

## Common Rules Shown

- Unknown facts stay `null`, `unknown`, or explicitly described as not recorded.
- Branches, pull requests, commits, checks, review status, deployment state, and last commit age are not maintained as Magnomo source-of-truth fields.
- Mago receives roadmap and feature-map handoff evidence only.
- RFC proposals remain mutable while under review; accepted material decisions are recorded as ADR records.
- Execution evidence is consumed as input evidence; Magnomo does not rewrite it.
