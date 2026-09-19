# Architecture Evidence Model

**Contract version:** 1.0.0

Use this model before architectural judgment so repeated reviews begin from comparable evidence.

## Evidence classes

| Class | Meaning | Examples |
|---|---|---|
| `mechanical` | directly produced by deterministic inspection | file paths, hashes, links, imports, counts |
| `declared-contract` | explicitly stated by package instructions/metadata | activation, modes, stop conditions, declared loading |
| `behavioral` | produced by actually executed scenarios/validators/harnesses | scenario result, validator behavior |
| `supplied` | evidence provided by the user or external report but not independently executed | benchmark report, incident note |
| `derived` | deterministic calculation from identified evidence | package identity, duplicate edge set |
| `judgment` | architectural interpretation | cohesion, maintainability, ownership fit |

Never silently convert one class into another.

## Deterministic inventory contract

`scripts/inventory_skill_package.py` emits schema `2.0.0` and:

- `package_identity_sha256`: hash over ordered relative paths and file hashes; independent of absolute package path;
- `files`: canonical path-ordered file evidence;
- `resource_map`: resource role, owner role, consumer evidence, and consumer status;
- `ownership_map`: deterministic owner-role classification with its basis;
- `dependency_map.edges`: observed path/link/import relationships;
- `progressive_loading_map.skill_md_declared_resources`: resources directly declared from `SKILL.md`;
- local links and broken-link facts.

The inventory is mechanical evidence only. It cannot decide cohesion, obsolescence, deletion safety, or architecture.

## Resource taxonomy

Use these stable roles:

- `control-plane`: root `SKILL.md`;
- `host-adapter`: host-specific metadata such as `agents/openai.yaml`;
- `reference`: reasoning/instruction resource loaded when needed;
- `script`: deterministic mechanics, validation, transformation, inventory, packaging;
- `template-asset`: output skeleton copied or filled;
- `runtime-asset`: binary/data/boilerplate consumed by outputs or runtime;
- `example`: demonstration evidence;
- `eval`: planned or executed scenario/evaluator resource;
- `package-resource`: resource not fitting a known role.

Resource role is not integration status.

## Ownership-role taxonomy

The deterministic map uses role ownership, not organizational people/teams:

- `control-plane`
- `host-adapter`
- `review-guidance`
- `deterministic-mechanics`
- `output-contract`
- `runtime-asset`
- `example-evidence`
- `evaluation-evidence`
- `unknown`

A reviewer may refine ownership only with package evidence. Never invent a human/team owner from a filename.

## Consumer tracing

`consumer_evidence` is a starting point, not a complete proof of use. Before destructive recommendations, check:

1. direct links/path mentions;
2. imports and dynamic imports;
3. file reads/writes and path joins;
4. glob/wildcard consumers;
5. template/validator/package-builder references;
6. examples/evals;
7. runtime/asset-only declarations;
8. host-specific and external consumers suggested by package evidence.

### Consumer states

- `observed-consumer-evidence`: at least one deterministic consumer signal exists;
- `unresolved-no-evidence`: the mechanical scan found no consumer signal; this is **not** orphan evidence.

Architectural review may later classify a resource as:

- `integrated`
- `weakly-integrated`
- `misplaced`
- `duplicate`
- `obsolete`
- `generated-debris`
- `orphaned`
- `unknown`

`orphaned`, `obsolete`, and removal advice require positive review evidence beyond `unresolved-no-evidence`.

## Dependency map semantics

Dependency edges are evidence types, not semantic coupling scores. A path mention may be documentation, a contract, or a runtime consumer. Do not infer architectural importance from edge count alone.

## Evidence IDs

For durable reports, assign stable run-local IDs:

- observations: `obs-001`, `obs-002`, ...
- judgments: `jud-001`, `jud-002`, ...
- recommendations: `rec-001`, `rec-002`, ...

Judgments reference observation IDs. Decisions may reference observation and judgment IDs. Recommendations reference the evidence that justifies them.
