# MAGO Activation Routing

Use this reference during hardening, packaging, or when a prompt could be confused with implementation, governance, general documentation, or repository execution work.

## Should Activate

Activate MAGO for canonical repository planning intent: discovery, ordering, adapt, prepare-define, define, refine, technical-design, reshape-tasks, define-product, refine-product, define-tasks, and refine-tasks. A resolved `BOARD_ROOT` is required before writes, not before identifying the planning mode or reporting missing canonical inputs. The expected output must be a MAGO-owned planning artifact, a read-only blocker diagnosis, or a validator report for such artifacts.

For read-only reconciliation, activate `reconcile` only when canonical Mago intent and supplied Magia evidence are both identifiable; preserve both authorities and emit only a non-authoritative reconciliation report.

## Should Not Activate

Do not activate MAGO for product-code implementation, runtime execution, deployment, test execution, runtime evidence gathering, delivery governance, release notes, stakeholder status, portfolio reporting, or general documentation outside the canonical board tree. These are handoff cases.

## Ambiguous Cases

Treat requests such as "plan this", "make a package", "update docs", or "turn this roadmap into specs" as ambiguous until the user or repository evidence establishes the canonical board root, board_id, cycle_id, and artifact family. Ask only for the smallest missing input when a safe default cannot be derived.

## Edge Cases

If the prompt is in scope but lacks required identifiers, activate the mode decision only far enough to name the blocker; do not write files. If the prompt mixes planning with implementation or governance, keep the planning boundary explicit and hand off the non-MAGO portion.

## Local Scenario Oracle

Native activation scenarios use one shared meaning: `expected_owner` is `mago`, `magia`, `nomia`, or `none`; `expected_activation: true` means Mago is the resolved owner, `false` means Mago must not be selected, and `null` means owner resolution is still open. `diagnostic_entry_allowed: true` permits read-only loading only to resolve ambiguity or report an in-scope blocker; it never permits mutation before owner and canonical write inputs are resolved.

## Regression and Adversarial Coverage

The activation scenario suite must include positive, negative, ambiguous, edge, regression, and adversarial cases. Regression cases preserve previously fixed routing behavior, such as product-only and task-only separation. Adversarial cases protect against prompts that try to smuggle implementation, runtime validation, release governance, or noncanonical docs into a planning request.

## Measurement Limits

The deterministic scenario validator is a package gate, not a live model-routing benchmark. Treat its metrics as static oracle conformance: useful for catching package regressions, insufficient coverage, and unclear expected boundaries. For release-critical changes, supplement it with a live prompt review using the same scenario suite and record live results separately; do not mark live routing as measured unless prompts were actually executed.

## Measured routing evidence

Use the shared external contract in `scripts/live_routing_harness.py` and `references/live-routing-result-schema.json`. Structural scenarios are not live-model accuracy evidence.
