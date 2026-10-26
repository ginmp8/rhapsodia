# Isolation, rollback and recovery

## Before edits

- Inspect version control status, branch, untracked files, local modifications, submodules and project-specific working conventions. Do not assume a clean tree.
- Prefer a dedicated Git worktree under an authorized location. If unavailable, use an equivalent clean isolated branch or recoverable directory snapshot that protects all existing work. If isolation cannot be established safely, stop before mutation.
- Record baseline revision or content identity, changed-file scope and whether the user explicitly permits new commits. A worktree is isolation, not a sandbox or permission boundary.
- Never run `git clean`, `git reset --hard`, force checkout, force push, unreviewed merge or delete an existing branch/worktree to prepare or recover an experiment.

## During the loop

- Keep one writer per worktree. Preserve original or last-known-good implementation before each candidate. Recheck live status before restoring or applying changes, particularly after parallel workers run.
- If a candidate fails, preserve diagnostics and revert **only the changes attributable to that attempt**. Do not blindly roll back other commits or edits. Use a scoped patch, temporary isolated worktree recreation or a known-safe VCS operation whose effects have been inspected.
- A commit, merge, database change, release or external side effect cannot be guaranteed reversible by the skill. Escalate before irreversible actions and document recovery needs.
- Stop rather than restore when provenance of overlapping modifications is uncertain.

## Closure

- Report which candidate was kept, restored or left isolated; the changed files and remaining uncommitted changes; validation state; residual risks; any cleanup deferred to the owner.
- Do not delete useful diagnostics before recording their evidence identity. Never publish logs containing secrets or personally sensitive values.
- Separate successful local candidate verification from user approval, merge, deployment, and production monitoring.
