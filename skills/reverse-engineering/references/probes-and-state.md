# Adaptive probes, structural fuzzing and state inference

**Purpose:** discover high-information unknown behaviors without treating guessed outputs as ground truth.
**Load when:** source has missing edge/negative/boundary coverage, original-vs-candidate divergences, stateful protocols, or a trusted observable oracle.
**Decision impact:** chooses input generation, feedback priority, state observation class, query budget, reset requirements and reproducible stopping conditions.

## Input-only probe/fuzz generation

```sh
<PYTHON> scripts/probe_engine.py generate --reference reference.jsonl --comparison differential.json --max-cases 100 --seed 7 -o probes.jsonl
<PYTHON> scripts/probe_engine.py fuzz --reference reference.jsonl --coverage coverage.json --max-cases 100 --seed 7 -o fuzz-hypotheses.jsonl
<PYTHON> scripts/probe_engine.py generate --openapi declared-openapi.json --max-cases 50 -o api-probes.jsonl
```

Generates bounded input mutations: omitted/null keys, primitive/numeric/Unicode boundaries, empty/duplicated/reordered lists, repeated/reordered/missing state actions and compositions of mutations. Corpus inputs are never re-emitted as novel. `--comparison` prioritizes cases with prior differential mismatches. Optional externally recorded coverage JSON `{ "by_case": { "id": ["observed_edge_A", "observed_edge_B"] } }` prioritizes cases with rare covered identifiers; the skill does **not** instrument the target or fabricate coverage. `--seed` pins deterministic fuzz ordering. All generated JSONL rows have `status:"unobserved"` and deliberately omit `observation`; validate on original before using as golden-master tests. Seeds and feedback are supplied data: they may contain private values and inferred domain-inappropriate mutations.

## Finite state inference

```sh
<PYTHON> scripts/state_inference.py offline --corpus reference.jsonl --alphabet actions.json -o states.json
<PYTHON> scripts/state_inference.py active --alphabet actions.json --argv-file approved-command.json --cwd TRUSTED_DIR --reset-confirmed --execute-authorized --depth 2 --max-queries 50 --capture-corpus observed-active.jsonl -o observed-states.json
```

`actions.json` is an array of action objects. Observations must use V2 `input.actions` aligned with `observation.steps`; each step can include explicit `state`, `output`, `error`, `status`, `events`, `effects`. The inference builds a **finite observed transition graph**, preserves conflicting observations and proposes missing transitions. Explicit equal state values can merge nodes; absent state values produce separate prefix nodes, **never silently inferred equal**. Output/effect values are hashed in the graph, not emitted raw. Active mode exhaustively enumerates bounded action sequences over a trusted resettable one-shot oracle and stores real captured cases; `--reset-confirmed` is an operator assertion, not an OS-enforced reset.

## Optional AALpy L* Mealy inference

```sh
<PYTHON> scripts/state_inference.py aalpy --alphabet actions.json --argv-file approved-command.json --cwd TRUSTED_DIR --reset-confirmed --execute-authorized --max-queries 100 --seed 7 -o inferred-mealy.json
```

AALpy, if independently installed, uses the same trusted one-shot oracle through membership queries; `step` replays full prefixes, so the oracle must reset deterministically for **every** query. L* with bounded random-walk equivalence queries yields a hypothesis, **not proof of minimality/equivalence**. Without AALpy, `offline` and bounded `active` modes work using stdlib only. Exhausted query budgets fail clearly; no oracle code is executed without explicit approval. Version compatibility of AALpy must be tested on the actual host before a runtime claim.

## Closure

Freeze reference observations before candidate implementation. Every probe/result has case identity, seed or command hash and status. Replay positive, negative, stateful, duplicate/retry and side-effect cases when supported. Preserve counterexample first pointer/kind in the trusted pipeline; input reduction does not prove globally minimal causes. Do not normalize away failures or overwrite protected fixture expectations.
