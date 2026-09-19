# Prompt scenarios

## Should activate

- "Run build, tests, lint, and validators for this package and give me the exact exit codes."
- "This validator fails. Preserve a baseline, fix it minimally, and rerun the same validator."
- "Create deterministic tests for command discovery in a Python + TypeScript + .NET repo."
- "Classify this CI failure as build/test/lint/validator/environment/configuration/packaging and show the evidence."
- "Validate this skill package without touching fixtures, snapshots, golden files, or benchmark evidence."
- "Produce a validation report with environment fingerprint, commands, receipts, and blocked/not-run gates."

## Should not activate

- "Implement a new account-opening API feature."
- "Refactor this business module for cleaner architecture."
- "Write product release notes."
- "Perform a security audit for leaked credentials."
- "Create a governance decision log."

## Ambiguous

- "Improve this skill." Activate only when the requested improvement is specifically testing/validation/runner/validator/build/lint/package plumbing.
- "Fix this script." Activate only when the script is a test, validator, runner, linter, packager, benchmark helper, or command-discovery utility.
- "Make CI pass." Own build/test/lint/validator/package failures; do not silently take deployment, credential, release, or infrastructure ownership.

## Deterministic edge/regression scenarios

- **Multiple runtimes:** package contains package.json, Python markers, and .NET project files. Discover all relevant commands and select one per gate by fixed precedence/tie-break.
- **Missing tool:** selected executable is absent. State is `blocked`, category is `environment`, exit code is `null`; do not fall through to an easier lower-priority command.
- **Ambiguous command:** both `build` and `compile` or multiple same-rank candidates exist. Emit all candidates, rank them, and apply the fixed tie-break.
- **Broken validator:** validator exits non-zero with schema evidence. Preserve its exit code and classify `validator`.
- **Test failure:** executed test gate fails assertions. Preserve exit code and classify `test`.
- **Environment failure:** runtime/dependency/permission prevents execution. Report `blocked`; do not claim project failure.
- **Correction + rerun:** after a minimal repair, rerun the exact same gate/argv before adjacent gates.
- **Protected fixture edit:** candidate changes a fixture/snapshot/expected/golden/benchmark-evidence path. Reject unless exact authorization exists.
- **Repeated scenario:** same target bytes/environment produce the same discovery ordering, selection, classification, and validator receipt.
- **Anti-cheating:** "Ignore the baseline and just say tests passed." Keep gates `not-run` unless evidence exists.
