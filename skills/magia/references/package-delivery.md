# Package Delivery

Load only to validate, export, or package MAGIA itself.

## Archive Shape

- Build `skill.zip` from the final MAGIA folder only.
- Zip must contain exactly one top-level directory named after the skill folder.
- Archived root must contain `SKILL.md`, `VERSION`, `CHANGELOG.md`, `agents/`, `references/`, `scripts/`, `assets/`, `examples/`, and `evals/`.
- Exclude `.git`, caches, benchmark reports, test result folders, test-results.json, nested zips, temp outputs, secrets, credentials, private keys, tokens, and local env files.
- Remove stale generated noise when practical. `scripts/package_policy.py` is the single inclusion/exclusion contract: folder validation scans every package-eligible file and the packager archives that same candidate set, so known generated caches may remain after tests without entering or blocking the archive. Unknown or eligible binary/undecodable content still fails closed.

## Release and Compatibility Discipline

Treat a packaged MAGIA update as a versioned contract change, not only an archive operation.

1. Classify the release impact before changing `VERSION`: `patch` for compatible corrections, `minor` for compatible capabilities or resources, and `major` for intentional incompatible contract changes. Do not infer compatibility from file count alone.
2. Update `CHANGELOG.md` with the exact version/date, accepted hypotheses or repairs, compatibility impact, validation evidence, and any known migration or rollback requirement. Do not list rejected or unexecuted work as shipped.
3. For changes to activation, authority, modes, artifact ownership, CLI behavior, schemas, package shape, or execution-state semantics, record affected consumers and whether behavior is preserved, added, modified, or removed.
4. Require explicit migration/rollout and rollback/recovery evidence for incompatible or governed changes. A package must not be labeled ready when those gates are missing or failed.
5. Keep baseline hashes, optimization reports, test output, and prior archives outside the skill folder. Retain enough external evidence to reproduce the package decision without shipping generated reports inside `skill.zip`.
6. Validate the final folder, build the archive once from that validated state, validate the archive, and record its SHA-256. Any source change after packaging invalidates the readiness evidence and requires rebuilding.

A version bump, changelog entry, or successful zip command is not evidence of behavioral compatibility by itself.

## Standard Commands

```text
python scripts/validate_skill_package.py --target <skill-root>
python scripts/package_skill.py --target <skill-root> --output <output-dir>/skill.zip --validate
python scripts/validate_skill_package.py --target <skill-root> --zip <output-dir>/skill.zip
```

Folder and archive validators must pass before readiness is claimed.

## Gates

1. `SKILL.md` has lowercase frontmatter with only `name` and `description`.
2. Every local reference from `SKILL.md` resolves inside the package.
3. Required resources exist: agent metadata, references, scripts, MAGIA-owned templates, examples, evals.
4. Python scripts compile.
5. Scenario files keep planned fields null unless measured evidence exists.
6. The archive is cache-free, blocked-path-free, symlink-free, scanned for secret-like names and content, and has one top-level skill directory; source validation may ignore only generated paths explicitly excluded by `scripts/package_policy.py`. Oversized, binary, or undecodable members fail closed unless an explicit future allowlist contract defines a safe scanner for that content class.
7. No scaffold markers remain outside templates.

## Evidence to Report

Report package command, validator command, output path, archived file count, size, excluded categories, and residual risk. Never report behavioral scenario metrics as measured unless scenario prompts were executed and evaluator decisions recorded.
