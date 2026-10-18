# Statistical interpretation in skill benchmarks

## At a glance

- **Purpose:** Keep trial-based comparison claims calibrated to sample composition, denominators, effect size and uncertainty.
- **Load when:** Comparing skill runs/versions, using pass rates, inferential intervals, subgroup scores or multiple chosen endpoints in a benchmark verdict.
- **Decision impact:** A candidate's apparent superiority may be a mix/selection artifact, exploratory multiple-testing win or statistically/operationally inconclusive delta.

## Contents

- [Population and denominators](#population-and-denominators)
- [Effect and uncertainty](#effect-and-uncertainty)
- [Multiplicity and selection](#multiplicity-and-selection)
- [Example and contract preservation](#example-and-contract-preservation)
- [Sources](#sources)

## Population and denominators

Record task/scenario ids, pass/fail/missing definition, valid trial count, suite role and distribution profile for each arm. Pair comparable tasks and trials before aggregating. Balanced diagnostic sets are not production prevalence. If arm populations or sample composition differ, pooled success rates and strict deltas are `not-comparable`; do not reinterpret subgroup reversal (Simpson's paradox) as skill superiority. Show per-group values when they could change the verdict.

## Effect and uncertainty

Report paired delta, declared practical-effect threshold, applicable uncertainty estimate and assumptions. A confidence interval should not be described as posterior probability of an observed fixed effect. Do not equate `p < 0.05` with practical value or a null-crossing interval with proof of no effect. Respect the existing v2/v3 claim classifications and hard-gate precedence; statistical uncertainty cannot override a failed safety/contract gate.

## Multiplicity and selection

Declare which metrics, cohorts, candidates and comparisons were committed before candidate evaluation versus selected after observing outcomes. Many unplanned tests/subgroups increase cherry-picking risk; use a method consistent with predeclared error control when justified, otherwise mark findings exploratory. Never invent adjusted p-values, bootstrap intervals, prevalence or weights. LLM evaluator stochasticity and evaluator contamination require independent controls, not merely statistical corrections.

## Example and contract preservation

If benchmark A runs 8/10 tasks against B's 7/10 but their ten scenarios are composed differently, do not conclude A is better; first compare identical frozen task identities or report separate descriptive results. The example is synthetic.

This reference is conditional guidance, not a new benchmark metric, scoring weight, schema or validator. Existing `benchmark` report schemas, paired bootstrap contract, frozen evaluator, protected tests, candidate comparison and read-only ownership remain authoritative.

## Sources

- Simpson (1951), https://doi.org/10.1111/j.2517-6161.1951.tb00088.x
- Kievit et al. (2013), https://doi.org/10.3389/fpsyg.2013.00513
- ASA statement (2016), https://doi.org/10.1080/00031305.2016.1154108
- NIST confidence intervals, https://www.itl.nist.gov/div898/handbook/prc/section1/prc14.htm
- Benjamini and Hochberg (1995), https://doi.org/10.1111/j.2517-6161.1995.tb02031.x
