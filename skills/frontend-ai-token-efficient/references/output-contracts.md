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

## Evidence language

Use precise evidence labels:

- **Executed**: a command, test, browser check, or script was run in this conversation.
- **Observed**: based on files, diff, screenshots, logs, or repo content that was inspected.
- **Inferred**: reasoned from common patterns or partial evidence.
- **Assumed**: not verified; state the assumption clearly.
- **Recommended**: a next validation step, not a claim that it passed.

Never claim validation, benchmark, readiness, security assurance, or browser behavior without evidence.
