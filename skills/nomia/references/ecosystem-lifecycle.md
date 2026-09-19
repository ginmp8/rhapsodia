# Ecosystem lifecycle and next-owner map

The three skills are independent packages with coordinated contracts. Choose the owner from the current lifecycle phase, not from the broad goal.

| Phase | Owner | Canonical result | Next owner |
|---|---|---|---|
| Intake and delivery governance | Nomia | governance facts, roadmap, status, decision, `nomia_to_mago` | Mago |
| Technical definition | Mago | PRD, design, tasks, validation plan, `mago_to_magia` | Magia |
| Implementation and validation | Magia | code, tests, execution evidence, `magia_to_mago` and/or `magia_to_nomia` | Mago or Nomia |
| Planning reconciliation | Mago | conformance/deviation result, revised plan or `mago_to_nomia` | Magia or Nomia |
| Delivery and release closure | Nomia | governance decision, status, feature report, release/internal notes | closed or new intake |

## Independent package invariant

- Nomia, Mago, and Magia remain separately installable, invokable, testable, and packageable skills.
- Resolve and load exactly one current owner for each phase. Do not concatenate the three `SKILL.md` files or introduce a cross-owner writer to simulate a monolithic skill.
- Shared contracts are byte-equivalent local copies validated at release time; no skill reads or executes a peer package at runtime.
- A multi-intent request traverses owner phases through typed handoffs instead of transferring or merging authority.

## Context loading rule

Load the shared lifecycle/routing contract and only the selected owner's branch resources. Peer-package internals may be consumed only as explicitly supplied, attributed, read-only evidence. This keeps the distributed capability usable without paying the context cost of all three control planes at once.

## Multi-intent rule

Decompose the request into phases, resolve the first owner, perform only that owner's work, and emit the typed handoff needed by the next owner. Never merge ownership merely to reduce handoffs.

## Ambiguous requests

For requests such as “continue the feature”, “finish the spec”, or “update status and fix it”, resolve the current canonical board/spec state and the requested lifecycle dimension before mutation.

## Coordinated release rule

Exact-version compatibility requires staging and validating all three candidate packages before any live switch. Promote the independently packaged skills as one coordinated release decision and roll back all three to the prior validated set if promotion fails.
