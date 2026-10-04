# Context Selection Evaluation

Use this reference when a context map, retriever, or future skill revision can be compared against a frozen gold/reference context. Do not use these metrics when relevance ground truth is unavailable.

## Purpose

Evaluate the upstream context-acquisition step independently from final code generation. A correct patch can hide poor context selection, while a good context set does not by itself prove a correct implementation.

## Required identities

Freeze or record:

- repository/base revision or supplied-file boundary;
- task/query identity;
- gold/reference relevant paths;
- available repository paths when unsupported-selection checks matter;
- token/byte budget when budget metrics are used;
- evaluator/fixture version and hash when results will be compared over time.

Never edit a frozen gold set after seeing candidate results merely to obtain a pass. If the oracle is wrong, invalidate the comparison and re-baseline it explicitly.

## Metrics

For positive-retrieval cases:

- **precision** = relevant selected / selected;
- **recall** = relevant selected / relevant expected;
- **F1** = harmonic mean of precision and recall;
- **unsupported-selection rate** = selected paths outside the declared available-path boundary / selected;
- **budget compliance** = selected cost <= declared budget;
- **budgeted yield** = recall multiplied by `min(1, budget / selected_cost)`; this package-local metric rewards recall within budget and penalizes overspending. It is not claimed to be numerically identical to external benchmark metrics with the same general name.

For `no-gold` cases, do not force precision/recall arithmetic to represent abstention quality. Evaluate **no-gold accuracy**: the case passes when the selected set is empty and the mapper explicitly reports `no-useful-local-context`/abstain.

## Fixture contract

`evals/context-selection-fixtures.json` contains deterministic package regression fixtures. They are synthetic calibration cases, not proof of real-repository retrieval performance.

Each case contains:

- `id`;
- `available_paths`;
- `expected_relevant`;
- `selected` entries with `path` and `cost`;
- `budget`;
- `abstain`;
- expected gates/metric thresholds.

Use `scripts/evaluate_context_selection.py` to execute the fixture or another compatible JSON file.

## Evidence layers

Keep claims separate:

- **structural evidence** — the map contract/resources/scripts exist and validate;
- **semantic-review evidence** — selected relations/requirements are judged appropriate;
- **behavioral evidence** — the mapper/retriever was actually run against frozen tasks and gold context;
- **runtime evidence** — repository/build/tool commands executed successfully in the target environment;
- **package-integrity evidence** — frozen hashes and package receipts match exact delivered bytes.

A passing synthetic fixture is deterministic structural/regression evidence. It is not measured behavioral improvement of an LLM or coding agent.
