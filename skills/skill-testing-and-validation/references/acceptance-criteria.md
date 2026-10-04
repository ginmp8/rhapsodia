# Acceptance criteria

## Hard gates

A testing/validation repair is complete only when all applicable hard gates have evidence:

- baseline preserved before mutation;
- target and working directory canonicalized;
- material target identity bound to executed gate evidence;
- relevant environment fingerprint captured without arbitrary environment/secret dumping;
- required command selection follows declared precedence/tie-breakers;
- each executed gate has a machine-readable receipt and preserved target exit code;
- read-only acceptance gates did not mutate material target bytes, or the mutation was explicitly expected and re-baselined;
- failures have a formal category/code before repair;
- protected evidence stayed unchanged unless exact authorization was recorded;
- the exact failing gate/command was rerun after repair;
- changed scripts parse/compile;
- target-owned tests/validators run when applicable;
- validators used as acceptance gates are repeatable/idempotent for unchanged material bytes/comparable environment;
- any declared reliability requirement has explicit stability evidence; retry-to-green is never sufficient;
- generated/changed tests used as semantic acceptance evidence have test intent and an adequate oracle source;
- for suspected faulty behavior, a bug-finding oracle is not derived only from current SUT output;
- coverage, mutation score, or another proxy metric is never the sole correctness gate;
- final required gate states yield the fixed overall conclusion;
- no success claim is based on a `not-run` or `blocked` gate;
- final candidate is frozen after its last pass.

## Overall gate state

For required gates:

1. any `fail` => overall `fail`;
2. else any `blocked` => overall `blocked`;
3. else all required applicable gates `pass` and at least one ran => overall `pass`;
4. else => overall `not-run`.

Reliability and oracle/effectiveness are separate acceptance overlays, not new gate states. When reliability is required:

- `stable/pass` satisfies the reliability overlay;
- `unstable` fails it;
- `inconclusive` blocks it;
- `not-assessed` leaves it not-run.

A gate-state `pass` does not override a failing required overlay.

## Skill-package gates

For reusable skill packages, additionally check when relevant:

- one root `SKILL.md`;
- `SKILL.md` YAML frontmatter passes the canonical structural validator; malformed YAML is a hard failure, not a warning;
- portable lowercase `name`/description frontmatter;
- referenced local files exist and remain within package root;
- non-template files have no unresolved scaffold markers;
- Python scripts compile; shell scripts parse when Bash capability exists;
- executable tests/validators cover negative as well as positive cases;
- activation examples include non-activation, ambiguity, failure, regression, reliability/oracle boundaries, and anti-cheating cases;
- package excludes caches, `.git`, old archives, logs, secrets, and temporary evidence;
- package/report outputs remain outside the validated target tree;
- package output and report/receipt paths do not alias one another;
- archive root uses the skill name, not a temporary staging directory;
- package replacement occurs only after the staged archive validates;
- package receipt includes SHA-256 of the committed archive.

## Proxy metrics

Coverage, mutation score, fuzz duration/case count, and similar quantitative signals describe explored or challenged surfaces. They do not independently establish correctness. Mutation evidence additionally requires a green baseline and recorded tool/operator context when the score is material.

## Evidence labels

Use `executed`, `supplied`, `static`, `planned`, or `blocked` to describe how evidence was obtained. Do not promote static structure, proxy metrics, or planned scenarios into executed behavioral correctness evidence.
