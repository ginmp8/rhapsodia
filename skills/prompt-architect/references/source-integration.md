# Source Integration

Use when a prompt is derived from external documentation, files, repositories, standards, examples, or multiple sources.

## Source authority

Default precedence:

1. current user requirements for the prompt-design task;
2. binding safety/legal/compliance constraints;
3. authoritative specification or official documentation for the target system/version;
4. repository-local contracts, tests, schemas, and maintained examples;
5. project/internal documentation supplied by the user;
6. reputable secondary sources;
7. community guidance;
8. inferred best practice.

Authority and recency are separate. A newer community post does not automatically override an older binding specification.

## Source identity and provenance

For each material source, record enough identity to distinguish what was actually used:

- title/path/URL;
- version, revision, branch/commit, or date when known;
- relevant section/range;
- whether content was directly inspected or only summarized by another source;
- requirements extracted from it.

When a repository/file revision materially controls acceptance, capture a **source snapshot** or exact source bytes when feasible and prefer a pinned VCS revision over a moving branch or live page. If the source changes mid-review, either continue using the captured version or intentionally re-baseline; do not mix versions silently.

## Extraction

Extract only facts that change prompt execution:

- required inputs/outputs;
- schemas/protocols;
- commands/tool capabilities;
- domain definitions;
- version-specific behavior;
- constraints and prohibited actions;
- failure modes;
- examples that clarify semantics;
- success criteria;
- citation/traceability requirements.

Convert them into concise prompt requirements rather than copying large passages.

## Conflict representation

Classify source conflicts as:

- `resolved-by-authority`;
- `resolved-by-version`;
- `scoped-exception`;
- `unresolved`.

For unresolved material conflicts, expose the alternatives and request authority instead of blending them.

## Repository/codebase prompts

Inspect contracts before style:

`README/docs -> manifests/config -> schemas/interfaces -> tests -> representative implementation -> examples`

Use repeated implementation patterns as evidence only when no stronger contract exists. Do not generalize from one isolated file.

## Evidence and citations in generated prompts

Add citation/source rules only when future executions need them. Do not embed one-time research notes into a reusable prompt unless they are operationally necessary.

If future execution requires sources that may be unavailable, define a fallback: state uncertainty, stop, or return missing-evidence status. Never instruct the executor to fabricate citations or source-backed claims.
