# Manually Reconcile Concurrent Git Changes

## At a Glance

- **Purpose:** Convert Git merge-tree conflict paths into auditable source-and-destination-preserving resolutions without merge commits.
- **Load when:** The plan reports `status: conflicts`, concurrent edits require special handling, or Git cannot cleanly integrate a binary, rename or mode change.
- **Decision impact:** Requires reviewed content for every conflict, prevents automatic ours/theirs replacement and keeps the destination ref unchanged until apply.

## Workflow

1. Treat `source_sha`, `target_sha` and `base_sha` in the plan as immutable inputs. Examine the three versions of every conflicting path with `git show <SHA>:<path>` and the surrounding entrypoints, configuration, docs, callers and tests. Inspect renamed/deleted paths and executable/symlink modes; a filename alone does not prove a feature.
2. Choose a coherent integrated design; preserve independent source and destination capabilities and their data/security contracts. If both cannot coexist safely, document the incompatible requirements and stop for an explicit decision. Never auto-resolve by taking the entire source, destination, or longest file.
3. Write final resolved contents to ordinary files inside a reviewed, approved resolution root **outside the tracked repository worktree**. Do not store credentials, generated secrets or live personal data. Store the resolution manifest outside the target worktree too.
4. Provide one resolution for **every path reported in `conflict_paths`**, matching that list exactly. For a normal file, specify `file` (relative to `--resolution-root`), its final Git mode (`100644`, `100755` or `120000`), and `reason` with meaningful rationale. To delete a path deliberately, specify `delete: true` and a rationale. Unsupported gitlinks or complex mode/type transitions must be handled through a reviewed native Git workflow, not forged in the manifest.
5. Generate a new plan with the same frozen refs and `--resolutions` + `--resolution-root`; the helper builds a temporary Git index, overlays reviewed blobs and verifies source-only/target-only paths. It does not edit any tracked worktree files. Inspect the candidate tree diff and run relevant checks before apply.

## Resolution manifest example

```json
{
  "schema": "branch-reconciliation-resolutions/v1",
  "paths": {
    "src/feature.ts": {
      "file": "src/feature.ts",
      "mode": "100644",
      "reason": "Combine the upstream handler with destination authorization and retry rules."
    }
  }
}
```

For this example the separate `--resolution-root` directory contains `src/feature.ts` with its integrated final bytes. The helper refuses absolute, parent-traversing and symlink escaping resolution paths. It checks manifest completeness and stores Git blob objects; no parent ref is changed during planning.

## Safeguards

- Git `merge-tree` returning a tree object on conflict does **not** imply a clean candidate; that object may include conflict markers. Never commit it directly. Only the reviewed resolved tree can be used.
- An explicit resolution reason is an audit marker, **not proof** that both behaviors survive. Review changed symbols and callers, use scenario tests for both source and destination, and compare docs and migrations.
- A source-only addition or deletion must remain exactly as source intended; a destination-only addition or deletion must remain exactly as the destination intended. The helper enforces exact tree entries for those classes.
- A conflict path can be omitted from the final tree only by an explicit reviewed deletion. Do not delete a necessary source feature merely to make the merge clean.
- When conflict data contains ambiguous binary/rename cases or non-representable Git object types, return `blocked` and escalate to a trusted native Git workflow with the same frozen SHA and single-parent gates.
