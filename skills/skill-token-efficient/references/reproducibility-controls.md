# Reproducibility Controls

## Evidence model

Keep four claims separate:

- **token evidence**: counts produced by one pinned method on baseline and candidate;
- **structural evidence**: files, local refs, protected literals, schemas, scripts, package shape, hashes;
- **behavioral/semantic evidence**: activation, scope, output behavior, invariant equivalence, readability;
- **runtime evidence**: actual host/tool execution when required.

A pass in one layer does not imply another.

## Baseline and candidate

Before any edit, preserve exact baseline bytes outside the mutation workspace and record a deterministic tree identity. `apply` should mutate a staged candidate copied from that baseline. The baseline, frozen evaluators, fixtures, expected outputs, and generated baseline evidence are protected.

Rollback is normally promotion-by-replacement: if the candidate fails, discard it and keep the installed/last-good target unchanged. If in-place mutation is unavoidable, record a byte-for-byte backup and restore plan before editing; stop if reliable restore is unavailable.

## Tokenization contract

Pin the method before comparison and use it unchanged for both arms.

- `estimator-v1`: standard-library deterministic lexical estimator; portable and reproducible, but not exact for a specific model.
- `tiktoken:<encoding>`: optional exact count for that encoding when `tiktoken` is installed. Record encoding and package version. Do not silently fall back.

Never label `estimator-v1` as an exact model-token count. Cross-host comparisons should prefer a portable pinned method unless a model-specific count is the explicit goal.

Pin the comparison scope too: `entrypoint` counts only `SKILL.md`; `instructions` counts `SKILL.md` plus progressively reachable references/examples/templates; `all-text` also counts scripts/evals/config text. Use `instructions` for prompt/instruction optimization and report `all-text` separately when package-source size matters.

## Refactor contract

Create/fill `assets/templates/refactor-contract.json` for the target, then validate it before mutation. The contract must identify:

- tokenization method;
- semantic invariants for activation, scope, safety, validation, evidence/citation, compatibility, output contract, readability, and progressive loading;
- verification type for each invariant: `contains`, `regex`, `local_reference`, `manual`, or `scenario`;
- protected literals for URLs, paths, commands, env vars, schemas, flags, proper nouns, versions, and numbers.

`manual` and `scenario` are intentionally not converted into fake mechanical proof. They remain hard gates until real review/execution evidence is recorded.

## Evaluator freeze

Freeze the exact scenario prompts, fixtures, expected outputs, validators/graders, thresholds, and comparison configuration that will decide acceptance. Candidate code must not modify the frozen copy. If a frozen evaluator is wrong, invalidate that comparison, fix/freeze a new evaluator, and restart.

## Local references and progressive loading

`SKILL.md` is the control plane. Detailed rules may move to one-level references when the load rule remains explicit. Validation must build a deterministic local-reference graph, fail broken local refs, and fail when a baseline-reachable instruction reference becomes unreachable without an explicitly authorized migration.

Do not reduce apparent context cost by orphaning required references.

## Source and output integrity

When external files or repository evidence materially determine equivalence, capture the exact source bytes and hashes before analysis; for pinned VCS evidence, prefer immutable revision reads over a mutable working tree. Re-baseline if source identity changes.

Before packaging or writing receipts, canonicalize output paths and reject output aliases with the target/input, protected evidence, or sibling receipt. Preflight must happen before mutation. A failed preflight leaves last-good bytes unchanged.

## Final freeze and receipt

After every applicable gate passes:

1. compute the final candidate tree identity;
2. make no further edits;
3. stage the package privately;
4. validate the staged package;
5. compute package SHA-256;
6. emit a parseable receipt tied to the exact candidate/package bytes;
7. commit outputs atomically where supported.

A post-pass edit invalidates the freeze. A failed package must not replace the last-good artifact. Preserve recovery paths if rollback is incomplete.

## Host-neutral skill root

Resolve `<skill-root>` from the current package containing `SKILL.md`; never require one host-specific install directory. Hosts such as GitHub Copilot or Cursor may place the same Agent Skills-compatible package under locations such as `skills/`, `.agents/skills/`, `.github/skills/`, `.cursor/skills/`, or `.claude/skills/`. These are placement adapters, not workflow semantics. Keep relative references inside the package and treat `agents/openai.yaml` or other host metadata as optional adapters unless the target explicitly makes them part of its contract.
