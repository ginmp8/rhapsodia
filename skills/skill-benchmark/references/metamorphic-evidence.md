# Metamorphic Evidence for Skill Benchmark

## At a Glance

- **Purpose:** Interpret paired model/agent outputs under a predeclared *metamorphic relation* (MR) when an exact golden answer is unavailable.
- **Load when:** Benchmark inputs include controlled paraphrases, irrelevant context, reordering, intended changes, or an explicit metamorphic-reliability claim.
- **Decision impact:** Requires independently justified preconditions, frozen pair identities, a narrowly defined relation/oracle, separation of suspected violations from confirmed faults, and comparability before claiming change.

## Ownership and boundary

`skill-benchmark` is a **read-only evidence consumer**: it does not design/run a general MT harness, auto-generate candidate prompts, mutate evaluator fixtures, or prove that outputs are semantically equivalent. Prefer existing direct oracles when available. Use `skill-harness` for constructing/running MT trials and `skill-testing-and-validation` for generalized executable MT strategy when those owners are available; preserve standalone operation by accepting independent supplied evidence.

## Minimum experimental design

1. Identify `base_case_id`, `variant_case_id`, input transformation, and the necessary relation. Predeclare and justify semantic preconditions **before** seeing target outputs.
2. Classify the transformation as **invariance** (meaning truly preserved), **expected change** (negation/authority/scope changed), or **invalid/unverified** (meaning may have drifted). Do not require identical routes for a change to permission or requested action.
3. Freeze suite, evaluator, host/model/runtime, catalog-pressure profile, visibility, trial policy, and baseline/candidate identities. Counterbalanced/order-controlled runs help diagnose position effects.
4. Compare observable **contract fields**, not raw wording. Separate routing, stop, constraints, authority, tool requests, evidence handling, and substantive answer correctness.
5. Treat a failed necessary relation as `candidate-violation`. Independent inspection must confirm the input precondition and evaluator correctness before calling it a semantic defect. Mark unresolved cases `inconclusive`.
6. Report denominator by *relation group*, number of pairs and trials, failures, adjudicated genuine defects, and uncertainty. Correlated variants of one base case are **not independent observations**; avoid spurious p-values and naive pass-rate inflation.
7. Benchmark target improvements only on paired, frozen, comparable executions. Any difference in material identities makes a strict improvement attribution `not-comparable` until intentional rebaseline.

## Optional mechanical evidence sidecar

The CLI validates only observed fields and hashes; it cannot prove that the input transformation preserved meaning or that the reported observation really ran.

```text
<PYTHON> scripts/validate_metamorphic_evidence.py --input <EVIDENCE.json> --json-output <REPORT.json>
<PYTHON> scripts/validate_metamorphic_evidence.py --baseline <BASE.json> --candidate <CANDIDATE.json> --json-output <PAIR_REPORT.json>
```

Minimal JSON envelope (`schema_version: 1`): `arm`, `suite_sha256`, `evaluator_sha256`, `runtime_sha256`, `evaluator_visibility`, `trial_policy`, nonempty `relations[]`. Each relation declares unique `id`, distinct `base_case_id`/`variant_case_id`, `transformation`, `precondition_evidence`, `relation`, `evidence_status`, and `base`/`variant` observation objects for `executed`/`supplied` cases. Supported *mechanically checkable* relations: `same-route` (string `route`), `same-stop` (boolean `stop`), `same-constraints` (set of `constraints` strings) and `same-authority` (string `authority`). A changed permission class is **not** automatically an invariant; adjudicate relation applicability first.

`planned` and `not-run` remain `not-measured`. `executed` and `supplied` are assertions in the input, not independently authenticated provenance. Reports separate `consistent`, `candidate-violation`, and `not-measured`; a successful validator exit is only a **structural success**, not an MT pass or true fault diagnosis. v2/v3 benchmark behavioral contracts remain unchanged; this is an optional adjunct, not an additional 0–100-score factor.

## Research and limitations

- Segura et al. (2016), peer-reviewed overview: https://doi.org/10.1109/TSE.2016.2532875
- Chatterjee et al. (2024), prompt perturbation sensitivity: https://aclanthology.org/2024.findings-emnlp.852/
- Cho et al. (2025), preprint LLM MT study: https://arxiv.org/abs/2511.02108. Manual adjudication found substantial false positives among MR violations in their NLP setup. This does not establish a universal false-positive rate for skills.
