# Stochastic Evaluation Profile

Use when a claim depends on repeatability across stochastic executions: model/agent behavior, model judges, retries, or other probabilistic paths. One run can prove a failure but normally cannot prove reliable improvement.

Validate `assets/schemas/stochastic-evaluation.schema.json` with:

```text
<PYTHON> scripts/validate_reproducibility_profiles.py --kind stochastic --input <TRIALS.json>
```

Predeclare the stop rule and maximum trial budget. Keep scenario/input/evaluator identities fixed for paired arms and isolate mutable trial state when independence matters. Report raw outcomes, empirical success rate, Wilson 95% interval, requested `pass_power[k] = p^k`, and limitations; `pass_power` is an independence-model estimate, not proof of independence.

For LLM judges, record judge identity and calibration status. A strong promotion claim cannot rely on an uncalibrated LLM judge and requires independent replication. Keep ties/unknown outcomes explicit instead of forcing a winner.

Use repeated-trial evidence to quantify reliability, not to let Harness choose survivors or champions; selection remains with the caller/search controller.
