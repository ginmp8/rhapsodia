# Review Workflow

## 1. Establish the target

Record:

- root skill path or archive;
- intended capability and owner role;
- requested mode and output language;
- files supplied, omitted, and protected;
- known failures, prior reviews, expected behavior, supported versions, and migration commitments.

Do not begin semantic scoring until the root is unambiguous. For ecosystem review, map each skill root separately before evaluating shared contracts.

## 2. Build the package map

| Surface | Questions |
|---|---|
| `SKILL.md` | Can the skill activate, route, execute, stop, and produce its declared current output? |
| `agents/openai.yaml` | Does user-facing metadata match the actual capability? |
| `references/` | Are rules reachable, current, non-contradictory, and branch-loaded only when needed? |
| `scripts/` | Are deterministic helpers integrated, runnable, current, and runtime-independent from peer skills? |
| `assets/` | Are assets used in outputs rather than hidden reasoning or historical residue? |
| `examples/` | Do examples represent current behavior and calibrate difficult decisions? |
| `evals/` | Do scenarios cover activation, rejection, ambiguity, edges, current behavior, and explicit migration isolation? |
| validators/package tools | Do they validate the properties used in current, compatibility, and readiness claims? |
| changelog/migrations | Are they factual history or incorrectly acting as current operational authority? |

## 3. Reconstruct the canonical current contract

Write a compact model:

- **Role and owner:** operational responsibility and authority boundary.
- **Activation:** prompts and artifacts that should trigger current behavior.
- **Boundaries:** adjacent requests to reject or hand off.
- **Inputs and versions:** canonical identifiers, schemas, paths, states, and accepted versions.
- **Modes:** current variants and any explicit migration/adaptation mode.
- **Workflow:** ordered current-state transitions from intake to closure.
- **Outputs:** required current sections, formats, evidence, and verdicts.
- **Validation:** current positive tests, invalid-input rejection, migration isolation, and package gates.
- **Stop conditions:** situations where proceeding would invent facts or accept unsupported compatibility.
- **Ownership:** writers, readers, consumers, and allowed cross-skill handoffs.

Name the canonical source for each important concept. Prefer the target's explicit precedence; otherwise use current machine-readable schemas or executed validators, then `SKILL.md`, directly loaded canonical references, validated fixtures, and finally changelog only as historical evidence.

## 4. Define invariants

At minimum, evaluate:

1. Common valid requests activate the current path without hidden context.
2. Adjacent requests and unsupported legacy inputs do not activate current execution incorrectly.
3. Every mode has a reachable entry, executable path, output, and closure rule.
4. Required resources exist and are loadable when needed.
5. Each concept has one compatible current meaning and one canonical owner.
6. Validators do not claim properties they do not inspect.
7. Planned scenarios are not reported as executed results.
8. Packaging excludes generated or obsolete operational residue.
9. The output contract can be satisfied from required inputs.
10. The correction input is self-contained.
11. Normal execution accepts only current contracts and identifiers.
12. Historical adaptation occurs only in an explicit, isolated migration mode.
13. Unknown or malformed current input does not silently fall back to legacy behavior.
14. Current and historical rules do not compete as sources of truth.
15. Peer skills exchange versioned contracts rather than importing or reading each other's internals at runtime.
16. Removal is blocked when owner, consumer, compatibility, or migration evidence is decision-critical and missing.

## 5. Run structural and semantic passes

### Structural pass

Use deterministic inspection for parseability, links, placeholders, syntax, inventory, eval categories, metadata, package noise, and discovery-only legacy signals. Candidate orphan files, keyword matches, old-looking filenames, and missing optional folders are leads, not automatic defects.

### Semantic pass

Trace behavior and challenge optimistic assumptions:

- wrong mode selected for a common prompt;
- evidence required but never requested or produced;
- later steps contradict earlier scope or authority;
- a resource is named but never loaded;
- a validator checks structure while the report claims behavior;
- an output template omits a mandatory field;
- a stop condition makes a core mode impossible;
- examples or tests preserve replaced behavior;
- current validation failure silently retries an old schema, alias, path, state, or version;
- migration, dual lookup, or dual writes occur during normal reads;
- old and current contracts both claim authority;
- one skill imports, executes, or directly reads a peer skill's internal files at runtime;
- changelog or historical prose is the only source of a current rule;
- cleanup removes required current contracts, or compatibility preservation keeps obsolete contracts without evidence.

## 6. Audit legacy, compatibility, ownership, and structural noise

Load `legacy-and-compatibility-audit.md` whenever historical behavior, compatibility, migrations, aliases, fallbacks, old versions, ownership drift, peer coupling, duplicated contracts, or context noise may be relevant.

For every material candidate:

1. locate it and identify writers, readers, imports, links, tests, validators, packaging, and handoffs;
2. identify the current canonical replacement and owner;
3. determine normal-path reachability and migration-mode isolation;
4. classify exactly once as `current`, `migration-only`, `obsolete`, `duplicate`, `contradictory`, `noise`, or `blocked`;
5. decide preserve, isolate, consolidate, remove, reject, or gather evidence;
6. define positive current validation and negative legacy rejection or migration-isolation validation.

In `legacy-audit` mode, always produce the legacy classification, ownership, compatibility, and runtime-coupling matrices, even when they contain no rows. In ordinary full review, include only relevant rows and classification counts. Do not claim that no legacy exists merely because searches returned no matches.

## 7. Test defect hypotheses

For each high-value hypothesis record:

- trigger or condition;
- expected current behavior;
- suspected failure or residue effect;
- evidence needed and observed;
- decision: confirmed, rejected, needs verification, or out of scope.

Do not combine unrelated hypotheses or convert a discovery signal directly into a finding.

## 8. Score after findings

For each rubric dimension:

- cite the strongest evidence;
- state deductions and their reason;
- avoid double-counting one root defect;
- apply gate overrides after the weighted total;
- label the score static unless an evaluator was executed;
- do not reward deletion or lower token count unless current behavior and authority are preserved.

## 9. Build the correction input

Include confirmed findings and explicitly selected likely findings only. Preserve current behavior, isolate valid migration-only behavior, consolidate duplicates, remove proven obsolete/noise items, repair contradictions, and keep blocked decisions outside mandatory fixes until evidence exists.

## 10. Closure criteria

A review is complete for the stated scope when:

- every supplied file was inspected or excluded;
- every blocker/major hypothesis is confirmed, rejected, or named as a decision-relevant gap;
- canonical current sources and owners are named;
- material historical candidates are classified or blocked;
- structural and semantic evidence are separated;
- findings satisfy the finding quality bar;
- current behavior, legacy rejection, migration isolation, ownership, and runtime independence are validated or explicitly blocked;
- the scorecard and verdict follow the evidence;
- the correction input is self-contained and report validation was run or its gap is stated.
