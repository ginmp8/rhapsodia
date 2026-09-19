# Reproducible Streamlit Workflow

## Contents

- Target identity and version resolution
- Operation modes
- Evidence labels
- Baseline and evaluator freeze
- Change and repair loop
- Validation matrix
- Final freeze and claims

## Target identity and version resolution

For an existing app, identify the exact target before proposing or applying changes:

- repository or app root;
- entrypoint and affected pages/modules;
- deployment target when relevant;
- Python version when known;
- Streamlit version or version constraint from the project environment, lockfile, requirements, or supplied runtime output.

Prefer project-owned version evidence over assumptions about the latest Streamlit release. When exact API availability, signatures, deprecations, configuration keys, or deployment behavior matter and the project version is unknown, ask for or inspect version evidence before giving version-specific instructions. If current external documentation is available, use official Streamlit documentation and record the relevant version or documentation state. Do not silently mix APIs from different Streamlit generations.

For new apps without a pinned version, state the compatibility assumption and keep version-sensitive features isolated.

## Operation modes

Select exactly one primary mode before execution. Secondary concerns may be noted, but do not mix workflows unless needed.

| Mode | Primary goal | Default evidence |
|---|---|---|
| `build` | create or extend an app | source + focused tests/smoke plan |
| `debug` | explain and repair a defect | symptom + reproducer/log + regression check |
| `review` | assess an existing app | inspected files + rubric + findings |
| `test` | add or improve verification | target behavior + test surface + executed results |
| `deploy` | make the app runnable in a target environment | config + build/startup + smoke evidence |
| `optimize` | improve performance, rerun cost, or maintainability | baseline metric/trace + candidate metric/check |
| `migrate` | change Streamlit/Python/deployment versions or APIs | source version + target version + compatibility checks |
| `reference` | answer a focused API/config question | project version or official docs when version-sensitive |

Tie-breakers:

1. If a concrete failure is present, choose `debug` even when a refactor may be part of the fix.
2. If the user asks for release readiness, choose `review` unless they explicitly ask to implement fixes.
3. If the task changes versions or deprecated APIs, choose `migrate`.
4. If the request is purely factual and no artifact change is requested, choose `reference`.
5. Ask one focused question only when two modes would cause materially different actions or safety requirements.

## Evidence labels

Use these labels when reporting validation or review claims:

- `measured`: produced by an executed command, test, benchmark, or runtime check in the current task;
- `observed`: directly inspected source, config, output, screenshot, or log;
- `supplied`: provided by the user but not independently reproduced;
- `derived`: deterministic calculation from measured/observed evidence;
- `inferred`: reasoned from incomplete evidence and explicitly uncertain;
- `planned`: recommended but not executed;
- `blocked`: required evidence could not be obtained.

Never report `planned`, `supplied`, or `inferred` evidence as measured.

## Baseline and evaluator freeze

When a before/after comparison is required, the protected pre-change tests, fixtures, scenarios, acceptance criteria, and measurement method form the **frozen evaluator**.

For non-trivial edits to an existing app:

1. Capture the relevant before-state: changed files, current failing behavior, current tests, and version evidence.
2. Run the narrowest existing validation that represents current behavior before mutation when execution is available.
3. Treat existing tests, fixtures, expected outputs, and user-provided acceptance criteria as protected evaluator evidence. Do not weaken or rewrite them merely to make a candidate pass.
4. If an evaluator is wrong, separate that correction from the candidate fix, document why it is wrong, then restart the comparison from a new baseline.
5. When performance improvement is claimed, preserve the measurement method, input data, warm/cold cache state, and relevant environment between baseline and candidate runs.

Do not edit secrets, production credentials, generated golden evidence, or unrelated files to satisfy validation.

## Change and repair loop

Use this loop for implementation, debugging, optimization, and migration:

`baseline -> smallest causal change -> narrow check -> adjacent checks -> final check`

Repair ordering:

1. input/schema and version mismatch;
2. state/rerun and side-effect correctness;
3. cache/resource/session boundaries;
4. data/API integration correctness;
5. UI behavior and accessibility;
6. performance and deployment concerns;
7. cosmetic polish.

When one objective check keeps failing, change one causal control at a time. If two consecutive repair rounds do not reduce the same objective error set, stop that branch and report the unresolved diagnostic instead of random-searching.

## Validation matrix

Choose the smallest validation set that proves the requested change without overstating confidence.

| Change surface | Minimum useful validation |
|---|---|
| pure Python logic | focused unit test or deterministic example |
| Streamlit state/widget behavior | AppTest when supported; otherwise a precise manual interaction check |
| import/syntax change | `python -m compileall` or equivalent targeted compile |
| cache behavior | test keys/TTL/invalidation assumptions and cross-user isolation risk |
| side effects | explicit trigger + idempotency/retry check where the external operation supports it |
| authentication/authorization | logged-out/logged-in boundary checks plus server-side authorization evidence |
| deployment | build/startup command + target-environment smoke check |
| performance | same workload and measurement method before/after |
| visual layout | runtime/browser or screenshot review; AppTest alone is insufficient |

When repository-owned commands exist, prefer them over invented substitutes. Do not introduce a new dependency solely to claim stronger validation unless the user accepts that dependency.

## Final freeze and claims

**Freeze after pass.** After the final applicable validation passes, freeze the candidate. Any code/config change after that point invalidates the affected evidence and requires rerunning the relevant checks.

Keep evidence layers separate:

- structural: source/config/package shape is valid;
- behavioral: tests or scenarios demonstrate expected behavior;
- runtime: the app actually starts and behaves in a runtime/deployment environment;
- performance: comparable measurements demonstrate a delta;
- perceptual: visual/editorial quality was reviewed separately.

Use precise claims. Examples:

- "The package structure validates" does not mean the app runs.
- "AppTest passes" does not prove browser CSS layout or identity-provider redirects.
- "The app starts locally" does not prove the production deployment is healthy.
- "The code uses caching" does not prove a performance improvement without comparable measurements.


## Packaging integrity

For skill-package delivery, canonicalize output and receipt targets before writing. Reject any output alias with the source tree or sibling receipt. Stage validation, ZIP creation, hash calculation, and receipt creation before commit. Use atomic delivery where the filesystem permits it, preserve the last-good package if commit fails, and emit a complete durable receipt tied to the exact package SHA-256.
