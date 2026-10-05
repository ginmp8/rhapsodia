# Versioning and Compatibility

The package version in `VERSION` and the machine output contract version solve different problems.

## Package version

Use semantic versioning for the skill package:

- patch: documentation, diagnostics, tests, or implementation repairs that preserve public decision semantics;
- minor: additive capability that keeps existing valid inputs/results compatible;
- major: activation/authority changes or incompatible skill-package behavior.

The current package version is `2.0.2`. The v2 envelope remains unchanged; this patch makes the Top-100 control plane more self-sufficient, replaces vague long-document previews with decision-useful previews, and strengthens preview/reference-depth regression checks without changing public decision semantics.

## Decision envelope version

`contract_version: decision-engine/2` is the current machine interface.

Compatible within `decision-engine/2`:

- clearer instructions/rubrics that do not change field meaning;
- stronger validators that enforce rules already declared by the contract/schema;
- new examples/evals/diagnostics;
- internal implementation changes that preserve accepted envelope semantics.

Require a new envelope contract version when a consumer must change because of:

- renamed/removed required fields;
- changed meaning of an existing field/status/type;
- new required field with no backward-compatible default;
- changed type or allowed value domain that invalidates previously contract-compliant output for a new semantic reason.

## Compatibility policy

Do not silently coerce v1 envelopes into v2 or add hidden legacy shims. Consumers must either keep a v1-compatible package or explicitly migrate using [migration-v1-to-v2.md](migration-v1-to-v2.md). This keeps contract identity auditable and avoids ambiguous semantics.
