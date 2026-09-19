# Capability Delta Review

Use this only when there is a meaningful baseline and candidate, prior report, or declared capability contract to compare. Do not invent a baseline from intuition.

## Goal

Describe what the candidate can demonstrably do relative to the baseline without confusing structural change with behavioral improvement.

## Capability identity

Name capabilities by observable responsibility or contract, not by implementation detail. Examples: `validate-package`, `compare-baseline-candidate`, `route-ambiguous-prompts`, `preserve-last-known-good-package`.

For each capability record:

- canonical owner/source;
- baseline evidence;
- candidate evidence;
- consumers or affected workflow paths;
- validation/evaluator evidence;
- classification;
- impact and confidence.

## Classifications

- `added`: candidate declares and integrates a capability absent from the baseline; behavioral proof may still be pending.
- `preserved`: capability and its relevant contract remain materially intact.
- `regressed`: candidate weakens, breaks, disconnects, or makes a previously supported capability unreachable.
- `removed-authorized`: capability is removed with explicit scope/compatibility authorization and required migration/rejection behavior.
- `removed-breaking`: supported capability disappears without sufficient authorization or compatibility evidence.
- `redundant`: candidate adds another path/resource for an already-owned capability without demonstrated value and with duplication/drift cost.
- `unproven`: text or structure suggests a delta, but the evidence cannot establish the capability or effect.

Do not use `improved` as a classification unless executed/supplied behavioral evidence directly supports the improvement. A static review can say `added with behavioral proof pending` or `preserved with stronger structural validation`.

## Evidence rules

Strong evidence, in descending order:

1. executed scenario/runtime evidence bound to exact baseline/candidate identities;
2. validators/tests proving the relevant contract;
3. canonical workflow/output/contract changes with reachable integration;
4. examples/templates/docs used only as supporting evidence;
5. filenames, keyword counts, or file counts as discovery only.

A new script that is never called by the workflow is not a capability gain. A removed file is not a capability loss when the same owned behavior remains reachable and validated through the canonical path.

## Comparison safeguards

- Compare the same capability definition across both versions.
- Separate capability existence from quality, speed, reliability, portability, and evidence strength.
- Do not infer behavioral gain from a higher static score.
- Do not count a host-specific adapter as a portable-core capability unless the core contract requires it.
- Treat changed evaluator/scenario definitions as a comparability gap, not an improvement.
- Record authorized simplification as `preserved` or `removed-authorized`, not regression, when evidence supports it.


## Self-generated candidate profile

When the candidate was produced by the same logical skill family that is being reviewed, record generation provenance without turning this reviewer into an orchestration layer:

- `candidate_origin = self-generated`;
- `controller_identity` when supplied;
- `baseline_identity`;
- `candidate_identity`;
- `generation_id` when supplied.

Review the candidate with the same capability taxonomy as any other baseline/candidate comparison. Self-generation is neither evidence of improvement nor evidence of regression by itself.

Additional safeguards:

- do not accept the candidate's own prose as proof that a capability was `added` or `preserved`;
- for behavioral capability claims, prefer executed/supplied evidence produced outside the candidate mutation surface;
- treat changes to the capability definition, evaluator, or acceptance rule between baseline and candidate as a comparability gap;
- flag a candidate that removes or weakens the mechanisms required to review its next generation as `regressed` or `unproven`, depending on evidence;
- keep controller provenance separate from capability ownership. The controller generated the candidate; it does not automatically own every changed capability;
- do not select other improvement specialists from this review. Return capability findings to the caller.

## Recommended matrix

| Capability | Baseline evidence | Candidate evidence | Classification | Behavioral proof | Impact |
|---|---|---|---|---|---|

Use `measured`, `observed`, `inferred`, `planned`, or `blocked` evidence language from the report contract.
