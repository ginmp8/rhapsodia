# Public Artifact Adapters

Load only for external Spec Kit, Kiro, or OpenSpec inputs. Normalize them read-only; never rewrite source artifacts to fit MAGIA.

```bash
python scripts/normalize_public_artifacts.py --source <artifact-root> --format auto --output <normalized.json>
```

Output includes format/root, SHA-256 fingerprints, requirements, criteria, tasks/state, design references, supported delta operations, `missing_fields`, and `lossy_mappings`.

Supported inputs:

- Spec Kit: `spec.md`, `plan.md`, `tasks.md` (optional constitution/checklists); preserve references/checkboxes and report unprovable links.
- Kiro feature/bug: `requirements.md` or `bugfix.md`, `design.md`, `tasks.md`; preserve EARS and current/expected/unchanged constraints.
- OpenSpec: `proposal.md`, optional `design.md`, `tasks.md`, `specs/**/*.md`; preserve ADDED/MODIFIED/REMOVED/RENAMED operations.

Rules:

- Read Markdown only; write output outside the source root.
- Reject source symlinks and resolved paths outside the selected root.
- Use hashes for resume drift; never invent missing fields or relationships.
- Normalization is not approval: inspect repository truth, select risk/profile, validate, converge, and preserve authority.
- Report material loss as `planning_change_required`; create a Mago technical-gap handoff instead of editing external intent.
