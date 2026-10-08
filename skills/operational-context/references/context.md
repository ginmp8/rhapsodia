# Task context and stable prefixes

`pack` requires `task_id`, `goal`, and 1..64 `required` file references. `optional` has at
most 128. A ref is `{"path":"src/file.py","role":"source"}`; optional `start_line`
and `end_line` are inclusive and must appear together. Roles are source, contract,
evidence, blocker, instruction and tool-schema. A role label never promotes source trust.

Default `budget_bytes` is 8192 (128..65536). Default `include_text` is false. A whole-file
SHA-256 is retained even when a line range is selected. Per-file input is at most 8 MiB;
inline selected text at most 32 KiB. Inline content also requires `approved_content:true`.

Required records and the complete optional-omission list must fit before any optional
record is added. Required overflow raises BUDGET_EXCEEDED without storing a pack.
Optional records are considered in declared order. The caller selects relevance; the
composer does not invent dependencies, silently truncate contracts, or run a summarizer.
An unavailable optional source still needs explicit caller removal/reselection rather
than silent omission that hides a missing source.

A returned `task-context/v1` contains its workspace scope, required/optional pins,
`omitted_optional`, `required_complete`, `incomplete`, exact `output_bytes`, and `pack_id`.
`incomplete:true` means optional context is omitted, not that required gates can be skipped.
The ID excludes the ID and byte-accounting fields; all other content is hash-bound.

`pack-save` is the explicit cache write. Its storage `id` differs from `pack_id` because
the storage envelope includes kind/scope. `pack-use` takes `{"id":"<storage SHA-256>"}`
and revalidates live pins. `pack-verify` accepts the complete returned pack read-only.
Do not use stale content merely because the old pack is internally hash-consistent.

`prefix` takes `static_refs`, `dynamic_tail`, `approved_content:true`, optional budget.
Static text stays in caller-declared order; per-turn task text stays in the separate tail.
The prefix digest is stable across tail changes. This does not configure API caching,
control hidden host prompts, or prove a cache hit. Hosts must actually preserve the prefix.
A smaller logical input and a cheaper cached prefix are different measurements.

`output-card` takes a source `path`, `observed_status` (passed/failed/blocked/not-run/unknown)
and optional `budget_bytes`. It returns path, hash, size and caller-observed status without
log text. Optional `include_excerpt:true` requires `approved_content:true`; `tail_lines`
is 1..200. Whole lines are removed to fit; `content_omitted` and line bounds reveal loss.
The full log remains at its exact source reference. Never infer success from a log card.
