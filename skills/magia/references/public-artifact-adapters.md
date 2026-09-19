# Public Artifact Adapters

MAGIA may consume supported public SDD artifacts as read-only execution inputs. The adapters normalize structure; they do not grant authority to change source requirements, designs, tasks, proposals, or deltas.

Use `scripts/adapt_public_artifacts.py`. The script reads a source directory and writes a separate normalized JSON execution view.

## Supported Inputs

### Spec Kit

Recognize common specification, plan, and task files, including feature folders that contain `spec.md`, `plan.md`, and `tasks.md`. Preserve source paths and content hashes. Treat constitution or project policy files as constraints when present, not implementation evidence.

### Kiro

Recognize requirements, design, and task files in a feature, bug, or quick-plan folder. A generated quick plan does not automatically qualify the implementation for MAGIA `quick`; MAGIA selects its profile from technical risk.

### OpenSpec

Recognize proposal, design, tasks, and spec-delta files within a change directory. Preserve delta file paths and report when proposal intent, task state, or verification expectations cannot be mapped.

## Normalized Execution View

The adapter emits:

- adapter kind and source root;
- source files with path, size, and SHA-256 digest;
- discovered requirements, design, tasks, deltas, and constraints;
- task checkbox counts when detectable;
- missing expected fields;
- lossy mappings and assumptions;
- read-only confirmation.

The normalized view is an execution convenience, not a rewritten source package. Cite original file paths in implementation and convergence evidence.

## Missing and Lossy Mapping

Report missing fields instead of inventing them. Typical lossy mappings include:

- prose acceptance criteria without stable identifiers;
- tasks that do not reference requirements;
- architecture decisions embedded only in narrative design;
- delta semantics that cannot be represented as a flat requirement list;
- approval, workflow, or policy state unavailable from files;
- implementation status inferred only from checkboxes without current repository evidence.

A lossy mapping can be usable for inspection but must not support a governed completion claim until the missing link is resolved or explicitly handed off.

## Read-Only Guarantee

The adapter never writes inside the source directory. Write output to a caller-selected path outside the source tree. Tests compare source hashes before and after adaptation. If the output path resolves inside the source directory, the command fails closed.
