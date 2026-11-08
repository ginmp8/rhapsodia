---
name: wayfinder
description: "Plan complex, multi-session work by mapping the decision frontier, unresolved dependencies and evidence-backed decisions into a durable map. Use when a goal cannot be clarified in one interview. Not for implementing tasks, owning Nomia governance or replacing Mago technical task planning."
---

# Wayfinder

## Mission and ownership

Build a durable **decision map** for problems too large or ambiguous for one Grilling session. The map records the route to a well-defined destination, not a backlog of implementation tickets. **Nomia** owns roadmap, priority, status, stakeholders and delivery governance; **Mago** owns requirements and technical work packages; **Magia** owns execution. Wayfinder may provide decision evidence to those owners but never change their canonical artifacts unilaterally.

## Modes

- **Chart:** define a destination, assess known decisions, and identify the resolvable decision frontier and the unspecifiable *fog*.
- **Resolve:** select one unclaimed frontier decision and complete its fact-finding, scenario or user interview.
- **Reconcile:** update the map after new evidence, resolved decisions, stale pointers or concurrent changes; never fabricate progress.

## Quick start

1. Establish the user-approved destination and durable map location. Read any existing map and owner contracts. Use the smallest local Markdown map unless an issue tracker is already configured **and** issue publication is authorized.
2. For a new map, use **grilling** (and **domain-modeling** when terminology matters) through native invocation or readable instructions when available; otherwise ask equivalent bounded frontier questions inline and test ambiguous terms with concrete scenarios. Missing a named-skill invocation API does not prevent decision discovery. Create only decisions that can be precisely stated now; defer vague future needs to *Not yet specified*.
3. Each decision has an ID, human-readable title, type (`research`, `prototype`, `grilling`, `task`), dependencies, state and evidence pointer. Follow [decision-map contract](references/map-contract.md).
4. During Resolve, choose an **unclaimed, unblocked** decision. Claim atomically only if the tracker supports a safe claim mechanism; on local files, check current state before updating. Never assume another worker has not claimed it.
5. Resolve the selected decision through evidence retrieval, user interaction or an authorized optional specialist. Record the exact answer and primary source; close the decision only when required evidence exists.
6. Recompute downstream dependencies and fog. Preserve decisions as indexed links, not copied authoritative claims. Stop after one resolution per session unless the user explicitly authorizes a wider batch.
7. Summarize frontier, blocked items, out-of-scope items, sources, next owner and proposed handoff. Do not auto-execute the planned work.

## Non-negotiable rules

- The map is an index to decisions, not a competing Nomia roadmap or Mago technical plan.
- Facts are not user choices. Investigate what approved tools can establish; ask the user for authority and genuine trade-offs.
- A Grilling HITL decision must not be resolved by the agent answering its own questions.
- Publication, issue edits, branch pushes and assignment changes require explicit user/host authority and freshness checks.
- Prefer no subagent over invented delegation. Fresh independent context is required where the host supports actual delegation.
- In RhapsodIA agent sessions, preserve required runtime/graph setup and source-bound evidence; no skill text overrides the host session guard.

## Host portability

A RhapsodIA session uses its existing runtime/graph prerequisites; other Agent Skills hosts need no RhapsodIA bootstrap. If persistent storage or tracker writes are unavailable, return the complete Markdown map for the user to save and explicitly mark persistence, claims and issue creation as **not performed**. Do not silently infer a durable state transition.
