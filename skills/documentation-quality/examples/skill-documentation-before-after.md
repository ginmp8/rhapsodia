# Skill documentation before and after examples

Use these examples to calibrate concise, evidence-grounded documentation improvements for Skill packages.

## Example 1: Reference file review

### Before

```markdown
# Validator

Run the validator to check everything. See the script here. It will validate the skill and create a complete report.
```

### Problems

- The script path is missing.
- The link text is not descriptive.
- The scope of "everything" is unsupported.
- The output claim is not tied to an actual file or command.

### After

```markdown
# Package validator

Use this reference when documenting the package validation step.

## Command

Run the validator only after confirming the package builder exists in the target package:

```bash
python target-package/scripts/package_skill.py path/to/skill-folder
```

## What it checks

The package validator checks skill structure and creates `skill.zip` when validation passes. If the script is absent or the interface differs, report that as a documentation gap instead of describing unverified behavior.
```

### Why this is better

- Names the artifact being documented.
- Uses a descriptive local path instead of an ambiguous link.
- Scopes the claim to inspected behavior.
- Gives a clear gap rule when the script does not exist.

## Example 2: README restructuring

### Before

```markdown
# My Skill

This skill helps with docs. It can review, fix, validate, harden, benchmark, and package any skill. Use the examples folder for more info. Click here for details.
```

### Problems

- The capability claim is too broad.
- It mixes documentation review with hardening, benchmarking, and packaging ownership.
- The examples path is not linked or verified.
- The link text is inaccessible.

### After

```markdown
# My Skill

This skill reviews and improves human-oriented documentation in a Skill package.

## Use it for

- reference file review;
- README and usage guide cleanup;
- script and validator documentation;
- example improvement;
- Markdown accessibility checks.

## Boundaries

Use a dedicated hardening or benchmark workflow for activation ownership, package maturity scoring, and full package repair.

## Examples

See `examples/skill-documentation-before-after.md` when you need rewrite patterns for concise Skill documentation.
```

### Why this is better

- Narrows the scope to documentation quality.
- Preserves ownership boundaries.
- Replaces vague link text with a specific path.
- Lists practical triggers without turning the README into a full manual.

## Example 3: Markdown accessibility pass

### Before

```markdown
## Setup

#### Running

For instructions, click here. See this and this for examples.
```

### After

```markdown
## Setup

### Run the documentation review

Read `references/documentation-quality-rubric.md` before evaluating technical accuracy. Use `examples/skill-documentation-before-after.md` when the requested output needs before/after examples.
```

### Why this is better

- Heading levels no longer skip from H2 to H4.
- Link targets are described by file purpose.
- The sentence explains when each resource is useful.
