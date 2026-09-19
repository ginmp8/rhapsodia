# Resource Integration and Deletion Safety

Use for resources in `references/`, `scripts/`, `assets/`, `assets/templates/`, `examples/`, `evals/`, `tests/`, metadata, and other package paths.

## Deterministic trace first

Before calling a resource unused or removable, inspect all applicable evidence dimensions:

1. imports;
2. markdown links;
3. exact path/name references;
4. runtime/script consumers;
5. tests;
6. validators/auditors;
7. examples and scenario suites;
8. packaging/archive rules, including broad directory traversal;
9. migration, legacy, compatibility, rollback, and conversion paths;
10. handoffs to adjacent roles/skills.

`scripts/inventory_skill.py` emits these dimensions in `resource_trace`. Absence of a detected edge is evidence of graph orphaning only; it is not proof of obsolescence.

## Integration evidence

A resource is normally `current` when at least one of these is evidenced:

- `SKILL.md` or an authoritative reference loads it conditionally;
- a script imports/reads/writes/validates it;
- a validator/schema delegates contract authority to it;
- a template is explicitly copied/filled/rendered/validated;
- an evaluator is frozen and used for acceptance;
- an example is declared non-authoritative and points to the real contract;
- a runtime asset is intentionally included by metadata/output rules;
- a migration-only resource is intentionally reachable only from migration/compatibility mode.

## Safe removal gate

Removal is allowed only when all are true:

- final status is `obsolete` or an explicitly approved duplicate consolidation;
- all ten trace dimensions were considered and recorded;
- no current/migration/rollback consumer remains;
- authority owner and successor are identified when a contract is involved;
- evaluator/test/validator dependencies are migrated without weakening gates;
- package/runtime behavior is checked after removal;
- rollback/last-known-good evidence exists;
- the removal maps to a diagnosed inconsistency, not a cleanliness preference.

If any item is unknown, classify `unknown` or `blocked` and keep the resource.

## Duplicate handling

Byte-identical files are a useful mechanical signal, not a deletion instruction. Semantic duplicates may differ in consumers, authority, host adapters, or migration role. Consolidate only after consumer tracing and contract ownership are explicit.

## Asset and metadata caution

Binary/static assets and host metadata can be legitimately consumed outside readable text. If no reliable consumer evidence exists, prefer `unknown` over `obsolete`.
