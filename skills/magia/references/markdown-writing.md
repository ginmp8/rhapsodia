# Markdown Writing

Apply to generated or updated MAGIA Markdown artifacts, especially implementation-notes.md and validation-evidence.md. Treat notes.md and validation.md as Mago-owned planning inputs; legacy execution content is read only by ADAPT mode during best-effort conversion to current MAGIA-owned artifacts.

## Rules

- Keep canonical sections required by the active template/mode.
- Use one H1 when expected; keep heading levels sequential and descriptive.
- Keep sections scannable with short paragraphs, small lists, and blank lines around headings/lists/fences.
- Use descriptive link text; avoid bare URLs and vague `here`.
- Use real Markdown lists, rare nesting, no fake bullets or decorative emoji.
- For images, use meaningful alt text or remove if they add no value.
- Use inline code for file names, commands, ids, YAML keys, and literal statuses; fenced code with language tag for multi-line snippets.
- Use tables only for true tabular comparisons.
- Mark examples as examples, not repository truth.
- Use repository-relative POSIX paths; avoid Windows or absolute local paths unless documenting unavoidable external literals.
- Keep MAGIA-created or updated durable docs under `BOARD_ROOT`.
- Prefer plain direct language; explain non-obvious jargon briefly; preserve nuance.
- Preserve canonical headings, field labels, and checklist ordering.
- When toggling a checklist item or execution-log line, edit it in place; keep position and attached context.
- Do not sort checklist items or execution logs by completion state.
- validation-evidence.md: record evidence and residual gaps for fast judgment.
- implementation-notes.md: keep assumptions, findings, decisions, follow-ups, and blockers distinct.
- notes.md and validation.md: preserve as planning inputs; do not append new MAGIA execution evidence there.
