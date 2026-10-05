# Change Review

## Purpose
Turn a noisy file/diff surface into a reader-ordered explanation of what changed, why it matters, how the design works, and where the implementation lives.

## Workflow
1. Resolve target/base/head or working-tree scope and inspect the changed-file list.
2. Write a one-paragraph `What / Why`; include `Why` only when requirements, PR/issue text, ADRs, commits, or traces actually support it.
3. Preserve explicit user requirements in their own words when available; otherwise omit the section.
4. Assign every changed file to exactly one lens.
5. Classify non-implementation lenses first: tests, docs, generated/lock, config/build, fixtures/snapshots, rename/move, formatting-only, import-only.
6. Group remaining implementation files by responsibility/design role in the order a reader should understand them. Keep a file whole unless two unrelated changes genuinely require separate lenses.
7. Build a semantic change map when more than one meaningful lens exists.
8. Add one design visual selected from relationship signals; use a second only when it covers a distinct dimension such as data model vs temporal interaction.
9. Walk implementation from the user/system entry point through the mechanism and invariant-bearing locations. Include unchanged bridge nodes when they are necessary to understand the path.
10. Finish with material risks/invariants and evidence locators; re-check the whole explanation for contradictions.

## File-lens rules
- Every known changed file appears once; no uncategorized remainder is allowed.
- Lens names describe responsibility, not directories: prefer `Credential validation` over `Application folder`.
- Tests/docs/generated/config lenses are usually supporting context, not the center of the narrative.
- A large function may be summarized semantically when line-by-line detail would obscure the change; never omit the invariant it implements.

## Default section order
`What / Why -> Requirements (if known) -> Change Map -> Design -> Implementation -> Risks/Invariants -> Evidence`

For a tiny self-evident change, collapse sections rather than forcing ceremony.
