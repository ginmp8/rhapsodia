# Report Contract

## Required report

Use this structure for substantive audit/apply/validation runs.

### 1. Target and scope
- target path/name;
- mode;
- host/runtime profile and detected capabilities when execution depends on them;
- baseline identity/snapshot;
- writable and protected scope;
- inspected/uninspected surfaces;
- host-specific adapters versus host-neutral core when portability is relevant.

### 2. Reproducibility ceiling
- target class;
- achievable guarantees;
- irreducible stochastic/subjective/external variance.

### 3. Baseline evidence
- target-owned commands and outcomes;
- inventory/audit paths;
- structural maturity before;
- evaluator freeze status;
- source snapshot/provenance identity when external evidence is material;
- whether pinned VCS evidence was read from immutable revision objects or only a mutable working tree;
- missing evidence.

### 4. Variability map
For each material source:
- surface;
- current variance;
- classification;
- chosen lower-level control;
- validation method.

### 5. Transformations
For each accepted change:
- hypothesis/problem;
- files changed;
- expected reproducibility effect;
- validation evidence;
- trade-offs.

Also list rejected/deferred transformations and why.

### 6. Evaluation
Separate:
- structural evidence;
- behavioral evidence;
- runtime evidence;
- perceptual/editorial evidence.

Include exact commands, pass/fail/not-run, paired comparison metrics, and significance output only when executed.

### 7. Final gates
State each applicable hard gate and its evidence. Include source-snapshot verification, output-alias preflight, last-good preservation/recovery, and receipt durability when those controls apply. Do not compress missing evidence into a pass.

### 8. Before/after
- structural maturity before/after, labeled structural;
- measured behavioral delta when available;
- token/time/rework trade-offs when measured;
- remaining nondeterminism.

### 9. Delivery
- frozen candidate identity;
- package/receipt path if produced;
- relevant hashes;
- authored and canonical output targets when alias safety matters;
- package validation;
- last-good preservation result;
- recovery paths if rollback was incomplete;
- receipt completeness/commit status;
- residual risks.

## Final status vocabulary

Use one of:
- `reproducibility-hardened`: hard gates pass and requested transformation completed;
- `validated-with-limitations`: applicable validation passed but material evidence remains unavailable;
- `partial`: useful bounded improvements exist but one or more required gates remain unresolved;
- `blocked`: safe completion is impossible with current evidence/scope.

Do not use `behaviorally improved` unless behavioral evidence was actually executed or supplied and meets the predeclared acceptance rule.
