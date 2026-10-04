# Architecture Evidence Model

**Contract version:** 2.0.0  
**Inventory schema:** 2.1.0

Use this model before architectural judgment so repeated reviews begin from comparable evidence. Inventory schema 2.1.0 is additive over 2.0.0: existing structural fields retain their meaning and `context_topology` is added as mechanical evidence.

## Evidence classes

| Class | Meaning | Examples |
|---|---|---|
| `mechanical` | directly produced by deterministic inspection | file paths, hashes, links, imports, counts, context topology |
| `declared-contract` | explicitly stated by package instructions/metadata | activation, modes, stop conditions, declared loading |
| `behavioral` | produced by actually executed scenarios/validators/harnesses | activation case result, validator behavior |
| `supplied` | evidence provided by the user or external report but not independently executed | benchmark report, incident note, catalog export |
| `derived` | deterministic calculation from identified evidence | package identity, duplicate edge set, change-radius count |
| `judgment` | architectural interpretation | cohesion, activation fit, maintainability, ownership fit |

Never silently convert one class into another.

## Architecture scope

Record exactly one context scope for the review:

- `single_skill` — the focal package is sufficient for the question;
- `skill_family` — adjacent skill activation/routing/ownership evidence materially affects the decision;
- `plugin_package` — a containing plugin/package/capability composition is the real boundary and the focal skill review may need a broader handoff.

Scope is evidence context, not an architecture decision. A focal package identity remains required for a canonical package report. When family/package evidence is missing, record the gap instead of inferring the surrounding system.

## Deterministic inventory contract

`scripts/inventory_skill_package.py` emits schema `2.1.0` and:

- `package_identity_sha256`: hash over ordered relative paths and file hashes; independent of absolute package path;
- `files`: canonical path-ordered file evidence;
- `resource_map`: resource role, owner role, consumer evidence, and consumer status;
- `ownership_map`: deterministic owner-role classification with its basis;
- `dependency_map.edges`: observed path/link/import relationships;
- `progressive_loading_map.skill_md_declared_resources`: resources directly declared from `SKILL.md`;
- `context_topology`: measured control-plane/direct-resource/reference-chain facts;
- local links and broken-link facts.

The inventory is mechanical evidence only. It cannot decide cohesion, activation collision, context quality, obsolescence, deletion safety, trust significance, or architecture.

### Context topology fields

`context_topology` contains at least:

- `skill_md_line_count`;
- `skill_md_word_count`;
- `direct_declared_resource_count`;
- `reference_chain_max_depth` — maximum local reference depth reachable from `SKILL.md`, where a direct reference is depth 1;
- `nested_reference_edge_count` — local reference-to-reference edges;
- `reachable_reference_count`;
- `unreachable_reference_count`.

These are facts, not thresholds. Depth, file count, or token proxies do not independently justify split/extraction.

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

Resource role is not integration status or trust status.

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

## Activation evidence

Use `references/activation-architecture.md` when catalog routing matters. Keep these separate:

- package-internal cohesion;
- focal activation declaration;
- adjacent catalog evidence;
- executed activation behavior.

If adjacent descriptions or runtime cases are unavailable, activation evidence is `unknown`/`partial`; absence of evidence is not proof of distinct activation.

## Evolution evidence

Use `references/evolution-architecture.md` for:

- quality/change scenarios;
- change radius;
- sensitivity points;
- tradeoff points;
- optional repository change-coupling evidence.

Static dependency edges and co-change are different evidence classes. Neither automatically implies a boundary. Historical co-change requires source/revision/time-range identity and remains corroborating evidence.

## Trust-boundary evidence

Use `references/trust-boundary-topology.md` when authority surfaces matter. Record executable, network, filesystem-write, external-tool, host-permission, and provenance signals as observed/declared/unknown evidence. Architectural topology does not establish security correctness; hand detailed security conclusions to a security reviewer.

## Consumer tracing

`consumer_evidence` is a starting point, not complete proof of use. Before destructive recommendations, check:

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

Scenario/sensitivity/tradeoff records reference observation/judgment evidence IDs where applicable. Judgments reference observation IDs. Decisions may reference observation and judgment IDs. Recommendations reference the evidence that justifies them.
