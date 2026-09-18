<!-- legacy-scan: definitions-only -->
# Legacy, Compatibility, and Structural Noise Audit

## Contents

1. Purpose and decision model
2. Canonical-current contract
3. Investigation workflow
4. Migration-only gate
5. Audit surfaces
6. Technical discovery searches
7. Finding and correction rules
8. Ecosystem ownership calibration
9. Required matrices
10. Closure criteria

## 1. Purpose and decision model

Use this reference when the target may retain historical behavior, obsolete compatibility, migration residue, duplicated contracts, old aliases, permissive fallbacks, or documentation that no longer represents executable current behavior.

The goal is not to erase history indiscriminately. The goal is to keep operational skill content aligned with:

- behavior currently supported;
- contracts currently accepted and emitted;
- responsibilities currently owned;
- canonical identifiers, paths, schemas, and states;
- validators and tests that participate in current gates;
- flows that can actually execute.

Classify every candidate before recommending a change:

| Classification | Meaning | Default treatment |
|---|---|---|
| `current` | Required by the current executable contract. | Preserve and identify its canonical source. |
| `migration-only` | Needed only by an explicit, isolated, still-supported migration path. | Keep isolated only when every migration gate passes. |
| `obsolete` | Historical behavior with no valid current consumer or supported migration. | Remove from operational files and tests. |
| `duplicate` | Repeats a rule whose canonical representation already exists. | Consolidate into the canonical source. |
| `contradictory` | Conflicts with the current contract, owner, schema, state, or path. | Remove or repair before readiness. |
| `noise` | Does not alter behavior but increases context, ambiguity, drift, or maintenance cost. | Remove or move outside normal skill loading. |
| `blocked` | Evidence is insufficient to remove, preserve, or isolate safely. | Name the missing evidence and do not guess. |

Do not classify solely from a keyword, filename, age, version number, or file count. Require a behavioral or maintenance consequence and traceable evidence.

## 2. Canonical-current contract

Before classifying legacy candidates, identify the current source of truth for each affected concept:

- package version versus ecosystem-contract version;
- accepted input and emitted output schemas;
- owner and writer for each artifact or decision;
- state vocabulary per domain;
- canonical path and identifier format;
- supported migration entry points;
- validation and package gates;
- current examples, templates, and fixtures.

Use this precedence unless the target declares another explicit order:

1. machine-readable schema or executable validator used by the current gate;
2. current `SKILL.md` control-plane contract;
3. directly loaded canonical reference;
4. validated example or fixture;
5. changelog or historical note only as evidence of what changed, never as current authority.

When sources disagree, record a `contradictory` candidate instead of choosing the most convenient source.

## 3. Investigation workflow

For every candidate:

1. Locate the instruction, file, field, alias, fallback, test, example, or contract.
2. Identify its writer, readers, imports, links, tests, validators, packaging inclusion, and handoffs.
3. Identify the current canonical replacement, if any.
4. Determine whether the normal path can still activate or accept the candidate.
5. Determine whether an explicit migration mode owns it.
6. Classify it using the decision model.
7. Record the smallest correction: preserve, isolate, consolidate, remove, reject, or gather evidence.
8. Define positive and negative validation that distinguishes current behavior from legacy acceptance.

Trace both directions:

- **producer to consumer:** what emits the value and who accepts it;
- **consumer to source:** where the consumer obtains the contract and whether it bypasses a declared handoff.

A current flow must not depend on reading historical documentation, trying old formats after current validation fails, or silently translating unknown inputs.

## 4. Migration-only gate

Keep a historical adapter only when all conditions are evidenced:

1. an explicit migration or adaptation mode exists;
2. the mode is isolated from normal activation and execution;
3. old formats are rejected outside that mode;
4. the migration produces the current canonical format before normal mutation or handoff;
5. the target skill owns the migration responsibility;
6. positive and negative tests prove isolation, failure atomicity, and loss reporting;
7. unsupported fields, states, or versions fail closed rather than defaulting silently;
8. the migration has a current consumer, support commitment, or removal condition.

If any condition is missing, classify as `blocked` until evidence is gathered or as `obsolete` when current support is explicitly withdrawn.

Do not keep implicit compatibility such as "try current, then legacy", dual writes, multi-path search, canonical-or-old field fallbacks, or automatic migration during normal reads.

## 5. Audit surfaces

### 5.1 Version and history integrity

Investigate:

- retroactive renumbering or reinterpretation of published releases;
- normalized-history tables that create fictitious equivalence;
- package versions mixed with ecosystem-contract versions;
- old versions accepted as aliases of current versions;
- changelogs that imply a historical release had another number;
- alignment of past history instead of compatibility of future releases.

Expected contract:

- preserve real published package versions;
- maintain a distinct current ecosystem-contract version when needed;
- use an explicit compatibility matrix of real versions;
- reject unknown or unlisted combinations.

### 5.2 Handoff and envelope contracts

Investigate:

- old handoff builders or validators retained beside current ones;
- version-1 envelopes, generic fields, or missing source, provenance, freshness, direction, or contract version;
- validators that try the current schema and then accept an old schema;
- examples or fixtures that still emit the replaced format;
- direct reads of another skill's artifacts that bypass the handoff contract;
- duplicated handoff scripts with different rules.

Expected contract: the normal path accepts only the current envelope. Historical adaptation occurs before the current handoff is built.

### 5.3 Field aliases and semantic conflation

Investigate generic or deprecated aliases such as:

- `priority`, `order_hint`, `critical_priority`, or unnamed urgency;
- canonical-or-old fallback expressions;
- templates containing both removed and current fields;
- tests whose purpose is to preserve a deleted alias;
- automatic conversion between business priority, technical criticality, and execution order.

Expected contract: each domain uses a namespaced, owner-specific field. Removed generic fields are rejected, not silently ignored.

### 5.4 State aliases and silent translation

Investigate:

- `done`, `complete`, `completed`, `closed`, `success`, or release/governance states treated as universal synonyms;
- spelling aliases accepted without versioning;
- generic state normalizers and unknown-state fallback;
- technical completion automatically closing governance or release decisions;
- projections that do not preserve original state, origin, or mapping version.

Expected contract: each dimension has its own vocabulary. Projections declare origin, preserve the source value, use a versioned mapping, and do not transfer authority.

### 5.5 Paths and identifiers

Investigate:

- old ID formats, random suffixes, ULIDs, UUIDs, hashes, or counters after a canonical format replaced them;
- old directory trees, aliases, multi-location lookup, dual writes, or read-time migration;
- references to replaced locations such as `docs/current` when no longer canonical;
- parsers that accept several formats without an explicit adapter mode.

Expected contract: one canonical identity and path format in normal operation.

### 5.6 Historical ownership drift

Investigate ambiguous verbs and cross-owner writes:

- "update the status", "set priority", "close the work", or "replan as needed" without naming owner, artifact, and authority;
- one skill defining another skill's architecture, requirements, delivery status, governance decision, implementation, or release communication;
- a downstream execution skill changing upstream requirements or acceptance criteria;
- a planning skill declaring execution or production complete without attributed evidence;
- direct writes to artifacts owned by another skill.

Expected contract: every write names the owning role, artifact, allowed transition, evidence, and handoff boundary.

### 5.7 Runtime coupling between skills

Investigate:

- runtime imports from another skill package;
- reading another package's `SKILL.md` or internal references during normal execution;
- executing another skill's scripts by path;
- absolute paths such as `/home/oai/skills/...`;
- dependence on joint installation for local core functions;
- shared mutable files;
- a contract whose only canonical copy lives inside one peer skill;
- one skill validating a peer by importing its implementation.

Expected contract: packages may carry byte-equivalent shared contracts and compare them in integration validation, but each skill remains operationally independent.

### 5.8 Broad or permissive compatibility

Investigate:

- broad version ranges, `>=`, any-version compatibility, best-effort reads, or default-to-current behavior;
- unknown fields ignored or coerced;
- unknown versions accepted because some fields exist;
- mixed versions allowed without an explicit matrix;
- catches that turn mandatory failures into warnings.

Expected contract: compatibility is explicit, bounded, matrix-based, and fail-closed.

### 5.9 Changelog as active documentation

Investigate changelogs that contain:

- current commands, complete contracts, authority rules, normative examples, or operational controls;
- the only copy of a still-valid rule;
- removed instructions retained as historical controls;
- text added only to satisfy a keyword validator;
- untested compatibility claims.

Expected contract: changelogs record concise factual changes. Current rules live in canonical operational files and are validated there.

### 5.10 Historical documentation in normal context

Investigate:

- long "formerly", "previously", "old format", or transition sections;
- commented-out old instructions;
- completed migration notes, obsolete equivalence tables, or renamed files and modes;
- architectural history that does not affect current execution.

Expected contract: move still-relevant historical rationale to an ADR or external record outside normal skill loading. Remove obsolete operational guidance.

### 5.11 Old, duplicated, or unintegrated scripts

Investigate:

- scripts named `old`, `legacy`, `v1`, `deprecated`, `backup`, `copy`, or ambiguous `new`;
- duplicate validators or builders for one contract;
- scripts not referenced by instructions, tests, validators, or packaging;
- wrappers with no additional behavior;
- completed migration code retained operationally;
- documented commands that no longer execute.

Before recommending removal, trace imports, subprocess calls, docs, tests, packaging, and platform conventions.

### 5.12 Tests preserving removed behavior

Investigate:

- tests that expect old aliases, schemas, paths, versions, or permissive fallback;
- old fixtures or golden files still marked valid;
- tests that pass because an invalid input is ignored;
- expected outputs regenerated automatically to accept a change;
- skipped mandatory tests without rationale.

Expected contract: replace obsolete acceptance tests with explicit rejection tests when support is removed.

### 5.13 Obsolete examples and templates

Investigate examples or templates with removed fields, old paths, old versions, incomplete provenance, generic priority, cross-owner writes, or bypassed validators.

Expected contract: every operational example represents the current contract and is validated when practical.

### 5.14 Duplicated and divergent contracts

Investigate:

- Markdown and machine-readable schemas with different enums or required fields;
- the same contract copied across files or skills without equivalence validation;
- producer and consumer disagreement;
- multiple mapping versions presented as current;
- error messages revealing different semantics.

Expected contract: choose a machine-readable canonical representation when appropriate. Documentation explains it without manually recreating divergent copies.

### 5.15 Artificial or fragile validation

Investigate:

- keyword-presence gates;
- checks satisfied by adding a sentence to a changelog;
- schema checks presented as producer/consumer proof;
- tests that do not execute the real path;
- success returned after exceptions;
- broad catches, mandatory conditions downgraded to warnings, or auto-updated hashes/expected outputs.

Expected contract: validate structure or behavior directly. A gate must fail when the protected invariant is violated.

### 5.16 Packaging and generation residue

Investigate nested archives, reports, logs, caches, bytecode, temporary files, benchmark outputs, generated manifests, diffs, backups, debug artifacts, unused snapshots, empty files, and generated local paths.

Expected contract: exclude generated evidence and residue from the final operational package unless a declared runtime asset requires them.

### 5.17 Scaffold and placeholders

Investigate unresolved markers, fillable tokens outside templates, empty headings, generic copied instructions, nonexistent tools, incomplete commands, impossible examples, and vague directions that name no validator.

Expected contract: placeholders exist only in declared templates. Operational instructions are executable and specific.

### 5.18 Context noise

Investigate repeated explanations, excessive principles already enforced by validators, redundant examples, motivational text, architectural history, copied rules from peer skills, non-actionable references, repeated disclaimers, and schema duplication.

Expected contract: retain the smallest canonical content that preserves activation, authority, workflow, evidence, validation, outputs, and stop conditions.

## 6. Technical discovery searches

Use equivalent searches when filesystem access exists. Adapt names and formats to the target domain.

```bash
rg -n -i \
  'legacy|deprecated|obsolete|old format|previously|formerly|historical|pre-normalization|normalized history|compatibility.?mode|allow_legacy|fallback|handoff-v1|schema.?version.?1|order_hint|priority|done|complete|cancelled|canceled|ulid|uuid|docs/current|backup|copy|v1' \
  <TARGETS>

rg -n \
  '/home/oai/skills|read_text.*SKILL.md|subprocess.*skills|import .*<PEER_SKILL>' \
  <TARGETS>

find <TARGETS> -type f \( -name '*.zip' -o -name '*.pyc' -o -name '*.bak' -o -name '*.tmp' -o -name '*.log' \)
find <TARGETS> -type d \( -name '__pycache__' -o -name '.pytest_cache' -o -name '.mypy_cache' -o -name '.ruff_cache' \)
```

Text search is discovery only. For each match, inspect surrounding rules, consumers, tests, and current canonical sources before classifying it.

The deterministic preflight may emit a `legacy_signal_summary`. Treat every entry as a candidate, not a confirmed defect.

## 7. Finding and correction rules

For each confirmed legacy finding:

1. identify the current canonical source;
2. identify writers, consumers, imports, links, tests, and packaging impact;
3. assign one classification;
4. remove or isolate the old behavior;
5. remove the corresponding fallback or alias;
6. update examples, templates, fixtures, and rejection tests;
7. update current documentation and keep changelog facts concise;
8. replace textual gates with structural or behavioral validation;
9. validate positive current behavior and negative legacy rejection;
10. verify ownership and runtime independence.

Do not prescribe deletion when evidence is `blocked`. Ask for the exact missing consumer, compatibility commitment, migration owner, version matrix, or test evidence.

A correction input must prohibit reintroducing historical prose merely to satisfy a textual validator.

## 8. Ecosystem ownership calibration

Use the following only as calibration when the reviewed target is the Mago/Magia/Nomia ecosystem. Do not apply these names to unrelated skills.

| Concern | Canonical owner or behavior |
|---|---|
| business priority, roadmap, owner, stakeholders, governance status | Nomia writes; others consume only as declared |
| technical criticality, execution sequence, architecture, technical plan | Mago writes |
| implementation evidence, code, tests, execution records | Magia writes |
| governance closure or release communication | Nomia, based on attributed evidence |
| requirement or acceptance-criteria changes | upstream governance/planning flow, not silent Magia mutation |
| cross-skill exchange | versioned handoff contract, not direct runtime reads or writes |

Calibrated suspicious cases include:

- generic `priority` used as an alias for both business and technical decisions;
- technical `done` automatically closing Nomia governance;
- Mago changing business owner or roadmap status;
- Magia rewriting PRD or acceptance criteria during implementation;
- Nomia writing technical tasks or validating code;
- any package importing peer scripts or reading peer `SKILL.md` at runtime.

## 9. Required matrices

For a `legacy-audit`, include these matrices even when rows are empty.

### Legacy classification matrix

| Item | Skill/package | Location | Classification | Normal-path reachable | Migration isolated | Recommended action | Evidence |
|---|---|---|---|---:|---:|---|---|

### Ownership matrix

| Artifact or decision | Correct owner | Writers found | Consumers | Authority violation | Result |
|---|---|---|---|---:|---|

### Compatibility matrix

| Contract | Real producer version | Real consumer version | Accepted | Rejected | Evidence |
|---|---|---|---:|---:|---|

### Runtime coupling matrix

| Caller | Dependency | Mechanism | Required at runtime | Canonical alternative | Classification |
|---|---|---|---:|---|---|

## 10. Closure criteria

A legacy audit is complete for the inspected scope only when:

- current canonical sources are named;
- every material candidate is classified or explicitly `blocked`;
- normal flows accept only current contracts and identifiers;
- old fields and states are rejected outside explicit migration modes;
- migrations that remain satisfy every migration-only gate;
- no retroactive version equivalence is presented as fact;
- ownership writes and authority transitions are explicit;
- runtime imports or direct peer-file reads are removed or justified as current architecture;
- examples, templates, tests, and validators represent current behavior;
- obsolete acceptance tests become rejection tests where support ended;
- changelogs are factual rather than normative;
- package residue and context noise are removed or justified;
- executed and blocked validations are separated;
- the correction input preserves current behavior while removing obsolete compatibility.
