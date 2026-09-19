# Output contracts

Use these formats to keep answers useful, auditable, and compact. Adapt section names when the user requests a specific artifact.

## Default response

```md
## Assumptions
- ...

## Recommendation or findings
- ...

## Minimal changes
- file/path: change and reason

## Validation
Executed:
- command/result or "not executed"

Recommended:
- command or browser check

## Risks and next step
- risk/dependency
- next highest-value step
```

## Framework selection

```md
## Assumptions
- project type:
- public/SEO need:
- server-side need:
- team constraints:

## Decision matrix
| option | fit | trade-offs | context cost |
|---|---|---|---|

## Recommendation
[one clear choice]

## When this changes
- condition -> different choice

## Starting structure
```txt
...
```

## Validation
- setup checks
- testing strategy
- migration risks
```

## Architecture plan

```md
## Assumptions
- ...

## Target structure
```txt
src/
  ...
```

## Dependency rules
| from | may import | must not import |
|---|---|---|

## Feature ownership
- feature: owner, responsibilities, contracts

## Minimal migration sequence
1. ...
2. ...

## Validation
Executed:
- ...
Recommended:
- ...

## Risks
- ...
```

## Implementation guidance

```md
## Assumptions
- ...

## Files to inspect first
- path: why

## Minimal implementation plan
1. ...
2. ...
3. ...

## Contracts and data boundaries
- confirmed:
- assumed:
- missing:

## Validation
- typecheck:
- unit/component tests:
- browser checks:

## Risks and rollback
- ...
```

## Code review

```md
## Summary
[overall status and highest-risk theme]

## Findings
### Critical
- [file/area] finding -> smallest fix

### High
- ...

### Medium
- ...

### Low
- ...

## Positive signals
- ...

## Minimal fix sequence
1. ...
2. ...

## Validation
Executed:
- ...
Recommended:
- ...

## Unverified risks
- ...
```

Severity guide:

- Critical: security leak, broken auth assumption, data loss, build-blocking failure, or inaccessible critical flow.
- High: architecture or coupling issue likely to spread, unsafe token/storage/logging pattern, severe UX/accessibility issue in a key flow.
- Medium: maintainability, context cost, test gap, or inconsistency that should be addressed soon.
- Low: cleanup, naming, doc, or minor consistency issue.

## UX flow review

```md
## Flow objective
- user:
- task:
- success event:

## Findings by impact
| impact | finding | smallest adjustment | metric/hypothesis |
|---|---|---|---|

## Recommended minimal change
- ...

## Validation needed
- user test / analytics / Playwright / screenshot / manual review

## Risks
- compliance, accessibility, data sensitivity, backend dependency
```

## Runtime validation plan

```md
## Scope
- flow:
- browsers/viewports:
- states:

## Checks
1. navigation and routing
2. loading, empty, error, success, permission states
3. form validation and focus
4. modal/keyboard behavior
5. responsive screenshots
6. console and network errors
7. accessibility smoke checks

## Playwright sketch
```ts
// focused example, not a full suite unless requested
```

## Evidence to capture
- command
- screenshots/videos/traces
- logs
- failures and gaps
```

## Security review

```md
## Scope
- files/areas reviewed:
- data sensitivity:

## Findings
| severity | area | issue | smallest safe fix |
|---|---|---|---|

## Required controls
- secrets/bundle:
- storage:
- logs/analytics:
- URLs/cache:
- XSS/CSP/source maps:
- authorization boundary:

## Validation
Executed:
- ...
Recommended:
- ...

## Stop conditions or blockers
- ...
```

## AI-context docs output

When creating docs, either provide a file list plus content or a concise patch plan.

```md
## Files to create or update
- AI_CONTEXT.md: purpose
- ARCHITECTURE.md: purpose

## Content
### `AI_CONTEXT.md`
```md
...
```

## Validation
- links to existing commands
- consistency with repo structure
- risks if assumptions are wrong
```

## Stable finding schema

For code, architecture, security, and UX findings, keep this conceptual schema even when rendering prose:

```text
severity
code/category
subject/location
evidence_label
evidence
impact
smallest_fix
validation
```

Order findings by severity, then dependency/root-cause order, then stable path/name order for ties. Merge duplicate symptoms that share one root cause.

## Evidence language

Use precise evidence labels:

- **Measured**: a command, test, scanner, browser check, or deterministic calculation was executed in the current run.
- **Observed**: based on files, diff, screenshots, logs, or repository content that was directly inspected.
- **Supplied**: the user/tool provided a result that was not independently rerun.
- **Inferred**: reasoned from partial evidence or established patterns.
- **Assumed**: unverified premise needed to proceed.
- **Planned**: validation or change proposed but not executed.
- **Blocked**: required evidence or action could not be obtained.

When the user's requested wording uses `Executed`/`Recommended`, keep those headings but map the underlying evidence to `Measured`/`Planned`. Never claim validation, benchmark, readiness, security assurance, repository-wide correctness, or browser behavior without corresponding evidence.

## Evidence layers

Keep these independent:

1. structural/static;
2. build/test;
3. runtime/browser;
4. perceptual/editorial.

A pass in one layer does not imply a pass in the next.
