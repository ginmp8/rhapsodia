# Reproducibility contract

## What is deterministic
Given the same normalized source assertions, mapping, namespace and executable versions, identity, source replacement, typed query ordering, fixed stdlib analytics and exported JSON/text are stable. Conflicts have an explicit source-rank tie-break. Transaction failures preserve last-good state; identical source revisions are no-ops.
Use a logical graph SHA-256 over canonical current data. Physical SQLite bytes are not an equivalence oracle: page order, history insertion order, journals, vacuum and storage layout may differ without changing knowledge. Do not compare raw DB hashes as proof that an ingestion result changed.

## What is not guaranteed
LLM/vision/speech interpretation, compiler coverage under different reference sets, optional-library algorithm output, OS fonts and cross-browser pixels can vary. Preserve versions/model identity, extraction settings, input hashes and uncertainty. Never relabel these as deterministic because a seed or confidence exists.
Optional analytics must be explicitly selected; an ambient installed library cannot silently change a stdlib algorithm. A changed mapping/extractor invalidates source extraction even if file bytes did not change.

## Validation
Freeze source corpus, accepted requirements and test oracles before the related candidate change. Preserve old regression fixtures. Record every relevant fail/repair/rerun, not only the last pass. Test idempotency, rollback, cross-source preservation, direction, finite limits, outputs/aliases and offline behavior. Re-run final gates after any edit; package only the frozen candidate.
Trace research source -> finding -> requirement -> implementation/test externally. Trace coverage proves accounting, not truth, model accuracy or universal completeness. Keep behavioral, structural, browser and host evidence separate.
