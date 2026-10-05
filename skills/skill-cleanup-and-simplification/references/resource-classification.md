# Resource Classification

## At a Glance

- **Purpose:** Own the seven-state resource taxonomy and the evidence rules for deciding whether a resource is used, integrable, duplicate, obsolete, generated, blocked, or unknown.
- **Load when:** Reviewing dead-resource candidates, duplicate/generated signals, scaffold/template status, or any plan whose mutation eligibility depends on classification.
- **Decision impact:** Fixes fail-closed precedence, defines which evidence can establish `generated`, `duplicate`, or `obsolete`, and prevents weak similarity, naming, or missing-reference signals from becoming deletion authority.
- **Do not load when:** Classification is already frozen and the remaining question is transaction safety/rollback; use `safe-cleanup-rules.md` instead.

## Contents

- Canonical state taxonomy
- Classification precedence
- Reachability evidence
- Generated evidence
- Duplicate tiers
- Scaffold and template guard
- Protected evidence guard
- Classification evidence strength
- Report shape

Classify every candidate before deletion, consolidation, or retention. Classification is evidence, not permission by itself; mutation must also pass the canonical deletion gate.

## Canonical state taxonomy

| State | Meaning | Default action |
|---|---|---|
| `used` | Reachable from the recorded root registry through a local reference edge. | Preserve. |
| `integrable` | Useful support resource that is not currently reachable, but is aligned with the skill and may be intentionally dormant. | Integrate or explicitly retain. |
| `duplicate` | Exact duplicate with mechanically identical content and a known canonical copy. | Consolidate only after consumer tracing and validation. |
| `obsolete` | Replaced or no longer valid, proven by explicit target/user/migration/validator evidence. | Remove only after explicit approval, rollback, and validation. |
| `generated` | Reproducible/cache residue supported by strong generation evidence and not required by the package. | Eligible for cleanup after preflight. |
| `blocked` | Protected by policy, evidence role, contract/test role, archive protection, secret-like identity, symlink/path risk, user instruction, or safety boundary. | Do not mutate. |
| `unknown` | Evidence is insufficient or conflicting. | Retain. Never auto-delete. |

Do not create extra top-level states for scaffold-only content, generated-like namespaces, or duplication tiers. Store those as evidence signals attached to one canonical state.

## Classification precedence

Use this fail-closed precedence when multiple signals apply:

1. `blocked` - protection or unsafe path wins.
2. `used` - reachable/consumed resource wins over cleanup heuristics.
3. `generated` - only with strong evidence, never namespace naming alone.
4. `duplicate` - only exact duplicates that are not required consumers themselves.
5. `integrable` - unreferenced support resource with plausible package role.
6. `obsolete` - only when explicit evidence establishes replacement/removal intent.
7. `unknown` - default when evidence is insufficient.

`obsolete` is normally reviewer- or user-established rather than inferred by the inventory script.

## Reachability evidence

Use [reference-graph.md](reference-graph.md) for the root registry, typed edges, declared roots, and coverage boundary.

Before declaring a resource unused, trace at least:

- `SKILL.md` links, images, reference-style links, and literal resource paths;
- transitive links from referenced resources;
- host adapter paths such as icons/assets metadata;
- script imports and explicit local paths;
- evaluator/test roots and their consumers;
- template, validator, example, packaging, and report-template consumers;
- known dynamic/build/runtime roots declared by the operator;
- replacement/migration notes and compatibility aliases;
- exact external references when the user provides them.

A shallow grep, absence of imports, or one incomplete root set does not prove obsolescence.

## Generated evidence

Directory names are signals, not authority. In particular, `dist/`, `build/`, `node_modules/`, `coverage/`, `out/`, and `target/` may contain generated material, but Agent Skills permits arbitrary additional directories. Namespace naming alone must never produce an auto-removable `generated` state.

Strong mechanical cache signals include known tool-cache directories such as `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `.tox/`, `.nox/`, and bytecode files such as `*.pyc`/`*.pyo`.

A weak generated-like candidate may be reclassified `generated` only with explicit approval plus corroborating evidence such as:

- `user-explicit-generated`;
- `target-doc`;
- `generator-command`;
- `manifest-generated`;
- `reproducible-generated`.

Reachability or protection still overrides generated evidence.

## Duplicate tiers

Keep automatic deletion authority narrow:

- `exact`: byte/hash identical; may mechanically receive `duplicate` if not protected/reachable.
- `normalized`: highly similar normalized lines; review candidate only.
- `structural`: same shape or repeated guidance with edits; reviewer judgment only.
- `semantic`: same intent expressed differently; reviewer judgment only.

Only `exact` can become `duplicate` mechanically. Before consolidating any non-exact candidate compare mode, audience, unique constraints/examples, activation implications, validator/evaluator role, and external compatibility references.

## Scaffold and template guard

A file containing unresolved fill directives, example tokens, or template variables may be legitimate. If it is referenced by the workflow or copied/filled at runtime, classify it `used` even if it looks like scaffold. Only explicit evidence can establish that scaffold is obsolete.

## Protected evidence guard

Fixtures, evals/tests, expected outputs, golden files, snapshots, contracts, benchmark reports, evaluator evidence, receipts used for comparison, secrets/credentials, archives, and user-declared protected files are `blocked` by default. Cleanup convenience never overrides protection.

## Classification evidence strength

Strong evidence includes:

- deterministic root/consumer graph with the exact `root_registry` recorded;
- file hash proving exact duplication;
- package metadata or manifest references;
- target documentation naming a replacement/deprecation/generator;
- user instruction explicitly marking a resource obsolete or generated;
- validator/test evidence;
- migration completion evidence with updated consumers.

Weak signals such as naming, age, fill-marker text, apparent lack of imports, a generated-like namespace, or similarity alone cannot justify deletion.

## Report shape

| Path | State | Roots/consumers | Evidence | Decision | Risk | Validation |
|---|---|---|---|---|---|---|
| `path/to/file` | `used` | `skill-entrypoint -> markdown-link` | Typed edge in frozen inventory | Preserve | Low | Reference graph |
