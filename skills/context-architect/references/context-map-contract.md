# Context Map Contract

Use this file when the user asks for a plan, impact analysis, PR plan, refactor plan, or multi-file implementation.

## Required properties

A context map must be:

- **Evidence-backed**: name the searches, files, diffs, commands, or snippets inspected.
- **Path-specific**: list concrete paths when available; avoid vague labels such as "service layer" unless paths are unavailable.
- **Dependency-aware**: include callers, registrations, interfaces, generated artifacts, configuration, and tests.
- **Actionable**: include a suggested sequence and validation commands.
- **Risk-aware**: include ripple effects and mitigations.

## Full template

```markdown
## Context Map for: [task]

### Scope classification
- Change type: [bugfix | feature | refactor | migration | config | test | investigation]
- Scope confidence: [high | medium | low] - [reason]
- Repository evidence inspected: [files/searches/commands]

### Primary files
| File | Why it is primary | Expected change |
|---|---|---|
| `path/to/file` | [direct responsibility] | [edit/test/read-only] |

### Secondary files and dependencies
| File | Relationship | Action |
|---|---|---|
| `path/to/file` | [caller/import/registration/config/test/schema] | [inspect/update/test/watch] |

### Test coverage and validation
| Test or command | Purpose | Confidence |
|---|---|---|
| `command` | [what it validates] | [high/medium/low] |

### Patterns to follow
- `path/to/similar` - [convention, shape, naming, error handling, logging, tests]

### Ripple effects and risks
| Risk | Evidence | Mitigation |
|---|---|---|
| [risk] | [source] | [action] |

### Suggested sequence
1. [read or modify first]
2. [next step]
3. [validation step]

### Open questions or blockers
- [blocking question only]
```

## Compact template

Use for small but still multi-file changes.

```markdown
## Context Map for: [task]
- Primary files: `...`
- Secondary files: `...`
- Tests/validation: `...`
- Pattern to follow: `...`
- Main risk: [risk + mitigation]
- Sequence: [1] ... [2] ... [3] ...
```

## Confidence rules

- **High**: primary files, usages, tests, and matching patterns were all inspected.
- **Medium**: primary files and either usages or tests were inspected, but some runtime/config path remains uncertain.
- **Low**: paths are inferred from names, snippets, stack traces, or partial files; mark the map provisional.

## Open question discipline

Ask at most three questions. Only ask when the answer changes file selection, safety, or acceptance criteria. Do not ask style or preference questions that can be inferred from existing code.
