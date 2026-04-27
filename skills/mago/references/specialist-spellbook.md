# Specialist Spellbook

Use this reference when defining, refining, decomposing, or correcting task specialist selection.

## Canonical Catalog

- current discoverable specialist catalog: .github/agents/README.agents.md
- use repository-relative POSIX specialist references in task metadata
- today the spellbook only discovers specialists from the current agents catalog, so discovered entries resolve to .agent.md paths
- the task metadata schema is still future-compatible with skill entrypoints when a skill catalog exists
- do not load or nominate specialists blindly from title alone; match them to the actual task boundary

## Selection Workflow

1. read the task's `Objective`, `Affected boundary`, `Task type`, `Validation`, and `Expected result`
2. identify the narrow technical domains involved: platform, framework, language, infra, docs, migration, security, or testing
3. search the current discoverable specialist catalog for specialists whose title or description materially narrows that task
4. keep the smallest useful set
5. record the specialist decision in the task metadata

## Task Metadata Contract

Every actionable task must declare:

- `Specialist Support`
- `Required LOAD`
- `Optional LOAD`
- `Selection Hint`

Use this closed enum for `Specialist Support`:

- `not_required`
- `required`
- `optional`

Field rules:

- `Required LOAD` and `Optional LOAD` must use repository-relative POSIX specialist references, comma-separated when there are multiple entries
- use `none` only when a field is intentionally empty by contract

Decision rules:

- `Specialist Support: not_required`
  - use when no specialist materially improves execution quality or safety
  - set `Required LOAD: none`
  - set `Optional LOAD: none`
  - set `Selection Hint: none`
- `Specialist Support: required`
  - use when execution quality or safety materially depends on at least one specialist
  - `Required LOAD` must list at least one specialist path
  - `Optional LOAD` may be `none`
  - `Selection Hint` must explain why those required specialists are sufficient
- `Specialist Support: optional`
  - use when specialist help is useful but not mandatory for an honest execution
  - `Required LOAD` may be `none`
  - `Optional LOAD` must list at least one specialist path
  - `Selection Hint` must explain when to load the optional specialists

## Selection Constraints

- prefer one specialist over many when one is enough
- use multiple specialists only when they cover complementary boundaries
- do not use specialists to compensate for a task that should have been decomposed
- if no matching specialist exists in the catalog, use `not_required`
