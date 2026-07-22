# Ecosystem lifecycle and next-owner map

The three skills are independent packages with coordinated contracts. Choose the owner from the current lifecycle phase, not from the broad goal.

| Phase | Owner | Canonical result | Next owner |
|---|---|---|---|
| Intake and delivery governance | Nomia | governance facts, roadmap, status, decision, `nomia_to_mago` | Mago |
| Technical definition | Mago | PRD, design, tasks, validation plan, `mago_to_magia` | Magia |
| Implementation and validation | Magia | code, tests, execution evidence, `magia_to_mago` and/or `magia_to_nomia` | Mago or Nomia |
| Planning reconciliation | Mago | conformance/deviation result, revised plan or `mago_to_nomia` | Magia or Nomia |
| Delivery and release closure | Nomia | governance decision, status, feature report, release/internal notes | closed or new intake |

## Multi-intent rule

Decompose the request into phases, resolve the first owner, perform only that owner's work, and emit the typed handoff needed by the next owner. Never merge ownership merely to reduce handoffs.

## Ambiguous requests

For requests such as “continue the feature”, “finish the spec”, or “update status and fix it”, resolve the current canonical board/spec state and the requested lifecycle dimension before mutation.
