# Acceptance criteria

Use this reference for planning and final validation.

## Minimum acceptance gates

A testing or validation task is complete only when the applicable gates have evidence:

- baseline command or static inspection was recorded before fixes;
- changed scripts compile or parse successfully;
- added tests or validators are run, or a clear not-run limitation is reported;
- build/test/lint gates are run when available and relevant;
- failure category and root-cause hypothesis are stated for each unresolved failure;
- blocked paths were not modified;
- final report distinguishes passed, failed, blocked, and not-run gates.

## Skill-package specific gates

For reusable skill packages, include these checks when relevant:

- exactly one root `SKILL.md` in the package root;
- frontmatter has a lowercase `name` and a useful lowercase `description`;
- no unresolved scaffold markers in non-template files;
- referenced local files exist;
- examples include activation, non-activation, ambiguous, and failure prompts when behavior matters;
- executable scripts have `--help` or clear CLI behavior when practical;
- Python scripts compile with `py_compile`; shell scripts parse with `bash -n` when available;
- templates are integrated by workflow instructions or scripts;
- package excludes caches, generated logs, old zips, secrets, `.git`, and temporary reports.

## Evidence labels

Use these labels consistently:

- `passed`: command or supplied evidence proves success;
- `failed`: command ran and returned a relevant failure;
- `blocked`: command could not run because of environment, missing dependency, authorization, or unavailable input;
- `not-run`: skipped by scope or no safe command exists;
- `planned`: proposed scenario or command not executed yet.

## Validation report quality

A useful report is reproducible. It names the target path, command, working directory, exit code, and relevant output excerpt. It also states what was not tested.
