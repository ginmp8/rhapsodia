# Portability

## Purpose
Keep one semantic skill usable across ChatGPT/OpenAI, Codex, Claude, GitHub Copilot, Cursor, and compatible Agent Skills hosts without requiring Whiteboard or another persistent runtime.

## Capability model
Detect capabilities instead of assuming product-specific tool names:
- repository/file read;
- diff/history/blame/PR access;
- process execution with Python 3 when deterministic helpers are desired;
- Mermaid or diagram rendering;
- HTML/artifact creation;
- linkable source locators.

## Degradation
- No repository/history access -> work only from supplied files/diff and mark provenance gaps.
- No process execution -> apply the same visual-selection/evidence rules manually and mark validator gates `not-run`.
- No Mermaid renderer -> emit valid Mermaid source if useful; otherwise structured text.
- No rich artifact support -> return the portable Markdown result; do not simulate an interactive canvas.
- No line-addressable source links -> cite file/symbol/commit identities without inventing line numbers.

## Host adapters
Host metadata may improve discovery/UI but must not change semantics. `agents/openai.yaml` is optional adapter metadata; the canonical behavior remains in `SKILL.md` and direct references.
