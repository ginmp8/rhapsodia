# Refine mode

Use refine mode when the request asks to minimally update one existing spec package so execution can continue with less ambiguity, without changing the initiative boundary.

## Scope
- planning-only by default
- operate on exactly one existing spec package under `<cycle_version>/specs/<spec_id>/`
- preserve correct history and done state
- change only what is required

## Core protocol
- read existing canonical planning docs first; do not refine blind
- preserve truthful content
- keep the smallest safe change
- separate intent, execution, validation, and notes
- record assumptions and ambiguities in `notes.md`
- keep reasoning guidance on every non-trivial task
- use specialist metadata only when it materially clarifies execution
- finish with the mandatory final review

## Canonical artifact mapping
Refine only these canonical files:
- `manifest.yaml`
- `prd.md`
- `tasks.md`
- `validation.md`
- `notes.md`

If source material refers to `MANIFESTO.yaml` or `DOCS_ROOT`, reinterpret those references into the current spec package and do not reproduce the legacy names.

## Refinement rules
- preserve done history
- update future todo work precisely instead of rewriting the whole plan
- re-evaluate reasoning only where ambiguity, scope, or evidence changed
- do not mark tasks done without matching evidence
- if blocker state changes materially, update `notes.md` in the same pass
- require concrete validation and coverage expectations when changed business logic is relevant
- if remaining work is still too broad, add a bounded future refinement or decomposition task only when justified

## Final review
Review in this order:
1. `manifest.yaml`
2. `prd.md`
3. `validation.md`
4. `notes.md`
5. architecture impact when relevant

After review:
- keep all planning docs internally consistent
- add only minimum new in-scope tasks
- do not create false completion claims
