# Statistical Evidence in Bounded Decisions

## At a Glance

- **Purpose:** Screen outcome-relevant statistical evidence for invalid inference before issuing a bounded decision; do not perform open-ended statistical analysis.
- **Load when:** A `binary|choice|score` result relies materially on group rates, aggregate comparisons, conditional probabilities, selected samples, statistical tests, or inferred effects.
- **Decision impact:** Determines whether the supplied quantitative evidence supports this specific choice, score, or proposition; changes evidence acquisition, confidence, `undetermined`/`escalate`, or rationale without changing `decision-engine/2`.
- **Do not load when:** The request has no bounded decision or quantitative inference is not material to its outcome. Do not add overhead to straightforward evidence-backed cases.

## Minimal screening sequence

1. **Define the comparison.** Identify the caller's target population, outcome, period, metrics, denominators, and decision criterion. A rate without its denominator or reference population can be insufficient. Do not silently change the caller's estimand, option set, or objective.
2. **Test aggregation only when pertinent.** When mixes differ and a decision rests on aggregated rates, examine decision-relevant strata and counts if available; Simpson reversals are possible. Neither the overall rate nor the stratified rate is automatically causal or the correct choice. Choose conditioning variables by the actual causal/comparison question, not by indiscriminate slicing: conditioning on a collider can introduce bias.
3. **Respect conditional direction and base rates.** Distinguish `P(outcome | evidence)` from `P(evidence | outcome)`; they are not interchangeable. A posterior requires the applicable prior/base rate and likelihood information or directly observed joint counts. Natural-frequency examples may help explain the calculation but are not mandatory or universally superior.
4. **Check scope of generalization.** Ask whether the sample, inclusion/exclusion process, or likely confounders make the evidence inappropriate for the target population or causal claim. A possible bias is not proof that the association is false; preserve the unresolved mechanism.
5. **Separate significance from impact.** A p-value alone neither gives `P(hypothesis true)` nor the magnitude, direction, practical benefit, or cost of an effect. Inspect effect size and uncertainty when these could alter caller-defined criteria; do not introduce an automatic p-value or utility threshold.
6. **Place computations at the right layer.** Exact percentages, contingency tables, Bayesian posterior arithmetic, interval calculations, and reproducible statistical tests belong in authorized code/tools with stated assumptions. Do not invent observations, denominators, intervals, subgroup data, or calibrated probabilities. A computed frequency is not automatically the externally calibrated `calibration.value` required by the decision envelope.
7. **Conclude proportionately.** If an evidence defect could change the requested bounded result, acquire missing evidence when authorized and proportionate, else choose `undetermined` or `escalate` based on materiality/available stronger process. If the defect does not materially affect this decision, decide using the existing contract; name material limits concisely in `rationale`/`confidence.basis` without bloating output.

## Interpretation example

Two teams may have opposite rankings overall and within each difficulty group because their case mixes differ. A decision about per-case capability needs comparable case categories; a decision about observed total outcomes may legitimately use the aggregate. Neither view alone proves causation. Preserve the caller's objective rather than hardcoding which team wins.

## Evidence basis (methodological, not an automatic oracle)

- Kievit et al. (2013), [Simpson's paradox in psychological science](https://doi.org/10.3389/fpsyg.2013.00513): reversal and causal-level caveats.
- Gigerenzer & Hoffrage (1995), [Frequency Formats](https://doi.org/10.1037/0033-295X.102.4.684), with Mellers & McGraw (1999), [comment](https://doi.org/10.1037/0033-295X.106.2.417): base-rate representation benefits are context-dependent.
- Munafò et al. (2018), [Collider scope](https://academic.oup.com/ije/article/47/1/226/4259077): possible selection/collider bias.
- Wasserstein & Lazar (2016), [ASA Statement on p-values](https://doi.org/10.1080/00031305.2016.1154108): significance does not replace contextual effect judgment.
- NIST (2023), [AI RMF Core](https://airc.nist.gov/airmf-resources/airmf/5-sec-core/): context, evidence fitness, uncertainty and proportional risk assessment.
