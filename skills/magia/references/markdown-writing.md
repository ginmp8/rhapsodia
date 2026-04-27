# Markdown Writing

Apply these rules to generated or updated notes.md and validation.md.

## Rules

- keep the canonical section set required by the active template or mode
- use one H1 only when the file format expects it; keep heading levels sequential
- use descriptive headings with natural capitalization
- keep sections scannable with short paragraphs, small lists, and blank lines around headings, lists, and fenced blocks
- use descriptive link text; avoid bare URLs and vague text such as `here`
- use real Markdown lists; keep nesting rare; never fake bullets with symbols or emoji
- if an execution doc includes an image, use meaningful alt text or remove the image if it adds no value
- use inline code for file names, commands, ids, YAML keys, and literal status values
- use fenced code blocks for multi-line snippets and add a language tag when useful
- use tables only for genuinely tabular comparisons
- mark examples clearly as examples, not repository truth
- use repository-relative POSIX paths such as a repository-relative board notes path; avoid backslashes, Windows paths, and absolute machine-local paths unless documenting an unavoidable external literal
- keep MAGIA-created or MAGIA-updated durable docs under `BOARD_ROOT`
- prefer plain, direct language; explain non-obvious jargon briefly; preserve factual nuance
- avoid decorative emoji and noisy emphasis
- preserve canonical headings, field labels, and checklist ordering when the file already follows the expected structure
- when toggling a checklist item or updating an execution-log line, edit the existing list item in place; keep its relative position and keep any attached context immediately below it
- do not sort checklist items or execution-log entries by completion state
- validation.md: record evidence and residual gaps for fast human judgment
- notes.md: keep assumptions, findings, decisions, follow-ups, and blockers distinct
