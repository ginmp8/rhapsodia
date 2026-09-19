# Quality Gates

Use these gates before claiming a skill is ready.

## Agent Skills Structural Gates

- exactly one root `SKILL.md` exists;
- `name` and `description` satisfy the Agent Skills specification;
- standard optional frontmatter is validated when present;
- host-specific frontmatter/extensions are intentional and their portability impact is recorded;
- referenced local files exist and remain inside the package;
- no scaffold markers, caches, generated reports, old archives, or secrets are packaged.

## Portability Gates

- the portable core does not require a vendor-specific tool-call syntax or install path;
- host capabilities are described abstractly where possible;
- `agents/openai.yaml` is optional in the portable profile and required only when the OpenAI profile contract says so;
- host-only metadata is classified as adapter, optimization, required capability, or blocker;
- missing host capabilities produce `not-run` evidence instead of false passes;
- multi-host support does not duplicate the semantic skill without a lifecycle reason;
- portability/redesign emits an explicit matrix for `portable-core,openai,codex,claude,copilot,cursor` unless the user deliberately narrows scope;
- structural compatibility and runtime validation are reported separately.

Run `../scripts/validate_portability.py <target> --hosts portable-core,openai,codex,claude,copilot,cursor` when filesystem execution is available.

## Activation Gates

- activation and non-activation examples exist or are intentionally omitted with rationale;
- ambiguous cases define ask/proceed/handoff behavior;
- the description resists common false positives and false negatives;
- activation optimization uses realistic near-misses and adjacent-domain negatives rather than trivial irrelevant prompts;
- held-out activation cases remain uninvolved in tuning when final activation-improvement claims are made;
- boundaries and stop conditions are explicit.

## Architecture Gates

- one operational role or an explicit router explains the package;
- modes share vocabulary, evidence, and validation lifecycle;
- branch-specific detail lives outside the control plane;
- every important resource has a declared consumer;
- scripts are used for deterministic work, not ornamental complexity.

## Evaluation and Generalization Gates

When behavioral quality is part of the claim:

- lifecycle state was identified so completed stages were not unnecessarily repeated;
- existing conversation/artifact context was harvested before asking the user to restate requirements;
- net-new skills use `without-skill` as baseline when meaningful; existing-skill updates use an immutable prior-version baseline;
- candidate and baseline arms receive equivalent prompts, files, environment assumptions, and evaluator rules;
- objective properties use objective evaluators where practical, while subjective properties use appropriate independent/perceptual review;
- fixes target a general failure class rather than exact eval wording, filenames, fixtures, or examples;
- held-out cases support improvement/generalization claims when execution infrastructure allows;
- repeated work is promoted to reusable scripts/references/assets only when repetition is material across runs;
- process traces are considered when they reveal repeated waste, inconsistent routing, or hidden host dependency;
- efficiency metrics, when measured, remain secondary to correctness and semantic quality.

If these behavioral checks cannot run, mark them `not-run` and limit claims to structural hardening.

## Reproducibility Gates

For substantive creation, redesign, quality-upgrade, or explicit reproducibility work:

- the local `reproducibility-by-design` pass classifies the ceiling and material variance before specialist routing;
- controls are proportional to real failure modes rather than added ornamentally;
- `reproducibility-engineer` is classified as `invoked`, `checklist-only`, `not-applicable`, `unavailable`, or `cycle-prevented` with rationale;
- material mechanical variance is controlled at the lowest reliable layer;
- validators/evaluators are independent enough to detect candidate failure;
- repair loops have diagnostic inputs and bounded stop conditions;
- frozen evaluator assets and protected evidence are unchanged;
- material source evidence is snapshotted or immutably identified before analysis when acceptance depends on exact bytes;
- source, evaluator, candidate, artifact, and receipt identities remain distinct when those evidence layers exist;
- output paths are canonicalized and aliases with inputs/protected files/sibling receipts are rejected before mutation when applicable;
- last-known-good outputs survive failed validation/commit and incomplete rollback preserves explicit recovery paths;
- delivery identity is traceable through durable receipts/hashes tied to the exact committed bytes when package reproducibility matters;
- subjective/stochastic ceilings are stated rather than disguised as determinism;
- deterministic controls did not introduce eval-specific overfitting.

## Change Acceptance Gates

For existing skills:

- material changes receive `skill-change-gate` review or equivalent checklist evidence;
- blocking regressions in activation, semantics, safety, portability, validation, packaging, output contract, or evidence discipline are repaired before acceptance;
- accepted trade-offs are explicit.

## Code and Script Gates

- changed scripts have safe command interfaces and clear failures;
- deterministic packagers preflight authored/resolved destinations, reject package/receipt aliases, validate staged bytes, commit atomically, and do not replace a good archive/receipt with a failed candidate;
- rollback failures preserve/report recovery evidence instead of deleting it;
- archive creation blocks traversal, symlinks, caches, secrets, and old packages;
- added/changed scripts have syntax/smoke-test evidence or are marked `not-run`;
- dependencies are minimal and declared.

## Evidence Gates

Report separately:

- structural evidence;
- behavioral evidence;
- runtime evidence;
- perceptual/editorial evidence;
- efficiency evidence when measured.

Do not claim benchmark or behavioral improvement from static validation.

## Final Package Gate

Deliver `skill.zip` only when:

- local quality and portability gates pass;
- target-owned mandatory validators/tests pass or the user explicitly scoped them out without implying readiness;
- frozen evaluators remain unchanged;
- required change acceptance does not block the candidate;
- package validation passes;
- the exact final archive exists and its durable receipt/hash corresponds to the frozen candidate;
- package and receipt targets do not alias each other or the frozen source tree;
- no edits occurred after the final pass.
