# Installation, Compatibility, and Release

## Installation

A distributed archive contains exactly one top-level `mago/` directory. Extract or install that directory into the host's supported skill location without merging it with another Mago version. Keep the package read-only except when intentionally developing a new version.

Install the declared runtime dependencies before validation:

```bash
python -m pip install -r requirements.txt
python -B scripts/validate_runtime_dependencies.py .
```

Validate and build a distribution from outside the skill folder:

```bash
python -B scripts/validate_distribution.py \
  --target . \
  --output-dir <external-output>/distribution \
  --report <external-output>/distribution-validation.json \
  --jobs 1
```

For installation-only verification of an extracted package:

```bash
python -B scripts/validate_runtime_dependencies.py .
python -B scripts/validate_release_metadata.py .
python -B scripts/validate_skill_package.py .
```

The output directory must be outside the skill root. Reports, caches, credentials, generated evidence, transaction workspaces, and old archives are excluded.

## Compatibility policy

- `release.json.version` follows semantic versioning for the skill distribution, not for cycle/spec identities.
- Patch releases repair documentation, validators, or scripts without intentionally changing canonical artifact contracts.
- Minor releases may add backward-compatible validators, templates, modes, or optional artifacts. A stricter contract must provide an explicit external migration rule. A legacy runtime path is permitted only when the machine-readable compatibility contract explicitly enables it; current handoff v3 and priority v2 contracts do not enable legacy runtime support.
- Major releases may change canonical schemas, ownership, or required workflow. They require migration notes and cannot silently rewrite existing packages.
- External SDD adapter versions are caller-supplied and explicit. Values such as `latest`, `current`, or `unknown` are rejected by executable adapters.
- Python compatibility, runtime dependencies, and supported OpenAI products are declared in `release.json`; `requirements.txt`, importability, installed versions, and `agents/openai.yaml` are validated before packaging.

## Coordinated three-package preflight

Mago remains an independent package, but exact ecosystem compatibility requires the staged Mago, Magia, and Nomia candidates to be checked together before installation:

Use the release-time coordinator as the canonical proof that the same three staged candidates, local suites, archives, contracts, and ecosystem harnesses passed together:

```bash
python -B scripts/validate_ecosystem_release.py \
  --mago <mago-root> --magia <magia-root> --nomia <nomia-root> \
  --output-dir <external-output>/coordinated-release \
  --json-output <external-output>/coordinated-release-ledger.json
```

The command accepts explicit peer roots only at release time and never imports or executes peer internals during normal Mago planning. A passing package-local validator alone is not a coordinated-release attestation.

## Upgrade and rollback

1. Validate the current three-package set and preserve all three archive checksums.
2. Extract the candidate into a separate folder; never overlay a live package.
   Apply this independently to all three package candidates in isolated staging folders.
3. Run every package-local gate, then the coordinated compatibility, routing, provenance, positive-flow, and negative-flow gates.
4. Verify that all three staged versions and shared contract hashes match before any live switch.
5. Switch the host from the old set to the complete candidate set as one operational decision; do not intentionally run a mixed-version set.
6. Roll back by restoring the prior validated folder; do not downgrade canonical planning artifacts without an explicit `adapt` or migration decision.
   For a coordinated release failure, restore all three prior validated folders and checksums as one rollback decision.

## Support boundary

The package supports Mago-owned planning artifacts and deterministic planning validators. It does not implement product code, execute deployment, produce runtime evidence, accept business/security risk, or provide automatic regulatory approval. Live model routing and plan quality remain separate behavioral evidence and must not be inferred from static package validation.
