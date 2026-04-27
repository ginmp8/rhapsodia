# Execution Evidence

Use this reference only when Magia needs to emit structured factual execution evidence for downstream consumption.

Magia owns execution evidence: repository changes, changed files, commands/tests run, validation outcomes, blockers, known failures, and deployment evidence only when directly observed or provided. Durable MAGIA evidence must live under `BOARD_ROOT`.

Magia does not create downstream governance or communication artifacts, including roadmap, release, status, stakeholder, portfolio, feature reporting, or release communication documents. Magia exposes evidence only; downstream consumers decide how to interpret and communicate it.

## Evidence Shape

When structured evidence is emitted, use this shape so consumers do not need to scrape prose:

```yaml
execution_evidence:
  spec_id: "spec001"
  feature_key: "example-feature"
  repo: "example-repo"
  branch: "feat/spec001-example"
  prs: []
  commits: []
  files_changed: []
  tests_run: []
  validation_summary: ""
  known_failures: []
  blockers: []
  deployment_evidence: null
  generated_at: "YYYY-MM-DD"
```

Use `null`, an empty string, or an empty list for missing evidence. Do not infer missing values from nearby text, branch names, task titles, or desired outcomes.

## Field Rules

* `spec_id`: active specNNN when known; otherwise `null`.
* `feature_key`: active feature key when known; otherwise `null`.
* `repo`: repository name when known; otherwise `null`.
* `branch`: observed current branch when known; otherwise `null`.
* `prs`: observed PR identifiers or URLs; empty means no PR evidence was observed.
* `commits`: observed commit SHAs or references; empty means no commit evidence was observed.
* `files_changed`: repository-relative changed paths.
* `tests_run`: commands or validation checks actually run, with outcomes when available.
* `validation_summary`: observed validation results and residual gaps only.
* `known_failures`: failing checks, broken behavior, or unresolved validation gaps.
* `blockers`: blockers that prevent truthful completion or release claims.
* `deployment_evidence`: observed deployment or release evidence only; otherwise `null`.
* `generated_at`: evidence generation date in `YYYY-MM-DD`.

## Interpretation Rules

* PR merge is not proof of production release.
* Passing tests are not proof of business acceptance.
* A changed file is not proof that the feature is complete.
* A completed Magia task is not proof that stakeholder communication is ready.
* Missing evidence must remain unknown, not inferred.
* Deployment, release, availability, and business acceptance require explicit evidence.

## Boundaries

When the active execution mode allows it, Magia may update controlled execution-state fields in canonical active spec packages, including truthful task checkboxes, validation evidence, execution logs, and manifest.yaml last_execution.

Magia must not rewrite planning intent, task definitions, roadmap inputs, product scope, acceptance criteria, feature sequencing, or PRD content. If execution reveals that planning content needs to change, record the blocker or follow-up as execution evidence and hand off instead of rewriting planning artifacts.

## Emission Rules

* Prefer existing Magia execution records when they already provide the needed evidence.
* Emit structured evidence only in MAGIA-owned execution evidence locations or existing execution records under `BOARD_ROOT`.
* Do not create or update downstream governance or communication artifacts from Magia.
* Do not add validators for downstream governance or communication artifacts.
* Do not change execution behavior just to satisfy reporting needs.
* Keep evidence factual, concise, and mechanically consumable.
