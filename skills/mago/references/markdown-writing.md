# Markdown Writing

Apply these rules to generated or updated prd.md, technical-design.md, tasks.md, notes.md, and validation.md.

## Rules

- keep the canonical section set required by the active template or mode
- use one H1 only when the file format expects it; keep heading levels sequential
- use descriptive headings with natural capitalization
- keep sections scannable with short paragraphs, small lists, and blank lines around headings, lists, and fenced blocks
- use descriptive link text; avoid bare URLs and vague text such as `here`
- use real Markdown lists; keep nesting rare; never fake bullets with symbols or emoji
- if a planning doc includes an image, use meaningful alt text or remove the image if it adds no value
- use inline code for file names, commands, ids, YAML keys, and literal status values
- use fenced code blocks for multi-line snippets and add a language tag when useful
- use tables only for genuinely tabular comparisons
- mark examples clearly as examples, not repository truth
- use repository-relative POSIX paths such as docs/boards/core/01.00.00/specs/spec001/tasks.md; avoid backslashes, Windows paths, and absolute machine-local paths unless documenting an unavoidable external literal
- prefer plain, direct language; explain non-obvious jargon briefly; preserve factual nuance
- avoid decorative emoji and noisy emphasis
- preserve canonical headings, front matter keys, field labels, and checklist/task ordering when the file already follows the expected template or mode
- when toggling a checkbox or updating a task line, edit the existing list item in place; keep its relative position and keep any attached metadata immediately below it
- do not sort task or checklist items by completion state
- tasks.md: keep tasks self-contained and reviewable
- validation.md: record evidence and residual gaps for fast human judgment
- technical-design.md: document architecture decisions and contracts, not implementation code or command runbooks
- notes.md: separate assumptions from findings and decisions
- prd.md: keep goals, constraints, and acceptance criteria readable without turning the file into a task list
