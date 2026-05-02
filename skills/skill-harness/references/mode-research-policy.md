# Mode and Research Policy

Use to select evidence sources.

## Modes

`auto`: user gives a target skill and expects the harness to find improvements. Allowed: target contents, user target files, public primary/current research for external frameworks or tools, permission-aware internal sources for clearly work-related requests, user-supplied benchmark/hardening/evaluation reports. Inspect first, research concrete weaknesses, prefer primary/current sources, record sources.

`context`: user restricts work to supplied context or asks for controlled rewrite. Allowed: target contents, conversation context, explicitly provided files/links the environment can open. Forbidden unless mode changes: public web, internal search not supplied by user, domain rules absent from target/context. Change only what context supports; state missing context instead of guessing.

`full`: user supplies context and wants broader research. Allowed: context-mode sources plus target/context-derived research, primary docs, current best practices, comparable mature skills, public references. Extract user context first, inspect target, verify/challenge context, resolve conflicts, keep binding constraints visible.

## Conflict Handling

Prefer user-declared desired behavior; target repository truth for implementation facts; primary/current external sources; measured harness results over expectations. Record unresolved conflicts and do not bake them into the target as fact.

## Research Output

Record research questions, sources used, adopted claims, rejected/unused claims, context constraints, and remaining unknowns.
