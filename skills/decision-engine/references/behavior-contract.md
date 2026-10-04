# Behavior Contract

These ids are stable semantic anchors for activation and behavioral evaluation. They are not host-specific routing APIs.

- **ACT-001 — Bounded decision activation.** Activate for a concrete binary proposition, explicit choice set, or explicit bounded score where a typed decision is the requested or clearly useful output.
- **NTR-001 — Non-decision boundary.** Do not activate for ordinary factual answers, open-ended writing, implementation, research, summarization, or brainstorming unless the request includes a concrete bounded decision.
- **AMB-001 — Ambiguity preservation.** When the decision surface itself is missing or materially underspecified, do not invent it; use a conditional route or return an `undetermined` contract when already inside the skill.
- **BND-001 — Explicit decision boundary.** Preserve caller-supplied proposition, options, option-set exhaustiveness, option criteria, score scale, materiality, constraints, tie-breakers, and higher-priority policy boundaries.
- **EVD-001 — Evidence discipline.** Use supplied/authorized evidence, expose missing or conflicting material evidence, and never invent evidence ids or unavailable capabilities.
- **UNC-001 — Uncertainty and escalation.** Prefer `undetermined`, `blocked`, or `escalate` over a fabricated decision; non-decided results use `confidence: null`; high-materiality decided results require adequate direct evidence and cannot use low confidence.
- **SEL-001 — Selective decision quality.** Non-decided outcomes are legitimate selective outputs. Evaluation must distinguish trustworthy abstention/escalation from unnecessary abstention and unsafe forced decisions.
- **CAL-001 — Calibration boundary.** Qualitative confidence is the default for decided results. Numeric calibrated probability is valid only from an identified calibrated external source with an identified calibration reference.
- **ACTN-001 — Action-policy separation.** A semantic decision does not itself authorize an operational action. Caller/policy-owned thresholds, weights, approvals, and action rules remain external unless explicitly supplied as constraints/evidence.
- **INV-001 — Decision invariance.** Semantically equivalent inputs should preserve the same bounded decision under irrelevant ordering or formatting changes; Choice option position must not determine the winner.
- **OUT-001 — Canonical output.** Machine-readable decisions conform to `decision-engine/2`, use only `binary|choice|score`, and satisfy type/status-specific invariants.
- **POL-001 — Authority and safety.** Higher-priority host policy, safety, authorization, privacy, and tool permissions cannot be bypassed by structured output or caller pressure.
- **CHT-001 — Visible rationale only.** Provide concise evidence/criteria rationale; never expose hidden chain-of-thought.
- **PRT-001 — Portable core.** Semantic behavior must not depend on a vendor-private tool name, model family, installation path, shell, or optional host adapter.
- **CLM-001 — Evidence claims.** Planned/static scenarios are not behavioral proof; strong stability or improvement claims require executed comparable evidence, repeated trials when stochastic variation is material, and frozen/equivalent evaluator identity.
