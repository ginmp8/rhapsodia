# Integrity and Recovery

Use for baseline identity, external evidence, output safety, packaging, receipts, and rollback.

## Immutable baseline first

Before target mutation, capture the exact target bytes with:

```text
<PYTHON> scripts/skill_harness_snapshot.py capture \
  --target <TARGET_SKILL_PATH> \
  --snapshot-dir <work-dir>/baseline-snapshot \
  --manifest <work-dir>/baseline-manifest.json
```

The helper fails closed on secret-like files and escaping/directory symlinks. If that blocks mutation, report the blocker rather than copying sensitive material.

Use the snapshot as the before-state. Do not silently rebuild the baseline after seeing candidate results.

## External and VCS evidence

If research files, repositories, benchmark fixtures, or other external inputs materially affect a comparison, record their exact identity before analysis. For pinned VCS revisions, prefer reads from immutable revision objects over the mutable working tree. Dirty files, branch movement, replacement refs, or regenerated files must not silently redefine a pinned source.

## Frozen evaluators

Evaluator fixtures, expected outputs, scoring rubrics, baseline evidence, and gate thresholds are protected after the comparison contract is set. If an evaluator is wrong, invalidate the experiment, repair it separately, freeze a new baseline, and restart; never edit it to make the candidate pass.

## Output preflight

Before any write:

- validate the authored output type/extension;
- resolve/canonicalize the destination and validate again;
- reject symbolic-link cycles;
- reject package/report destinations inside the target skill;
- reject aliases between package, report, input, evaluator, protected path, or sibling output;
- preserve existing last-good bytes on preflight/validation failure.

Alias means canonical or same-file identity, not just equal path strings.

## Recovery-aware commit

For package + receipt/report delivery:

1. stage all candidate outputs privately in their destination filesystem;
2. validate the staged ZIP and compute hashes from those exact bytes;
3. preserve existing target files as backups;
4. commit all staged outputs;
5. remove backups only after every commit succeeds;
6. on failure, restore last-good outputs;
7. if rollback is incomplete, preserve recovery files and report exact paths.

Do not delete recovery evidence merely to make the directory look clean.

## Durable receipts

A package receipt should identify at least:

- `receipt_version`;
- `status` and `stage`;
- validation profile;
- target and skill name;
- source tree hash;
- package SHA-256 and size;
- file/entry count;
- validation result;
- recovery paths when needed.

Write file receipts atomically and flush stdout before exit. Do not emit `status: pass` until the described package bytes are committed.

## Final identity check

After the final pass and before delivery, verify the target was not edited after packaging by comparing its current tree hash with the `source_tree_sha256` in the package receipt. Any post-pass edit requires rerunning affected gates and packaging again.
