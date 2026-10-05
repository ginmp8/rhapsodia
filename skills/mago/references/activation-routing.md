# MAGO Activation Routing

> Storage binding: `artifact-native` is the default. Board/registry/cycle mechanics in retained mode references apply only after explicit `legacy-board` selection. Authority, privacy, evidence, validation, and handoff rules apply in both profiles.

## Should Activate

Activate Mago when the requested outcome is a Mago-owned technical planning artifact, a read-only diagnosis of why such planning cannot proceed, or validation/reconciliation of existing Mago planning state. Typical intents include discovery, ordering, adapt, prepare/define/refine, technical design, planned ADRs, complexity reduction, product-only planning, task-only planning, task reshaping, and read-only reconciliation.

For the default native profile, write eligibility depends on a resolved repository/owner root, `work_item_id` or existing planning identity, evidence source, rigor/lifecycle selection, and one internal mode. A Board, cycle, shared registry, Workspace, or UI is not required. If only the mode or blocker can be established, Mago may load read-only far enough to report it but must not mutate.

For read-only reconciliation, activate `reconcile` only when canonical Mago intent and supplied Magia evidence are both identifiable. Preserve both authorities and emit only a non-authoritative reconciliation result.

## Should Not Activate

Do not activate Mago for product-code implementation, runtime execution, deployment, test execution, runtime evidence gathering, delivery governance, release notes, stakeholder/portfolio reporting, or general documentation that is not a Mago planning artifact. Route execution work to Magia and governance/status ownership to Nomia.

## Ambiguous Cases

Requests such as "plan this", "make a package", "update docs", or "turn this roadmap into specs" are ambiguous until the planning owner, repository/owner root, work item or existing planning identity, evidence source, and intended artifact family can be resolved. Ask only for the smallest missing input when an interactive safe default cannot be derived; in unattended work, preserve the unknown and stop before mutation if it blocks correctness.

If `legacy-board` is explicitly selected, additionally resolve its required Board/cycle/registry identity. Never infer `legacy-board` merely because old Board files exist.

## Edge Cases

If a prompt mixes planning with implementation or governance, keep only the Mago-owned planning portion and hand off the rest. If a selected mode document exposes only Board-specific write mechanics while native mode is active, do not invent a native write path; remain read-only or block until the native contract supplies one.

## Local Scenario Oracle

Scenario metadata uses one shared meaning: `expected_owner` is `mago`, `magia`, `nomia`, or `none`; `expected_activation: true` means Mago is the resolved owner, `false` means Mago must not be selected, and `null` means owner resolution is still open. `diagnostic_entry_allowed: true` permits read-only loading only to resolve ambiguity or report an in-scope blocker; it never permits mutation before owner and write inputs are resolved.

## Regression and Adversarial Coverage

Activation coverage must include positive, negative, ambiguous, edge, regression, and adversarial cases. Protect product-only/task-only separation, native-vs-legacy storage selection, and prompts that try to smuggle implementation, runtime validation, release governance, or noncanonical documentation into a planning request.

## Measurement Limits

The deterministic scenario validator is a package gate, not a live model-routing benchmark. Static oracle conformance can catch package regressions and unclear expected boundaries but does not measure live selection accuracy. For release-critical routing claims, execute a live prompt review against the same frozen scenario corpus and record it separately.

## Measured routing evidence

Use `scripts/live_routing_harness.py` with `references/live-routing-result-schema.json` for live routing evidence. Never report structural scenarios as measured live-model accuracy.
