# Mutation and Safety Policy

## Allowed Scope

Default writable scope is the target skill folder only.

Common allowed files:

- `SKILL.md`;
- `agents/openai.yaml`;
- `references/*.md`;
- `scripts/*` when deterministic validation or packaging is needed;
- `assets/templates/*` when templates are filled, copied, or rendered by the workflow;
- `examples/*` and `evals/*` only when benchmark design is explicitly in scope or no frozen evaluator exists yet.

## Blocked Paths

Do not edit or package:

- `.git/`;
- secrets, credentials, keys, tokens, private certs;
- generated reports and baseline evidence;
- old `skill.zip` files;
- caches and bytecode;
- benchmark fixtures and expected outputs after freeze;
- unrelated repository files;
- user-declared read-only files.

## Patch Discipline

Use one bounded hypothesis per patch batch.

Safe patch examples:

- refine frontmatter description;
- move long branch detail from `SKILL.md` to `references/`;
- add output contract;
- add stop conditions;
- repair broken local links;
- simplify duplicate guidance;
- add a deterministic validator;
- improve script error handling;
- reduce tokens after validation.

Unsafe patch examples:

- change evaluator and target behavior in the same batch;
- edit expected outputs to make tests pass;
- remove safety or validation rules to save tokens;
- delete unknown assets without usage analysis;
- package generated evidence or credentials;
- claim benchmark improvements without running or receiving benchmark results.

## Rollback

Before broad mutation, preserve enough state to revert:

- copy files or use version control when available;
- record changed files per patch;
- reject changes that fail gates;
- keep rejected hypothesis notes so the same weak idea is not repeated.

## Tool and Connector Boundaries

When target optimization depends on repository, Drive, or connected-source truth, use the available connector instead of guessing. If source access is unavailable, frame the change as a design assumption or stop when the assumption affects correctness.

## Security Floor

Every optimized skill must preserve or add:

- secret handling boundaries;
- safe filesystem scope;
- no fabricated validation or benchmark claims;
- no unsafe shell guidance;
- explicit package exclusions;
- clear stop conditions for missing evidence.
