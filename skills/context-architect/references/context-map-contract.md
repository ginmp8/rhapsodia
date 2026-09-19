# Context Map Contract

Contract version: **2.0**

Use this file for plans, impact analyses, PR plans, refactor plans, reviews, or multi-file implementation work.

## Required properties

A context map must be:

- **Evidence-backed**: distinguish `measured`, `observed`, `supplied`, `inferred`, `planned`, and `blocked` evidence when material.
- **State-identified**: record repository/revision or supplied-file boundary and freshness status when available.
- **Path-specific**: list concrete paths only when supported by evidence.
- **Ownership-aware**: identify the owning source, contract, schema, or generator before derived outputs.
- **Consumer-aware**: include direct callers/usages plus runtime/config/dynamic consumers relevant to the selected tier.
- **Bounded**: state evidence tier and closure status instead of searching indefinitely.
- **Actionable**: include dependency-ordered change sequence and validation commands.
- **Risk-aware**: connect material risks to evidence and mitigations.

## Canonical ordering

Use this section order for full maps:

1. Evidence identity
2. Scope classification
3. Primary files / owners
4. Secondary files and dependencies
5. Test coverage and validation
6. Patterns to follow
7. Conflicts / unresolved consumers, when present
8. Ripple effects and risks
9. Coverage and closure
10. Suggested sequence
11. Open questions or blockers

Ordering inside tables:

- primary files: direct ownership/edit relevance first, then normalized path;
- secondary files: contract/schema/generator -> direct consumer -> runtime/config -> test -> operational/docs, then normalized path;
- risks: blocking/high -> medium -> low, then subject/path;
- suggested sequence: dependency order, never alphabetical order when dependencies differ.

## Full template

```markdown
## Context Map for: [task]

### Evidence identity
- Contract: context-map/2.0
- Repository: [root or supplied-file boundary]
- Revision/worktree: [commit/branch/dirty state/unknown]
- Evidence freshness: [measured | observed | supplied | blocked]

### Scope classification
- Change type: [bugfix | feature | refactor | migration | config | test | investigation]
- Evidence tier: [focused | standard | extended]
- Scope confidence: [high | medium | low] - [reason]
- Repository evidence inspected: [paths/searches/commands]

### Primary files / owners
| File | Evidence | Why primary | Expected action |
|---|---|---|---|
| `path/to/file` | observed | owns the changed behavior | edit |

### Secondary files and dependencies
| File | Relation | Evidence | Action |
|---|---|---|---|
| `path/to/file` | direct consumer | observed | inspect/update |

### Test coverage and validation
| Test or command | Evidence | Purpose | Confidence |
|---|---|---|---|
| `command` | planned | validates changed behavior | medium |

### Patterns to follow
- `path/to/similar` - [specific convention and evidence]

### Conflicts / unresolved consumers
- [only when evidence conflicts or dynamic/external consumers remain unresolved]

### Ripple effects and risks
| Severity | Risk | Evidence | Mitigation |
|---|---|---|---|
| high | [risk] | observed/inferred | [action] |

### Coverage and closure
- Closure: [closed | provisional | blocked]
- Owners/definitions: [covered/unresolved]
- Direct consumers: [covered/unresolved]
- Runtime/config: [covered/unresolved/not-applicable]
- Tests/validation: [covered/unresolved]
- External/dynamic consumers: [covered/unresolved/not-applicable]

### Suggested sequence
1. [first dependency-safe change]
2. [next change]
3. [validation]

### Open questions or blockers
- [only questions that change file selection, safety, or acceptance]
```

## Compact template

Use only when scope is small and evidence already establishes ownership and direct consumers.

```markdown
## Context Map for: [task]
- Identity: [repo/revision/freshness]
- Tier / closure: [focused|standard] / [closed|provisional]
- Primary: `...`
- Secondary: `...`
- Tests/validation: `...`
- Main risk: [risk + evidence + mitigation]
- Sequence: [1] ... [2] ... [3] ...
```

## Confidence rules

- **High**: owning source, direct consumers, runtime/config as applicable, relevant tests, and selected-tier closure were all established with observed/measured evidence.
- **Medium**: owning source and direct consumers are established, but one noncritical runtime/test/external branch remains inferred or unresolved.
- **Low**: primary paths are inferred from names/snippets/partial files, authoritative evidence conflicts, or material consumers/validation are blocked.

Confidence cannot be upgraded by writing more prose. It follows evidence coverage.

## Question discipline

Ask at most three questions. Ask only when the answer changes file selection, safety, compatibility, or acceptance criteria. Prefer repository evidence over preference questions that existing code can answer.
