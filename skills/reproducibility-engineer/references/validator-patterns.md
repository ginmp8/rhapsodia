# Validator Patterns

## At a Glance

- **Purpose:** Define independent validator, diagnostic, preflight, repair, and receipt patterns for objective acceptance gates.
- **Load when:** Adding or changing a validator, machine-readable receipt, output-path preflight, target-class check, or diagnostic-driven repair rule.
- **Decision impact:** Determines what a validator may prove, required receipt identity, path-collision checks, target-class assertions, diagnostic stability, repair ordering, and independence boundaries.
- **Do not load when:** No objective/mechanical gate is being designed or modified.

## Contents

- Core rule
- Receipt shape
- Output path preflight
- By target class
- Diagnostics
- Repair ordering
- Independence traps

## Core rule

A validator should test properties the generator cannot simply assert about itself. Prefer machine-readable receipts and stable diagnostic codes.

## Receipt shape

A useful validator receipt contains:

```json
{
  "receipt_version": 1,
  "status": "pass",
  "stage": "validation",
  "checks": [
    {"code": "schema/valid", "status": "pass", "subject": "candidate.json", "evidence": {}, "supported_fixes": []}
  ],
  "errors": 0,
  "warnings": 0,
  "metrics": {},
  "hashes": {"source_sha256": "...", "artifact_sha256": "..."},
  "recovery": []
}
```

Use stable stages and diagnostic codes for argument/preflight, source snapshot, validation, commit, rollback, and packaging failures when those stages exist. Persist file receipts atomically and flush stdout receipts before exit so large JSON remains complete. Do not require hashes when they add no value.

## Output path preflight

Before any write, validate both the authored output and its canonical/resolved destination. Reject:

- wrong output type/extension, including after symbolic-link resolution;
- output aliases of inputs, evaluators, protected files, or sibling receipts;
- symbolic-link cycles;
- relative outputs that escape their allowed root after canonicalization;
- multi-output target collisions.

Preflight failure must leave existing bytes untouched. When commit/rollback fails after staging, preserve recovery paths instead of deleting the remaining evidence.

## By target class

### Structured text/JSON/YAML
Check:
- parseability;
- schema/version;
- required fields;
- enums/ranges;
- referential integrity;
- semantic invariants;
- forbidden extra fields when contract requires closure.

### Code generation
Check:
- parse/compile/build;
- focused tests;
- type/lint/static analysis when project-owned;
- contract/interface compatibility;
- forbidden placeholders/stubs;
- dependency/lockfile policy;
- runtime smoke test when meaningful.

Do not treat compilation as semantic correctness.

### Documents/spreadsheets/slides
Check:
- file format validity;
- render/open cycle;
- overflow/cutoff/collision where detectable;
- formulas/recalculation/errors for spreadsheets;
- required sections/content;
- generated-file integrity.

Perceptual polish still requires visual review.

### Web/UI artifacts
Check:
- actual browser load;
- console errors;
- viewport overflow/reflow;
- interaction smoke tests;
- accessibility checks appropriate to scope;
- screenshot/perceptual review separately.

Do not pass by clipping content or hiding overflow.

### Research/analysis
Check:
- source presence and provenance;
- date/version/jurisdiction where material;
- citation-to-claim traceability;
- required uncertainty labels;
- output sections;
- unsupported numeric claims;
- source hierarchy compliance when enforceable.

Do not pretend the validator can prove a judgment is correct.

### Agent execution evidence
Check environment/provenance, stochastic trial evidence, and multi-stage lineage only when those surfaces are material. Use `scripts/validate_execution_evidence.py` rather than free-form self-attestation.

- environment: required identities, input/output digests, and material drift across paired arms;
- stochastic evaluation: trial uniqueness/outcomes, declared stop rule, derived uncertainty/`pass^k`, judge identity/calibration when used, and independent replication for strong claims;
- lineage: unique nodes, resolvable dependencies, acyclic graph, node/output digests, canonical-output agreement, and explicit invalidation/replay metadata.

A valid profile proves contract conformance, not that an external model/API is deterministic or that the candidate is behaviorally superior.

### Tool/action workflows
Check:
- preconditions;
- authority/scope;
- request shape;
- idempotency key/retry rules when applicable;
- postconditions;
- rollback/compensation evidence;
- action receipt/audit trail;
- last-good preservation and rollback/recovery evidence when mutation is transactional.

## Diagnostics

Prefer:

`code + subject + evidence + supported_fixes + severity`

Stable codes make repair behavior and regression tests reproducible.

## Repair ordering

Fix upstream causes before downstream symptoms:

`schema/input -> semantic placement/state -> routing/dependencies -> presentation -> polish`

For non-visual skills use the analogous order:

`contract -> mechanics -> behavior -> delivery -> presentation`.

## Independence traps

Weak validator designs include:
- checking only that the generator wrote "status: pass";
- using the same function to generate and validate without independent invariants;
- parsing only a preview while claiming full-file validation;
- validating a stale last-good artifact after candidate generation failed;
- accepting absent evidence as zero errors;
- validating only the authored output name while a symlink resolves to a different file type;
- writing an artifact and receipt to paths that alias each other;
- emitting a success receipt before the described bytes are committed.
