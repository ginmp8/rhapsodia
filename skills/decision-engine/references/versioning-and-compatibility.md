# Versioning and Compatibility

The package version in `VERSION` and the machine output contract version solve different problems.

## Package version

Use semantic versioning for the skill package:

- patch: documentation, diagnostics, tests, or implementation repairs that preserve the public decision semantics;
- minor: additive capability that keeps existing valid inputs/results compatible;
- major: activation/authority changes or other incompatible skill-package behavior.

## Decision envelope version

`contract_version: decision-engine/1` is the current machine interface.

Compatible within `decision-engine/1`:

- clearer instructions/rubrics that do not change field meaning;
- stronger validators that enforce rules already declared by the contract/schema;
- new examples/evals/diagnostics;
- internal implementation changes that preserve accepted envelope semantics.

Require a new envelope contract version when a consumer must change because of:

- renamed/removed required fields;
- changed meaning of an existing field/status/type;
- new required field with no backward-compatible default;
- changed type or allowed value domain that invalidates previously contract-compliant output for a new semantic reason.

Do not add legacy shims speculatively. Add migration guidance only when an actual prior public contract must coexist with a new one.
