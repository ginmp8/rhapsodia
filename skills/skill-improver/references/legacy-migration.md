# Legacy `skill-improvement` Migration

`skill-improver` is the canonical implementation owner. The former `skill-improvement` package is a compatibility shim only and must not maintain a parallel review/fix/reproducibility engine.

## Capability mapping

| Legacy surface | Canonical replacement | Migration rule |
|---|---|---|
| `skill-improvement` natural-language/command alias | `skill-improver` | Route the request to the canonical skill and preserve explicit user parameters. |
| `.skill-improvement/` session files | `.skill-improver/` evidence/state root | Do not create new legacy state. Existing legacy state is read-only historical evidence. |
| `skill_loop_state.py start/advance` | canonical runner lifecycle | No direct state mutation replacement; the runner records iterations automatically. |
| `skill_loop_state.py status` | `scripts/skill_improver_status.py` | Derive status from canonical evidence rather than a second state store. |
| legacy cancellation | `scripts/cancel_skill_improver.py` | Write the canonical stop request; preserve accepted changes. |
| legacy structural-review helper | frozen evaluator + structural change gate + `Skill Quality Reviewer` when available | Do not copy the old reviewer into the canonical package. |
| `critical/major/minor` triage | `references/severity-lifecycle.md` | Use the stable canonical taxonomy and `needs-verification`. |
| default `max_iterations=20` | default `max_iterations=3` | This safety default intentionally changes. Preserve an explicit legacy/user-supplied value. |
| `<skill-improvement-complete>` | canonical termination status | Shim may emit the marker only for validated `accepted`/`completed` outcomes. |

## Compatibility commitments

- Preserve explicit target path, evaluator, iteration budget, and output requests from a legacy invocation.
- Preserve the meaning of cancellation: accepted edits remain, in-flight/rejected candidates are not promoted.
- Do not silently translate an unbounded legacy request into unbounded execution; require the canonical explicit infinite-mode acknowledgement.
- Treat old `.skill-improvement/` files as historical evidence only. Do not delete them automatically.
- Do not claim legacy activation/behavioral parity without executed paired scenarios.

## Removal condition for the shim

Remove the compatibility shim only after consumer tracing finds no remaining explicit `skill-improvement` invocations or package-path dependencies in the deployment scope and an announced migration window has elapsed.
