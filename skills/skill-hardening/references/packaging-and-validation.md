# Packaging and Validation

## Portable package contract

A package must contain exactly one skill root with `SKILL.md`; its portable frontmatter must satisfy the open Agent Skills core; all package-local references must resolve; and the archive must exclude `.git`, caches, generated evidence/reports, secrets/credentials, symlinks, old ZIPs, and unresolved scaffold markers outside templates.

Portable frontmatter requires valid `name` and `description` and may include `license`, `compatibility`, `metadata`, and experimental `allowed-tools`. Do not require descriptions to be lowercase or to meet an arbitrary word count. Archive root must match `SKILL.md:name`. Host-specific frontmatter extensions belong to explicit host profiles/adapters, not the portable core.

Optional `scripts/`, `references/`, `assets/`, `examples/`, `evals/`, and host adapters are not packaging prerequisites unless the target actually references/needs them.

## Commands

```text
<PYTHON> scripts/inventory_skill.py --target <TARGET> --output <WORK>/inventory.json
<PYTHON> scripts/hardening_audit.py --target <TARGET> --output <WORK>/audit.md --json-output <WORK>/audit.json
<PYTHON> scripts/validate_portability.py --target <TARGET> --hosts portable-core,openai,codex,claude,copilot,cursor --json-output <WORK>/portability.json
<PYTHON> scripts/validate_hardened_skill.py --target <TARGET> --min-score 85 --profile portable --json-output <WORK>/validation.json
<PYTHON> scripts/package_skill.py --target <TARGET> --output <OUTPUT>/skill.zip --validate --profile portable --baseline-tree-sha256 <BASELINE_SHA256> --json-output <WORK>/package-receipt.json
<PYTHON> scripts/package_skill.py --validate-only <OUTPUT>/skill.zip --profile portable
```

Add `--require-scenarios`, `--scenario-min-per-core-type`, `--require-coexistence`, or `--hosts` to `validate_hardened_skill.py` only when the acceptance claim needs those gates.

Resolve `<PYTHON>` to an available Python 3.10+ launcher. Bundled scripts use the standard library only.

## Deterministic delivery

Build to a private temporary archive, normalize ZIP entry ordering/timestamps/permissions, validate before replacement, compute identities, atomically replace the requested output, and preserve the last-good archive on failure. Reject package/receipt outputs inside the frozen target or aliases of each other.

Receipt v3 keeps candidate/target/archive identities and additionally records `builder_sha256`, `validation_profile`, and optional `baseline_tree_sha256`. This is provenance-lite evidence, not a claim of SLSA conformance.

## Blocking gates

1. Portable folder/spec validation passes.
2. Requested host-profile structural validation passes when claimed.
3. Referenced paths resolve; no blocked/cache/secret/symlink/scaffold path is included.
4. Builder creates and validates a single-root archive whose root matches `SKILL.md:name`.
5. Package output is atomically committed only after validation; last-good output survives failure.
6. Receipt identities correspond to the exact committed candidate/archive and record builder/profile identity.
7. Frozen candidate/evaluator evidence did not change after final pass.

Scenario/behavior gates are separate and required only by the behavioral claim; packaging success does not prove activation/output quality.

When the package builder itself changes, build twice from the same frozen candidate and confirm identical archive SHA-256 values.
