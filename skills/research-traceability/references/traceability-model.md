# Traceability Model

## Purpose

Represent research-to-skill transformation as explicit evidence-bearing relations rather than prose memory.

## Entity model

### Source `S-*`

Represent one evidence source or immutable evidence bundle. A source is provenance, not a conclusion.

Required concepts:
- locator/title;
- source authority;
- evidence state (`snapshotted`, `pinned`, `live`, or `user-provided`);
- stable identity when available.

### Finding `F-*`

Represent one atomic research claim that can be independently accepted, rejected, scoped, or tested for relevance.

A good finding:
- states one claim;
- cites one or more sources;
- preserves qualifiers, version, jurisdiction, and uncertainty that affect meaning;
- does not contain an implementation choice unless the evidence itself establishes it.

Consolidate semantic duplicates into one finding with multiple `source_ids`. Preserve disagreement as conflict rather than averaging incompatible claims.

### Requirement `R-*`

Translate one or more accepted findings into target-skill behavior. Requirements must be operational and testable enough to drive implementation and evaluation.

Use priorities:
- `must`: required for accepted semantics or hard safety/correctness;
- `should`: materially improves target behavior but permits explicit trade-off;
- `may`: optional enhancement that still requires justification if implemented.

### Change `C-*`

Represent one substantive implementation relation:
- `existing`: target already satisfies the requirement;
- `add`: new behavior/resource;
- `modify`: change existing behavior/resource;
- `remove`: remove behavior that conflicts with accepted requirements.

A change without `satisfies` is unjustified. Treat it as probable gold plating until traced or removed.

### Evaluation `E-*`

Represent verification of one or more requirements. Use:
- `deterministic`: script/schema/static assertion;
- `scenario`: behavior/activation case;
- `review`: semantic or editorial judgment;
- `runtime`: real host/tool execution;
- `perceptual`: subjective visual output when relevant.

Do not make a generator its only judge for objective properties.

### Conflict `K-*`

Represent material disagreement among findings or sources. Preserve the competing finding IDs, resolution status, and rationale. `unresolved` conflicts block finalization when they can change required behavior.

## Finding dispositions

Assign exactly one disposition:

- `implement`: research implies a missing or inadequate target behavior;
- `already-covered`: target already satisfies the derived requirement;
- `rejected`: evidence is too weak, contradicted, out-of-date, or methodologically unsuitable;
- `not-applicable`: valid finding does not belong to this target's scope;
- `uncertain`: evidence does not support a safe decision yet;
- `conflict`: credible evidence disagrees materially.

Require rationale for every disposition. Do not hide excluded knowledge by omitting the finding.

## Bidirectional relations

Require symmetric links:

`Source -> Finding -> Requirement -> Change`

`Requirement -> Evaluation`

and reverse:

`Change -> Requirement -> Finding -> Source`

`Evaluation -> Requirement`

The JSON workspace stores both sides for fast auditing. The validator rejects disagreement between forward and reverse link sets.

## Two independent quality dimensions

### Trace coverage
Mechanically check whether required links exist and resolve.

### Trace validity
Semantically review whether the links are true:
- source actually supports finding;
- finding justifies requirement;
- change actually satisfies requirement;
- evaluation actually tests requirement.

Never infer trace validity from 100% trace coverage.
