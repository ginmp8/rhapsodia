# Acceptance criteria

## Hard gates

A testing/validation repair is complete only when all applicable hard gates have evidence:

- baseline preserved before mutation;
- target and working directory canonicalized;
- relevant environment fingerprint captured;
- required command selection follows declared precedence/tie-breakers;
- each executed gate has a machine-readable receipt and preserved target exit code;
- failures have a formal category/code before repair;
- protected evidence stayed unchanged unless exact authorization was recorded;
- the exact failing gate/command was rerun after repair;
- changed scripts parse/compile;
- target-owned tests/validators run when applicable;
- validators used as acceptance gates are repeatable/idempotent for unchanged bytes/environment;
- final required gate states yield the fixed overall conclusion;
- no success claim is based on a `not-run` or `blocked` gate;
- final candidate is frozen after its last pass.

## Overall state

For required gates:

1. any `fail` => overall `fail`;
2. else any `blocked` => overall `blocked`;
3. else all required applicable gates `pass` and at least one ran => overall `pass`;
4. else => overall `not-run`.

## Skill-package gates

For reusable skill packages, additionally check when relevant:

- one root `SKILL.md`;
- `SKILL.md` YAML frontmatter passes the canonical structural validator; malformed YAML is a hard failure, not a warning;
- portable lowercase `name`/description frontmatter;
- referenced local files exist and remain within package root;
- non-template files have no unresolved scaffold markers;
- Python scripts compile; shell scripts parse when Bash capability exists;
- executable tests/validators cover negative as well as positive cases;
- activation examples include non-activation, ambiguity, failure, regression, and anti-cheating cases;
- package excludes caches, `.git`, old archives, logs, secrets, and temporary evidence;
- archive root uses the skill name, not a temporary staging directory;
- package replacement occurs only after the staged archive validates;
- package receipt includes SHA-256 of the committed archive.

## Evidence labels

Use `executed`, `supplied`, `static`, `planned`, or `blocked` to describe how evidence was obtained. Do not promote static structure or planned scenarios into executed behavioral evidence.
