# Brownfield Discovery Summary

Use this reference at the end of a bounded discovery frontier when a compact handoff is more useful than loading every inspected file. The summary is repository evidence, not a design decision or execution record.

## Required sections

- inspected frontier and evidence timestamp;
- likely capability boundary and confidence;
- primary modules and entry points;
- supporting files and dependency edges;
- existing patterns to preserve;
- contracts, schemas, migrations, security boundaries, and operations affected;
- existing validators and tests;
- unknowns, conflicts, and access gaps;
- candidate files likely to be affected, clearly labeled provisional;
- recommended next frontier or readiness for `order`;
- explicit non-claims: no implementation, runtime proof, owner, business priority, technical criticality, execution sequence, or final architecture.

Use `assets/templates/brownfield-discovery-summary.md.template` when a durable summary is needed. Keep detailed evidence in candidate docs and discovery artifacts; do not duplicate full repository content in the summary.
