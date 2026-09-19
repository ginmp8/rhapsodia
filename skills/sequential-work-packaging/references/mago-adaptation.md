# MAGO adaptation rules

Use this reference only when the request explicitly involves MAGO planning or legacy `.MAGO-*` entrypoints.

## Authority boundary

Current MAGO and Sequential Work Packaging use different canonical identity/path models. Do not pretend they are the same system.

- Current MAGO owns its `BOARD_ROOT`, cycle/registry identity, package paths, richer artifact set, transaction semantics, and typed ecosystem handoffs.
- Sequential Work Packaging owns the separate `<cycle_version>/spec-catalog.yaml` plus `specNNN` convention defined by this skill.
- Never rewrite a current MAGO `spec-<date>-<feature-key>` identity into `specNNN` inside `BOARD_ROOT`.
- Never hand-edit MAGO generated catalog/queue projections or replace the MAGO registry with this skill's `spec-catalog.yaml`.
- Never discard MAGO-only artifacts such as `technical-design.md`, registry records, cycle metadata, traceability, priority fields, or ecosystem handoffs because they are outside this skill's canonical five-file spec package.

When a current MAGO board/package is the source, this skill is an **external compatibility adapter/projection** only. MAGO remains authoritative. Write the sequential package outside MAGO `BOARD_ROOT`, preserve source hashes/identity mapping, disclose losses, and never round-trip edits back into MAGO without MAGO's own adapter/reconciliation workflow.

## Current MAGO mode mapping

Map only when the caller explicitly wants a Sequential Work Packaging projection or equivalent standalone workflow:

| MAGO intent | Sequential mode | Constraint |
|---|---|---|
| `order` | `order` | project registry/order evidence; do not replace MAGO registry |
| `adapt` | `normalize` | legacy/current MAGO source remains read-only; output is non-authoritative |
| `prepare-define` / `define` | `define` | only map the shared planning subset |
| `refine` | `refine` | preserve stable task ids and done history |
| `reshape-tasks` | `decompose` | only when the intent is splitting broad remaining tasks |
| `define-tasks` | `define` | tasks-focused input may still require this skill's full canonical package before execution-ready status |
| `refine-tasks` | `refine` | do not synthesize missing MAGO-only phases/fields as sequential truth |
| `technical-design` and other MAGO-only modes | no automatic mapping | keep as external evidence/unknown artifact; do not flatten into another file silently |

MAGO's `business_priority`, `technical_criticality`, `execution_sequence`, registry lifecycle, and ecosystem handoff fields are not owned by this skill. Preserve them only as attributed external evidence when relevant.

## Legacy `.MAGO-*` compatibility

For legacy standalone prompts that do not resolve to a current MAGO `BOARD_ROOT`/registry:

- `.MAGO-DEFINE`
  - ordering request -> `order`
  - one sequential spec package -> `define`
- `.MAGO-REFINE` -> `refine`
- `.MAGO-DECOMPOSE` -> `decompose`

Legacy names are input aliases only:

- `MANIFESTO.yaml` -> `manifest.yaml`
- `PRD.md` -> `prd.md`
- `TASKS.md` -> `tasks.md`
- `VALIDATION.md` -> `validation.md`
- `NOTES.md` -> `notes.md`
- `FEATURE_ORDER.yaml` -> `spec-catalog.yaml`
- `docs/current` -> caller-selected sequential cycle destination

Do not preserve those legacy paths as authoritative output.

## Compatibility and loss report

When projecting from current MAGO, record at least:

- authoritative source: MAGO;
- MAGO board/cycle/spec identity and exact source hashes;
- sequential destination identity;
- mapped fields/artifacts;
- MAGO-only fields/artifacts retained only as source evidence;
- omitted or lossy semantics;
- unknown files preserved;
- whether round-trip is unsupported;
- validation outcomes.

If a loss would change planning meaning, block rather than claim compatibility.

## Reproducibility gates

Apply `references/reproducibility-contract.md` before mutation. Resolve canonical paths, preserve stable identities, require expected-before hashes, stage candidates outside live targets, validate before/after invariants where applicable, commit atomically, and emit a machine-readable receipt. Unknown files are preserved. A repeated equivalent pass must be `no_change`, not a formatting rewrite.
