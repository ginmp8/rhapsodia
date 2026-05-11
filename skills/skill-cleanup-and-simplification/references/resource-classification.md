# Resource Classification

Classify each candidate before deletion, consolidation, or retention.

## Status taxonomy

| Status | Meaning | Default action |
|---|---|---|
| `used` | Referenced by `SKILL.md`, local links, scripts, templates, validators, examples, or package metadata. | Preserve. |
| `integrable` | Useful and aligned with the skill, but not currently wired into the workflow. | Integrate before considering deletion. |
| `obsolete` | Replaced, stale, contradicted, or outside current scope with evidence. | Remove or archive only after validation plan. |
| `duplicated` | Same purpose and overlapping content as another resource. | Consolidate, then update links. |
| `generated` | Build output, cache, local report, temporary file, or package residue. | Remove if not protected evidence. |
| `placeholder` | Unadapted scaffold, to-do marker only file, fake example, or template residue. | Remove or replace. |
| `blocked` | Protected by policy, user instruction, or safety uncertainty. | Do not change. |
| `unknown` | Evidence is insufficient. | Retain and recommend review. |

## Evidence checklist

Use at least one strong evidence source before classifying as removable:

- direct local link or import graph;
- script usage or command references;
- package metadata or manifest references;
- comments or documentation naming the resource;
- file hash or content comparison proving duplication;
- validation output showing generated/cache status;
- user instruction naming the file as obsolete;
- replacement file with updated references.

Absence of evidence is not evidence of absence.

## Progressive-loading guard

Skill resources may be intentionally dormant until a branch needs them. Preserve a file when it provides:

- mode-specific instructions too long for `SKILL.md`;
- validation or report templates;
- examples or scenario suites;
- schemas, rubrics, policy references, or command contracts;
- assets copied or filled during a workflow.

If useful but unreferenced, mark `integrable` and add a loading rule or workflow reference.

## Classification output shape

Use this table shape in reports:

| Path | Status | Evidence | Decision | Risk | Validation |
|---|---|---|---|---|---|
| `path/to/file` | `used` | Linked from `SKILL.md` | Preserve | Low | Link check |
