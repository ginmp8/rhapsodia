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

## Long-input selection and coverage (caller-side)

Use when a task spans long documents, many files, or dispersed evidence and a relevant
constraint may be missed. This is a **selection/checking protocol**, not a new CLI
operation or a guarantee that any model reliably attends to every input position.

1. Convert the task into answer-critical obligations: claims/questions, required
   contracts, dependencies, counterevidence and expected source boundaries. For each,
   locate an exact path and line range (or record `unknown` and seek a bounded read).
2. Explore section/symbol indexes and links before selecting snippets. Check relevant
   material across source regions, including the middle where warranted; search
   paraphrases and related symbols, not literal keyword hits alone. Avoid indiscriminate
   whole-file inclusion or fixed first/last placement rules.
3. Classify each located span as required or optional. Keep a small caller-side coverage
   map: obligation -> source/lines -> supporting/conflicting/unknown -> pack inclusion.
   Preserve multi-span dependencies, exceptions, trust labels and source provenance.
4. When required evidence will not fit, narrow/retrieve with the owner or enlarge an
   authorized budget within bounds. Do not downgrade required material to optional,
   silently summarize away qualifiers, or pretend a truncated pack is complete.
5. After `pack`/`pack-verify`, compare the included required anchors against the map;
   show missing, conflicting and omitted optional evidence. Revalidate source pins.

For claims of improved long-context model outcomes, separately test exact and paraphrased
facts placed near the beginning, middle and end, with distractors and missing/contrary
sources, under fixed model/runtime/evaluator identity. CLI checks alone show only pack
integrity and selection metadata, not model recall or semantic accuracy.

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
