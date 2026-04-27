# ADR Artifacts

## adr-records.md

Append-only governance decision log owned by Magnomo. Use after a material decision is made.

Required sections:

- `# ADR Records`
- `## Entries`

Use one `### YYYY-MM-DD - Title` heading per ADR entry. The title must describe the decision as a noun phrase or imperative outcome, not a question.

Each ADR entry must include these labels in order:

- `Status`
- `Decision`
- `Context`
- `Reason`
- `Alternatives`
- `Impact`
- `Decision Maker`
- `Links`
- `Supersedes`

Quality rules:

- Record the decision after it is made; keep undecided items in `rfc-proposals.md` or `roadmap.md` `Open Decisions`.
- Include honest downsides or accepted trade-offs in `Impact` or `Reason`.
- Include why rejected alternatives were not chosen when alternatives exist.
- Supersede or correct with a new entry instead of editing old historical meaning.
- Keep code-only architecture ADRs outside Magnomo unless the user explicitly frames them as roadmap or governance decisions.

