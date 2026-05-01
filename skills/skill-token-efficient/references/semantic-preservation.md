# Semantic Preservation

## Semantic Map

Before editing, extract: purpose/owner; triggers/exclusions; mutation rights by mode; allowed/blocked/protected paths; tool, connector, command, filesystem, and environment rules; evidence/citation requirements; safety/legal/compliance/privacy/security constraints; workflow order; validation/package gates; output sections; stop conditions; resource loading rules.

## Equivalence Test

Each invariant must be preserved verbatim, replaced by a shorter equivalent, moved to a referenced file with a loading rule, or intentionally changed with user/source authority and report note.

## Safe Deletion Test

Delete only when all are true:

1. Text is duplicate, scaffold, generic filler, stale, or weaker than another rule.
2. It does not define scope, safety, tool use, evidence, output, validation, package, or stop behavior.
3. No workflow, reference, template, script, example, or eval depends on it.
4. The readability floor from `compression-playbook.md` still passes.

## Risk Labels

- `low`: wording shortened; no rule moved/removed.
- `medium`: duplicate rules merged or moved; references checked.
- `high`: activation, examples, modes, validation, stop, or output contract changed.
- `blocking`: safety, authority, evidence, or packaging may be weakened.

High/blocking risk requires targeted validation or rollback. Prefer a slightly longer sentence over an ambiguous fragment when behavior may change.
