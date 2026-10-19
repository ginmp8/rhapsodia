# Selective Decision Policy

## At a Glance

- **Purpose:** Apply selective answering, deferral, and escalation to bounded `decision-engine/2` decisions without changing its schema or inventing accuracy guarantees.
- **Load when:** The caller requests a decision gate with abstention/review rules, numerical acceptance thresholds, or measured risk-versus-coverage reporting.
- **Decision impact:** Selects only among existing status semantics, requires evaluation of accepted and rejected cases, and invalidates unsupported model-confidence or distribution-shift claims.
- **Do not load when:** A normal bounded low-risk decision has adequate evidence and no selective policy; do not add unnecessary abstention.

## Selection and authority

1. Apply policy/authorization first. A forbidden action, missing permission, or unavailable mandatory tool yields `blocked` with `next_action` if required; uncertainty does not override policy.
2. Decide when the bounded question, evidence, and constraints support it; retain the existing `decided` value and qualitative confidence rules.
3. Use `undetermined` when missing/contradictory evidence or non-exhaustive options prevent a justified decision but no designated reviewer is required.
4. Use `escalate` only when the declared policy requires a stronger evaluator, independent verification, or a qualified human/specialist; name a feasible `next_action` and do not imply it has occurred.
5. Do not substitute `blocked`, `undetermined`, and `escalate` for one another to optimize reported answered-case accuracy. None grants execution permission.

## Selective risk and coverage

When representative labeled cases and a **predeclared** acceptance policy exist, distinguish:

- `coverage = decided / eligible` for in-scope eligible decisions; state inclusion/exclusion, treatment of blocked cases, and denominator.
- `selective_error = wrong_decided / decided`; if `decided = 0`, report undefined, not 0% error.
- `false_abstention = eligible_answerable_not_decided / eligible_answerable`, when answerability labels are available. An abstained sample is not automatically wrong or safe.
- Review burden, review latency, deferral success, and per-subgroup error/coverage when harms or distribution vary.

A lower selective error achieved by rejecting almost everything is not an unconditional quality improvement. Compare risk-coverage curves or declared operating points and costs. Do not fit/select thresholds on the same cases later reported as untouched test performance. Maintain separate calibration/selection and evaluation sets when a measured policy claim is requested.

## Calibration and deployment limits

- `calibrated_probability` remains permitted only for an identified external calibrated source with `calibration_ref`, declared event meaning, model/version, evaluation population and validity conditions. Free-form LLM confidence is not that source.
- Calibration and selective prediction are distinct. Good marginal calibration does not automatically imply strong error ranking, selective risk control, subgroup fairness, or safe downstream actions.
- A published statistical bound applies only under its assumptions, sampling process, confidence level, data and model identity. Never transpose research guarantees to an unevaluated LLM agent.
- Under distribution shift, changed tools/models/tasks, insufficient labels or stale evaluator identity, invalidate numerical operating claims; use the existing qualitative status and report what requires recalibration or expert review.
- Evaluate over-refusal and benign-case utility; policy-driven refusal and missing permission are not prediction errors, but remain visible in overall workflow metrics.

## Operational output

Preserve `decision-engine/2` exactly. No new required fields, probabilities, thresholds, statuses or authority are introduced. In `rationale`, record only applicable criteria, evidence gaps, policy selection reason, and denominator/provenance of externally supplied numeric claims; report larger risk-coverage evidence separately, not as a fabricated per-case confidence.

## Research basis

- Geifman & El-Yaniv (2017), selective risk/coverage: https://papers.neurips.cc/paper_files/paper/2017/hash/4a8423d5e91fda00bb7e46540e2b0cf1-Abstract.html
- Guo et al. (2017), confidence calibration: https://proceedings.mlr.press/v70/guo17a.html
- Wen et al. (2025), LLM abstention: https://aclanthology.org/2025.tacl-1.26/
- Sullutrone et al. (2025), over-refusal: https://aclanthology.org/2025.findings-acl.1243/
