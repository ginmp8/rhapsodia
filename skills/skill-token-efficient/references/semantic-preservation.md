# Semantic Preservation

## Required invariant categories

Before editing, make these explicit in the refactor contract:

1. activation and non-activation boundaries;
2. target scope, authority, mutation rights, blocked/protected paths;
3. workflow/order, tool/filesystem/environment rules;
4. safety/security/privacy/compliance constraints;
5. validation, stop, package, rollback, and final-freeze gates;
6. evidence/citation/reference/source/path/line traceability duties;
7. compatibility/version/migration commitments;
8. output contract;
9. progressive-loading/resource-loading duties;
10. minimum readable execution.

Each invariant is preserved verbatim, replaced by an equivalent, moved with an explicit loading rule, or intentionally changed with authority and evidence. Ambiguous equivalence is a failure, not a token win.

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

Automatic extraction is supporting evidence, not semantic authority. Put critical values in the frozen contract.

## Verification types

- `contains`: required literal/phrase remains in candidate content.
- `regex`: deterministic pattern must match.
- `local_reference`: required local path remains reachable from `SKILL.md`.
- `manual`: semantic/readability judgment requires explicit review evidence.
- `scenario`: requires executed behavioral scenario evidence for a behavioral claim.

Never convert `manual` or `scenario` to a weaker mechanical check merely to get green.

## Safe deletion

Delete only when all are true:

1. content is duplicate, scaffold, stale, generic filler, or strictly weaker than another preserved rule;
2. no required invariant or protected surface depends on it;
3. no reference, script, template, example, evaluator, or consumer depends on it;
4. local-reference/progressive-loading validation passes;
5. the readability floor still passes.

## Readability floor

A candidate must still make trigger/non-goals, inputs, order, protection, evidence/citation duties, validation, output, and stop conditions directly executable without reconstructing omitted rules from inference. Prefer a few extra tokens over ambiguous critical instructions.
