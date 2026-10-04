# Semantic Preservation

## Required invariant categories

Before editing, make these explicit in the refactor contract:

1. activation and non-activation boundaries;
2. target scope, mutation rights, blocked/protected paths;
3. authority hierarchy: modality, negation, precedence, exceptions, trust boundaries, and instruction-versus-data rules;
4. workflow/order and tool/filesystem/environment protocol;
5. safety/security/privacy/compliance constraints;
6. validation, stop, package, rollback, and final-freeze gates;
7. evidence/citation/reference/source/path/line traceability duties;
8. compatibility/version/migration commitments;
9. output contract;
10. progressive-loading/resource-loading duties and load conditions;
11. minimum readable execution.

Each invariant is preserved verbatim, replaced by an equivalent, moved with an explicit placement/load rule, or intentionally changed with authority and evidence. Ambiguous equivalence is a failure, not a token win.

## Authority and typed procedural semantics

Treat a skill as a procedural contract, not a bag of semantically similar sentences. Preserve the relations that determine execution:

- mandatory versus optional duties;
- `must`/`must not` and equivalent modality;
- negation scope;
- rule precedence and exceptions;
- preconditions, guards, thresholds, and stop conditions;
- trusted instructions versus untrusted data/content;
- workflow ordering, dependencies, and tool protocol;
- output/evidence obligations and who may authorize an exception.

A shorter statement is not equivalent when it changes any of these relations even if lexical or embedding similarity remains high.

## Placement and load conditions

For contract v2, classify material invariants as `entrypoint`, `reference`, or `either`.

- `entrypoint`: the instruction must be available before branch-specific loading decisions occur.
- `reference`: the invariant may move out of `SKILL.md` only with a non-empty `load_condition` that tells the agent when it must load the referenced detail.
- `either`: either location is acceptable if reachability and readability remain intact.

A local reference that merely exists does not prove operational equivalence. Validate both reachability and the instruction that causes it to be loaded when needed.

## Protected surfaces

Preserve or explicitly authorize/evidence any change to:

- URLs;
- local/file paths;
- commands and code blocks;
- env vars;
- schema names/keys;
- CLI flags;
- proper nouns/product/host names;
- versions/dates;
- numeric limits/thresholds;
- required output sections and paired duties such as `evidence/citation`, `source/path`, and `file/line`.

Automatic extraction is supporting evidence, not semantic authority. Put critical values and relations in the frozen contract.

## Verification types

- `contains`: required literal/phrase remains in candidate content.
- `regex`: deterministic pattern must match.
- `local_reference`: required local path remains reachable from `SKILL.md`.
- `manual`: semantic/readability judgment requires explicit review evidence.
- `scenario`: requires executed behavioral scenario evidence for a behavioral claim.

Never convert `manual` or `scenario` to a weaker mechanical check merely to get green. See [Behavioral Equivalence](behavioral-equivalence.md) for claim boundaries.

## Safe deletion

Delete only when all are true:

1. content is duplicate, scaffold, stale, generic filler, or strictly weaker than another preserved rule;
2. no required invariant, authority relation, or protected surface depends on it;
3. no reference, script, template, example, evaluator, or consumer depends on it;
4. local-reference/progressive-loading validation passes and moved rules retain explicit load conditions;
5. the readability floor still passes.

## Readability floor

A candidate must still make trigger/non-goals, authority, inputs, order, protection, evidence/citation duties, validation, output, and stop conditions directly executable without reconstructing omitted rules from inference. Prefer a few extra tokens over ambiguous critical instructions.
