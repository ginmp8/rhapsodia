# Reproducibility contract

## Canonical identity

Record these identities separately:

- cycle identity: `cycle_version`;
- execution identity: `spec_id`;
- functional identity: `feature_key`;
- functional release identity: `(feature_key, feature_version)`;
- task identity: explicit `taskNNN` when present;
- filesystem identity: canonical relative path plus SHA-256 of the exact bytes;
- change identity: transaction id derived from the normalized semantic operation plan and candidate hashes; absolute staging-source paths are excluded from identity.

Do not substitute one identity for another.

## Input normalization

Normalize before making decisions:

- mode: lowercase enum `order|define|refine|decompose|audit|normalize`;
- `cycle_version`: string matching `NN.NN.NN`;
- `spec_id`: lowercase `spec` plus at least three digits;
- `feature_key`: lowercase kebab-case;
- `feature_version`: `vMAJOR.MINOR.PATCH` without omitted components;
- status/type/classification/phase: canonical lowercase enums from `convention.md`;
- paths: relative to the declared cycle root, resolved before mutation;
- dependencies: lists with duplicates removed only when duplicate entries are semantically identical; preserve original identity order when it is already valid.

Do not lowercase or rewrite free-form titles, requirements, notes, evidence, or unknown fields just to normalize the package.

## Deterministic mode resolution

Explicit mode always wins. Explicit MAGO aliases map through `mago-adaptation.md`. Without an explicit mode, select only when exactly one observable intent matches. If selection remains ambiguous, the only safe automatic mode is read-only `audit`; mutation is blocked with `MODE_AMBIGUOUS`.

## Deterministic new spec allocation

When a new spec is requested without explicit `spec_id`:

1. hash and lock the current catalog as a precondition;
2. parse all valid `specNNN` ids;
3. choose `max(numeric id)+1`, zero-padded to at least three digits;
4. never fill cancelled or historical gaps implicitly;
5. re-check the catalog hash immediately before commit;
6. block on conflict instead of choosing another id silently.

For append ordering use `max(order)+10`. For insertion, require explicit before/after anchors and choose a free integer between them. When none exists, return `ORDER_REBALANCE_REQUIRED`. Rebalancing existing orders is a separate explicitly authorized operation.

## Feature identity and version rules

The same `feature_key` may legitimately appear in multiple specs. Within one cycle:

- the same `(feature_key, feature_version)` cannot be owned by two specs;
- later evolution must have a greater semantic version and greater `order`;
- later evolution must depend on the immediately previous spec for that `feature_key`;
- changing an existing spec's `feature_key` is an identity change and blocks unless the caller explicitly requests a migration with evidence.

Version bump mapping is mechanical only after semantic change classification is supported by evidence. No evidence -> no guessed bump.

## Stable task ids

For new or newly decomposed tasks use:

```md
- [ ] Task 1: Short title
  - Task ID: task001
```

Rules:

- `taskNNN` is the stable identity; display numbering is not identity;
- never reuse a removed/cancelled task id inside the same spec;
- new task id = `max(existing canonical task number)+1`;
- preserve existing ids and done history;
- a dependency must reference a stable task id and appear earlier in execution order;
- legacy tasks without `Task ID` remain readable and must not be renumbered during unrelated refinement;
- normalization may add explicit ids only with a recorded mapping and no ambiguity.

## Unknown and legacy files

Unknown files are preserved by default. Report them, hash them for before/after checks when a whole package is staged, and never delete or rewrite them solely because the convention does not recognize them.

Legacy names map only during `normalize` or explicit MAGO adaptation. Normalization is additive by default:

- snapshot legacy input;
- write canonical output to a non-aliasing destination;
- detect collisions before writing;
- preserve legacy source bytes;
- record old -> new mapping in the change receipt;
- do not claim migration complete while unknown/conflicting files remain unresolved.

## Preconditions

Before any mutation:

- cycle root resolves inside the allowed workspace;
- each output resolves inside the cycle root;
- source, target, receipt, evaluator, and protected paths do not alias;
- the durable receipt resolves outside the canonical cycle tree;
- no output path resolves through a symlink alias;
- every update target has the expected current SHA-256;
- every create target declares `ABSENT` and is actually absent;
- selected `spec_id` and functional identity are unique;
- mandatory source artifacts for the selected mode are present;
- the operation plan conforms to its declared schema: unknown fields block, hash preconditions are syntactically valid even for no-op writes, and `post_validate.mode` cannot differ from or weaken the selected mutation mode;
- no unresolved recovery state exists from a prior failed transaction;
- an exclusive cycle transaction lock can be acquired before snapshot/staging.

A precondition failure changes no canonical bytes. A preserved lock or recovery workspace is evidence, not clutter: do not delete it automatically merely to continue.

## Transaction, concurrency, and idempotency

Use one logical transaction for all files changed by one planning action.

1. acquire an exclusive lock scoped to the canonical cycle root;
2. reject unresolved recovery workspaces from earlier transactions;
3. preflight all targets, aliases, protected paths, receipt location, and expected-before hashes;
4. snapshot the exact before-tree outside the canonical cycle and verify the live tree still matches that snapshot;
5. stage candidate bytes privately and verify staged hashes against the hashes used to construct the transaction identity;
6. assemble a complete candidate tree from the exact before snapshot plus staged writes;
7. validate candidate structure and before/candidate transition invariants before mutating live targets;
8. re-check the live tree and target hashes immediately before commit;
9. preserve last-good target bytes;
10. commit staged bytes;
11. validate committed structure and before/committed transition invariants;
12. require the committed tree hash to equal the exact prevalidated candidate tree hash;
13. roll back all committed targets on failure and verify restoration;
14. emit one durable receipt for the final state and remove transient transaction state only after success is durable.

The transaction id is stable for the same semantic operation and candidate bytes even when temporary source filenames/directories differ. It may include the canonical cycle identity/path, mode, authorization, target-relative paths, expected-before hashes, and candidate hashes; it must not depend on incidental staging locations.

If current target bytes already equal candidate bytes, mark the target `noop`. If every target is `noop`, validate the current postcondition, return `no_change`, and do not rewrite canonical bytes.

## Partial failure and recovery

`failed_recovered` means all mutated targets were restored to their verified before bytes. A retry may proceed only after preconditions are rechecked.

`failed_recovery_required` means rollback was incomplete. Stop further mutation, preserve backup/candidate paths, and require recovery before a new operation.

Never delete recovery evidence after incomplete rollback.

## Receipt contract

A change receipt must identify:

- `receipt_version`;
- final `status` and `stage`;
- transaction id;
- canonical cycle root;
- every target path;
- expected-before hash;
- observed before hash;
- candidate hash;
- committed after hash or `noop`;
- exact before-tree, candidate-tree, and committed-tree hashes when mutation occurred;
- candidate structural validation and candidate transition-validation results;
- committed structural validation and committed transition-validation results;
- failure and recovery path when applicable.

Success refers only to the exact committed bytes. Do not emit success before post-validation and exact candidate/committed identity checks.

## Validation precedence

Repair failures upstream first:

`identity/input -> lock/recovery -> path/preconditions -> exact snapshot -> catalog/manifest -> dependencies -> tasks -> candidate transition invariants -> precommit recheck -> commit/recovery -> committed validation -> receipt`

Never weaken a validator, remove an invariant, delete unknown evidence, or renumber stable ids to make a candidate pass.
