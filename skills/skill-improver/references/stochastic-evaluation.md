# Stochastic Evaluation

Use only for strong claims about stochastic agent/model reliability or behavioral improvement. A single run can still support a local observation, but not a repeated-reliability claim.

## Trial contract

- predeclare the number of trials per case;
- keep task/evaluator and material runtime identity equivalent across paired arms;
- preserve raw per-trial outcomes;
- prefer paired `no-skill`, `parent`, and `candidate` trials for marginal-value claims;
- report failures and ties, not only averages.

For binary success, `pass@k` measures at least one success in `k` attempts while `pass^k` measures all `k` attempts succeeding. Choose the statistic from the reliability claim before seeing candidate results.

`assets/templates/paired-trials.json.template` is the portable evidence shape. `assets/schemas/stochastic-evaluation.schema.json` documents the structural contract. Validate with `scripts/validate_execution_evidence.py --kind stochastic`; summarize with `scripts/summarize_paired_trials.py`.

## Claim limits

Derived probabilities assume a repeatable trial-generating process and can be misleading when trials are correlated. Report the assumption. A better mean or sign-test diagnostic does not waive activation, safety, compatibility, promotion-holdout, contamination, capability-delta, or package gates.
