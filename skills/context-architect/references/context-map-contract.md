# Context Map Contract

Contract version: **2.1**

Use this file for plans, impact analyses, PR plans, refactor plans, reviews, or multi-file implementation work.

## Required properties

A context map must be:

- **Evidence-backed**: distinguish provenance labels and the evidence source class when it affects confidence.
- **State-identified**: record repository/revision or supplied-file boundary, change-set identity when relevant, and freshness status.
- **Path-specific**: list concrete paths only when supported by evidence.
- **Ownership-aware**: identify the owning source, contract, schema, or generator before derived outputs.
- **Consumer-aware**: include direct callers/usages plus runtime/config/build/dynamic consumers relevant to the selected tier.
- **Relation-aware**: use typed directional relations and material hop/depth instead of a generic undifferentiated dependency list.
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
11. Parallelization map, when execution topology is material
12. Open questions or blockers

Ordering inside tables:

- primary files: direct ownership/edit relevance first, then normalized path;
- secondary files: contract/schema/generator -> direct consumer -> runtime/build/config -> test -> operational/docs, then normalized path;
- risks: blocking/high -> medium -> low, then subject/path;
- suggested sequence: dependency order, never alphabetical order when dependencies differ.

## Full template

```markdown
## Context Map for: [task]

### Evidence identity
- Contract: context-map/2.1
- Repository: [root or supplied-file boundary]
- Revision/worktree: [commit/branch/dirty state/unknown]
- Change anchor: [base...head | changed paths | supplied anchor | not-applicable]
- Evidence freshness: [measured | observed | supplied | blocked]

### Scope classification
- Change type: [bugfix | feature | refactor | migration | config | test | investigation]
- Evidence tier: [focused | standard | extended]
- Scope confidence: [high | medium | low] - [reason]
- Repository evidence inspected: [paths/searches/commands]

### Primary files / owners
| File | Evidence | Source class | Why primary | Expected action |
|---|---|---|---|---|
| `path/to/file` | observed | semantic index | owns the changed behavior | edit |

### Secondary files and dependencies
| File | Relation type | Direction / hop | Evidence | Source class | Selection role | Action |
|---|---|---|---|---|---|---|
| `path/to/file` | called-by | owner -> consumer / 1 | observed | semantic index | direct consumer | inspect/update |

`Selection role` should explain why the item is present, such as `direct consumer`, `runtime wiring`, `reverse dependent`, `validation`, `boundary`, or `risk evidence`.

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
- Runtime/build/config: [covered/unresolved/not-applicable]
- Tests/validation: [covered/unresolved]
- External/dynamic consumers: [covered/unresolved/not-applicable]
- Traversal: [max material hop/depth and why expansion stopped]
- Context selection quality: [measured metrics | no gold/reference set | not-applicable]

### Suggested sequence
1. [first dependency-safe change]
2. [next change]
3. [validation]

### Parallelization map
- [optional: independent units, ordered edges, shared reads, write conflicts, barriers, isolation, merge owner, evidence gaps]

### Open questions or blockers
- [only questions that change file selection, safety, or acceptance]
```

## Compact template

Use only when scope is small and evidence already establishes ownership and direct consumers.

```markdown
## Context Map for: [task]
- Identity: [repo/revision/change anchor/freshness]
- Tier / closure: [focused|standard] / [closed|provisional]
- Primary: `...`
- Secondary: `...` ([relation], [source class])
- Tests/validation: `...`
- Main risk: [risk + evidence + mitigation]
- Sequence: [1] ... [2] ... [3] ...
```

## Confidence rules

- **High**: owning source, direct consumers, runtime/build/config as applicable, relevant tests, and selected-tier closure were all established with observed/measured evidence from appropriate source classes.
- **Medium**: owning source and direct consumers are established, but one noncritical runtime/test/external branch remains inferred or unresolved.
- **Low**: primary paths are inferred from names/snippets/fuzzy retrieval/partial files, authoritative evidence conflicts, or material consumers/validation are blocked.

Confidence cannot be upgraded by writing more prose. It follows evidence coverage and source quality.

## Context-selection metrics

When a frozen gold/reference context exists, use `references/context-selection-evaluation.md` and report the executed metric evidence separately. Do not fabricate precision/recall/F1 from subjective confidence. A case may legitimately resolve to `no-useful-local-context`.

## Question discipline

Ask at most three questions. Ask only when the answer changes file selection, safety, compatibility, or acceptance criteria. Prefer repository evidence over preference questions that existing code can answer.
