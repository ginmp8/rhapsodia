# Verify / Diagnose — finite behavior comparison and counterexamples

**Purpose:** compare original and independently implemented candidate under frozen comparable stimuli, including bounded state and explicitly observed effects.
**Load when:** accepting a reconstruction, triaging differences, replaying trusted oracles, comparing HTTP results or reducing failure cases.
**Decision impact:** determines exact input equality, allowed observation exceptions, failure-class preservation, runner validity and defensible pass wording.

## Strict offline comparison

1. Freeze exact reference/candidate JSONL bytes, evaluator, baseline artifact and candidate identities, environment/reset policy and comparator options. Treat `runner_status` in manually supplied files as unauthenticated metadata.
2. Validate v1/v2 NDJSON unique IDs, strict JSON, typed data/action-step/effect shapes and runner status. Report any missing/unverified cases; never count timeout/errors as agreement simply because both sides failed.
3. Compare case IDs and **inputs exactly** with no ignore paths or numeric tolerance. Compare observation fields, error kind/code, ordered events/steps/effects, type differences and array ordering. `true` never equals `1`.
4. Optional `--numeric-absolute-tolerance` and `--ignore-pointer` work **only** on `/observation/...` and must have a documented nondeterminism rationale. Never blanket-normalize failures/time/identifiers. Diff records omit raw values but source corpora may still be sensitive.
5. Output matched/mismatched/missing-reference/missing-candidate/unverified counts, limited JSON-pointer findings, comparator options and `PASS_OBSERVED_CASES` or `DIVERGENCE_OR_INCOMPLETE`. `PASS_OBSERVED_CASES` means only matching **valid supplied finite** cases.

```sh
<PYTHON> scripts/behavior_lab.py compare reference.jsonl candidate.jsonl -o diff.json
<PYTHON> scripts/behavior_lab.py compare reference.jsonl candidate.jsonl --numeric-absolute-tolerance 0.001 --ignore-pointer /observation/clock -o diff.json
```

## Trusted program replay and optional file effects

`scripts/behavioral_pipeline.py` executes distinct user-approved trusted argv/cwd programs (one JSON stdin input to one JSON stdout observation per subprocess) only with `--execute-authorized`. Neither subprocess limits nor this flag confer consent or OS/network isolation. Use an independently assessed trusted environment, freeze actual executable/script/dependency identities and reset initial state between comparisons.

```sh
<PYTHON> scripts/behavioral_pipeline.py --cases cases.jsonl --reference-argv ref.json --candidate-argv cand.json --reference-cwd REF --candidate-cwd CAND --output-dir NEW_DIR --execute-authorized --shrink-trials 40
<PYTHON> scripts/behavioral_pipeline.py --cases cases.jsonl --reference-argv ref.json --candidate-argv cand.json --reference-cwd REF --candidate-cwd CAND --output-dir NEW_FS_DIR --execute-authorized --capture-fs
```

`--capture-fs` adds regular working-directory create/modify/delete hashes as explicit `file` effects, with bounded size/count and no symlink traversal. It does **not** see network/DB/outside-cwd/process effects and cannot be combined with `--shrink-trials`, since the runner does not reset effects. An `oracle_runner.py` standalone path supports the same `--capture-fs` observation.

## Diagnose / shrink without silently changing failure meaning

1. Confirm that the same valid divergence repeats on comparable reset states. Record first JSON pointer+`kind` signature.
2. Default `--shrink-trials N` tries deterministically bounded input simplifications on both oracles and retains candidates preserving the *first mismatch signature*. Cases that fail execution are not accepted as valid reduced mismatches.
3. `--shrink-allow-different-mismatch` explicitly relaxes the signature requirement, yielding a weaker reproducer. Neither mode proves global input minimality.
4. Add verified reduced inputs as separate regressions and rerun unchanged frozen reference/candidate corpora after implementation repairs. Never change golden values or test thresholds just to make a mismatch disappear.

## API/UI/state verification routes

`interface_traces.py replay` records client-observed HTTP status/body hash and optionally sanitized JSON; trust, reset and exact origin requirements apply. `web_investigator.py capture/explore` records bounded Playwright interactions, selected-text hashes, DOM/network metadata and optional screenshots; it is not a complete visual-diff oracle, and site code executes only under the explicit authorization gates. `state_inference.py offline|active|aalpy` preserves finite transition evidence; its missing transitions remain hypotheses. `probe_engine.py fuzz` is structured input generation, not self-contained coverage instrumentation. All runtime-specific missing tools, failures and partial views must remain visible in the verdict.
