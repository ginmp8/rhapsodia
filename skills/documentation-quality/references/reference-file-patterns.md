# Reference file patterns for Skill documentation

Use this guide when reviewing or creating files in the `references/` directory in Skill packages. The goal is to improve future execution while preserving context economy.

## Purpose of `references/`

A reference file should contain conditional detail that is useful only for a branch of work. It should not duplicate the always-loaded control plane in `SKILL.md`.

Good reference files usually contain:

- rubrics and quality criteria;
- checklists for specialized review modes;
- schemas, contracts, or report section requirements;
- command runbooks for scripts and validators;
- target-domain constraints too detailed for `SKILL.md`;
- worked examples that calibrate output quality.

## Recommended reference shape

Use this shape when creating a new reference file:

```markdown
# Clear reference title

Short purpose statement naming when to load this file.

## Decision or review criteria

The non-obvious rules that change execution.

## Procedure or checklist

Steps or checks specific to this branch.

## Examples

Compact examples that reflect real target behavior.

## Validation or stop conditions

How to verify the output and when to report a gap.
```

## README or guide pattern

Use this shape for a repository README or main guide:

1. What this project or package is.
2. Who it is for.
3. Quick start or most common path.
4. Core concepts needed to avoid misuse.
5. Common workflows.
6. Script, command, or API reference when relevant.
7. Examples.
8. Troubleshooting.
9. Validation, maintenance, or contribution notes.

Keep the quick start shorter than the reference sections. Move long details into linked docs.

## Script or validator documentation pattern

Use this shape when documenting scripts or validators:

```markdown
## `path/to/script`

Purpose: what it does and when to run it.

Inputs:
- required path, file, flag, or environment input;
- optional flags and defaults.

Command:

```bash
python path/to/script.py --target path/to/target --output report.json
```

Outputs:
- files written;
- stdout or stderr expectations;
- exit behavior.

Limitations:
- cases not checked;
- manual review still required.
```

Only use a command example after verifying the script exists and the interface is inspectable. Otherwise, document the gap.

## Documentation restructure pattern

When documentation is duplicated or hard to navigate:

1. Inventory docs by purpose, audience, and source of truth.
2. Identify duplicate sections and choose one canonical home.
3. Keep `SKILL.md` limited to activation, routing, workflow, boundaries, and output contract.
4. Move branch-specific details into `references/`.
5. Move reusable report skeletons into `assets/templates/`.
6. Move before/after or calibration material into `examples/`.
7. Remove or rewrite stale claims only after checking source truth.
8. Add cross-links only where they improve execution.

## Context economy rules

- Prefer one concise reference over many overlapping files.
- Avoid nested reference trees unless the package already uses that convention.
- Avoid copying large source files into documentation.
- Do not document obvious Markdown mechanics inside a domain Skill unless they affect output quality.
- Keep examples short enough to calibrate style without becoming a second manual.
- Record gaps instead of adding speculative documentation.

## Anti-patterns

- Turning every checklist into always-loaded `SKILL.md` content.
- Adding a reference file that is not linked from `SKILL.md` or another declared workflow.
- Mixing template variables into a human guide instead of storing a real template under `assets/templates/`.
- Claiming validation passed because a validator exists.
- Hiding missing examples behind broad wording such as "includes many examples".
- Rewriting terminology and breaking the target package's established contract.
