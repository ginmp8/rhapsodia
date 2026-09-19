# Resource Classification

Classify every candidate before deletion, consolidation, or retention. The classification is evidence, not permission by itself; mutation must also pass the canonical deletion gate.

## Canonical state taxonomy

| State | Meaning | Default action |
|---|---|---|
| `used` | Reachable from `SKILL.md`, a host adapter, a referenced resource, local link, script import/path, template/validator/example/eval consumer, or package metadata. | Preserve. |
| `integrable` | Useful support resource that is not currently reachable, but is aligned with the skill and may be intentionally dormant. | Integrate or explicitly retain. |
| `duplicate` | Exact duplicate with mechanically identical content and a known canonical copy. | Consolidate only after consumer tracing and validation. |
| `obsolete` | Replaced or no longer valid, proven by explicit target/user/migration/validator evidence. | Remove only after explicit approval, rollback, and validation. |
| `generated` | Cache, build output, temporary/local report, generated package residue, or other reproducible artifact not used by the package. | Eligible for cleanup after preflight. |
| `blocked` | Protected by policy, evidence role, archive protection, secret-like identity, symlink/path risk, user instruction, or safety boundary. | Do not mutate. |
| `unknown` | Evidence is insufficient or conflicting. | Retain. Never auto-delete. |

Do not create extra top-level states such as `placeholder` or `duplicated`. Scaffold/placeholder markers and similarity scores are evidence signals attached to one of the canonical states.

## Classification precedence

Use this fail-closed precedence when multiple signals apply:

1. `blocked` — protection or unsafe path wins.
2. `used` — reachable/consumed resource wins over cleanup heuristics.
3. `generated` — only when not reachable or protected.
4. `duplicate` — only exact duplicates that are not required consumers themselves.
5. `integrable` — unreferenced support resource with plausible package role.
6. `obsolete` — only when explicit evidence establishes replacement/removal intent.
7. `unknown` — default when evidence is insufficient.

`obsolete` is normally reviewer- or user-established rather than inferred by the inventory script.

## Usage and reference tracing

Before declaring a resource unused, trace at least:

- `SKILL.md` references and local Markdown links;
- transitive links from referenced resources;
- host adapter paths such as icon/assets metadata;
- script imports and explicit local paths;
- template, validator, example, eval, packaging, and report-template consumers;
- replacement/migration notes and compatibility aliases;
- exact external references when the user provides them.

A resource indirectly referenced through another reference is `used`.

Absence from a shallow grep, import list, or one mode does not prove obsolescence.

## Duplicate rules

Exact byte/hash equality may establish an exact duplicate mechanically. Choose a canonical copy deterministically, preferring an already-used/reachable copy and then canonical path ordering.

Partial similarity is only a review candidate. Before consolidation compare:

- mode and audience;
- unique constraints and examples;
- activation/scope implications;
- validator or migration role;
- external compatibility references.

A partial duplicate must not be automatically classified `duplicate` or deleted.

## Scaffold and template guard

A file containing `TODO`, placeholders, example tokens, or template variables may be legitimate. If it is referenced by the workflow or copied/filled at runtime, classify it `used` even if it looks like scaffold.

Only explicit evidence can establish that scaffold is obsolete.

## Generated artifact guard

Generated/cache/build artifacts may be classified `generated` only when they are not reachable/required by the package and are not protected evidence. Empty build/cache directories are not meaningful package content by themselves.

## Protected evidence guard

Fixtures, expected outputs, golden files, snapshots, benchmark reports, evaluator evidence, receipts used for comparison, secrets/credentials, archives, and user-declared protected files are `blocked` unless the user explicitly changes the protection policy for a non-destructive purpose.

## Classification evidence

Strong evidence includes:

- deterministic reference/consumer graph;
- file hash proving exact duplication;
- package metadata or manifest references;
- target documentation naming a replacement or deprecation;
- user instruction explicitly marking a resource obsolete;
- validator/test evidence;
- migration completion evidence with updated consumers.

Weak signals such as naming, age, TODO text, apparent lack of imports, or similarity alone cannot justify deletion.

## Report shape

| Path | State | Evidence | Decision | Risk | Validation |
|---|---|---|---|---|---|
| `path/to/file` | `used` | Reachable from `SKILL.md` through `references/index.md` | Preserve | Low | Reference graph |
