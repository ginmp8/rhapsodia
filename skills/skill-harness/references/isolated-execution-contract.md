# Isolated Execution and Evaluator Visibility Contract

Use this contract only when a harness will execute behavioral scenarios or ingest execution evidence. Static audits do not need a runtime sandbox.

## Goal

Prevent a candidate skill from gaining accidental access to evaluator-only material, mutable state, or prior-run artifacts that would make baseline/candidate comparisons unreliable. Isolation is capability-based, not Docker-specific.

## Visibility zones

Classify every execution input before a measured run:

| Zone | Candidate may read? | Examples |
|---|---:|---|
| `candidate-visible` | yes | scenario prompt, declared user files, target skill/package, explicitly allowed runtime context |
| `runner-only` | no unless required by the host | launcher config, orchestration metadata, temporary credentials or handles |
| `evaluator-only` | no | hidden graders, expected answers, private rubrics, holdout labels, scoring thresholds not required by the task |
| `post-run-only` | no during execution | adjudication output, comparison metrics, final grader decisions |

A rubric may be candidate-visible when the task itself requires that rubric. In that case it is not a hidden grader and must not be described as hidden or blind.

## Isolation levels

Record one of:

- `workspace`: fresh dedicated work directory; mutable artifacts/caches from prior runs are absent;
- `process`: workspace isolation plus a separate process/runtime boundary;
- `container`: process isolation inside a fresh container or equivalent sandbox;
- `external-host`: execution occurs in a host whose isolation cannot be independently enforced here; record the host profile and limitations.

`workspace` is the portable minimum. Do not require Docker or a specific sandbox implementation as core semantics.

## Run evidence

A measured behavioral run should bind at least:

- `run_id`;
- `arm`: `without-skill`, `baseline`, `candidate`, or `single`;
- target/source SHA-256 when a skill is present;
- evaluator SHA-256 and scenario-suite SHA-256;
- host/runtime profile;
- isolation level;
- candidate-visible manifest SHA-256;
- evaluator-only manifest SHA-256 when hidden evaluator assets exist;
- trace reference/hash when the runner can produce one;
- leakage check result;
- scenario results.

Use `assets/templates/execution-evidence.json.template` as the portable envelope.


## Self-hosted execution profile

When the evaluated skill is participating in its own improvement, bind the run to the generation without turning the Harness into an improvement orchestrator.

Record an optional `self_hosting` object:

```text
generation_id
controller_identity_sha256
baseline_identity_sha256
candidate_identity_sha256
controller_candidate_separated
controller_read_only
```

Rules:

- the controller is execution provenance, not a benchmark arm;
- the active controller must remain read-only during candidate execution;
- `candidate_identity_sha256` must equal the candidate arm target identity;
- `baseline_identity_sha256` must equal the baseline arm target identity when that arm is captured;
- controller and candidate identities must differ for a material self-improvement candidate;
- evaluator-only assets remain outside both controller-authoring and candidate-execution visibility when a blind/hidden claim is made;
- Harness reports execution integrity only. Promotion, hypothesis selection, and specialist routing remain outside Harness ownership.

A self-hosting envelope may be used for baseline and candidate runs from the same generation. Both arms must name the same `generation_id` and controller identity when they are later compared.

## Leakage gate

A hidden-grader or blind-evaluation claim is invalid when any evaluator-only file, expected outcome, holdout label, grader prompt, or post-run adjudication is available to the candidate before completion. If exposure is intentional because the rubric is part of the task, classify it as candidate-visible and drop the hidden/blind claim.

A measured comparison is also invalid when mutable outputs from a previous arm are reused as candidate inputs without an explicit scenario requirement.

## Optional no-skill control

Use `without-skill` only when it answers a real question such as whether a newly created skill adds capability over the host baseline. For an existing-skill update, the immutable prior version remains the primary baseline. A no-skill arm may be additional context; it must not replace the prior-version baseline for regression claims.

All compared arms must use the same scenario/evaluator identities and materially equivalent host configuration. Otherwise mark the delta `not-comparable`.

## Trace discipline

A trace is evidence, not ground truth. Prefer references/hashes over embedding secrets or full sensitive payloads. A trace should expose enough to identify the run, invoked tools/actions, outcome, and failing scenario without leaking evaluator-only content.

Do not require a trace when the host cannot produce one. In that case mark trace evidence `unavailable` and avoid claims that depend on inspecting execution internals.

## Stop conditions

Do not call behavioral evidence measured when:

- hidden evaluator assets were candidate-visible;
- arm identities or scenario/evaluator hashes differ for a claimed comparison;
- prior-run mutable state contaminated a later arm;
- required result rows are incomplete;
- the runner cannot distinguish executed evidence from planned/simulated results;
- a trace is required by the declared acceptance contract but cannot be produced or identified.
