# Semantic Preservation

## Semantic Map

Before editing, extract: purpose/owner; triggers/exclusions; mutation rights by mode; allowed/blocked/protected paths; tool, connector, command, filesystem, and environment rules; evidence duties; citation/reference/source/path/line traceability duties; safety/legal/compliance/privacy/security constraints; workflow order; validation/package gates; output sections; stop conditions; resource loading.

## Equivalence Test

Each invariant must be preserved verbatim, replaced by a shorter equivalent, moved to a referenced file with a loading rule, or intentionally changed with user/source authority and report note.

Do not treat traceability as implied. If source text says `evidence/citation`, `citation`, `source`, `path`, `line`, or `reference`, final text must still require verifiable references unless the user explicitly removes that duty.

## Safe Deletion Test

Delete only when all are true:
1. Text is duplicate, scaffold, generic filler, stale, or weaker than another rule.
2. It does not define scope, safety, tool use, evidence, citation/reference traceability, output, validation, package, or stop behavior.
3. No workflow, reference, template, script, example, or eval depends on it.
4. The readability floor from `references/compression-playbook.md` still passes.

## Traceability Guardrail

Evidence and citations are related, not interchangeable:
- `evidence`: command output, inspected content, logs, benchmark results, reports, or observations supporting a claim.
- `citation/reference`: where that evidence can be verified: source link, file path, line range, command/report path, artifact ID, or source pointer.

Compression may shorten wording but must preserve verification. Prefer `evidence/citation` or `evidence and references` over generic `evidence` when the original required both.

## Risk Labels

- `low`: wording shortened; no rule moved/removed.
- `medium`: duplicate rules merged or moved; references checked.
- `high`: activation, examples, modes, validation, stop, output contract, or citation/reference wording changed.
- `blocking`: safety, authority, evidence, citation/reference traceability, or packaging may be weakened.

High/blocking risk requires targeted validation or rollback. Prefer a slightly longer sentence over an ambiguous fragment when behavior may change.
