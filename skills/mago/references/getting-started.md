# Mago Getting Started

> Storage binding: `artifact-native` is the default. Use `legacy-board` only when explicitly selected; Board/cycle/registry mechanics never override native storage or identity rules.

Use this page when Mago is selected but the internal mode or next planning step is unclear. It is an onboarding projection, not a lifecycle, source of truth, or storage authority.

## Route by intent

| User state | Mago action | Hand off/block instead when |
|---|---|---|
| "I have an idea or demand" | inspect the resolved Nomia handoff or supplied evidence, then clarify technical planning inputs | requester, owner, business priority, due date, roadmap, or stakeholder facts must be authored by Nomia |
| "I need to understand the repository" | use `discovery` read-only first and produce bounded repository evidence | the request is to edit code, run product tests, deploy, commit, or open a PR; route to Magia |
| "I need a plan" | resolve native planning identity, rigor/lifecycle, and one mode; create only evidence-triggered artifacts | owner/root/work item/evidence is unresolved enough that mutation would invent truth |
| "I need to change an existing spec" | refine canonical Mago intent and produce a non-authoritative change delta | runtime evidence must be changed; Magia owns it |
| "I need to know what happens next" | report the next evidence-backed planning action or render the planning compass | the requested status is delivery governance; Nomia owns it |
| "I need tasks grouped for execution" | project dependency-safe execution waves without executing tasks | Magia must still resolve actual file/contract/runtime overlap before parallel execution |

## Minimum start sequence

1. Resolve `repo_root`, the Mago owner/artifact root, `work_item_id` or existing planning identity, evidence source, intended outcome, rigor profile, lifecycle stage, and exactly one mode before writes.
2. If a new native planning identity is needed, use `scripts/native_planning.py identity` and reuse the resulting identity; do not mint a second identity for retries.
3. If `legacy-board` is explicitly selected, resolve its Board/cycle/registry identifiers and then use the retained legacy contracts. Existing Board files alone never select this profile.
4. Record unresolved facts as assumptions, questions, or blockers; use `references/clarification-prioritization.md` when several unknowns compete.
5. Select only artifacts triggered by `references/artifact-decision-matrix.md`; templates are structural aids, never write triggers.
6. Validate with the narrowest relevant native/domain validators. Standard/governed planning requires traceability; governed work also requires the triggered risk/security/decision evidence.
7. Publish native artifact metadata only after source validation, then validate the returned `artifact_actions`; publication integrity is not product-test evidence.
8. Handoff only validated planning intent. Reconcile Magia execution evidence read-only and preserve its provenance.

If a selected mode reference contains `BOARD_ROOT`, cycle, registry, manifest, or generated catalog/queue instructions while native mode is active, treat those mechanics as legacy-only. Do not infer a replacement native path that the native contract does not define.

## Profile quickstart

### Quick

Use only for one bounded, reversible, well-understood change with known validation and no material contract, migration, auth/security/privacy/compliance, multi-repository, architecture, or irreversible-data trigger. Native minimum: `planning-identity.json`, `prd.md`, `tasks.md`, and `validation.md`.

### Standard

Use for normal repository changes requiring explicit requirements, design reasoning, dependencies, compatibility expectations, tasks, notes, and validation. Native minimum: quick set plus `notes.md` and only triggered technical artifacts.

### Governed

Use for regulated, security-sensitive, financial, privacy, migration, public-contract, operationally risky, cross-service, or multi-repository work. Every trigger family must be satisfied or explicitly marked not applicable with evidence; governed handoff also requires the stronger clarification/traceability contracts.

## Typical entry prompts

- `Use Mago to inspect this repository and identify planning work without editing code.`
- `Use Mago to turn this resolved Nomia handoff into the smallest safe native plan for work item X.`
- `Use Mago to refine this existing planning identity and show added, modified, removed, and preserved behavior.`
- `Use Mago to create the technical design and planned ADRs for this work item without implementation.`
- `Use Mago to show the current planning stage, missing evidence, pending gates, and next planning action.`
- `Use Mago to project dependency-safe execution waves for Magia without executing tasks.`

## What Mago never does

Mago does not invent governance facts, implement product code, execute product tests, fabricate runtime evidence, certify deployment, accept business risk, rewrite Magia execution evidence, or treat generated projections as canonical source state.
