# Behavior Contract

These ids are stable semantic anchors for activation and behavioral evaluation. They are not host-specific routing APIs.

- **ACT-001 — Bounded decision activation.** Activate for a concrete binary proposition, explicit choice set, or explicit bounded score where a typed decision is the requested or clearly useful output.
- **NTR-001 — Non-decision boundary.** Do not activate for ordinary factual answers, open-ended writing, implementation, research, summarization, or brainstorming unless the request includes a concrete bounded decision.
- **AMB-001 — Ambiguity preservation.** When the decision surface itself is missing or materially underspecified, do not invent it; use a conditional route or return an `undetermined` contract when already inside the skill.
- **BND-001 — Explicit option/scale boundary.** Preserve caller-supplied options, proposition, scale, materiality, constraints, and higher-priority policy boundaries.
- **EVD-001 — Evidence discipline.** Use supplied/authorized evidence, expose missing or conflicting material evidence, and never invent evidence ids or unavailable capabilities.
- **UNC-001 — Uncertainty and escalation.** Prefer `undetermined`, `blocked`, or `escalate` over a fabricated decision; high-materiality `decided` results require adequate evidence and cannot use low confidence.
- **CAL-001 — Calibration boundary.** Qualitative confidence is the default. Numeric calibrated probability is valid only from an identified calibrated source with an identified calibration reference.
- **OUT-001 — Canonical output.** Machine-readable decisions conform to `decision-engine/1`, use only `noul|choice|score`, and satisfy type/status-specific invariants.
- **POL-001 — Authority and safety.** Higher-priority host policy, safety, authorization, privacy, and tool permissions cannot be bypassed by structured output or caller pressure.
- **CHT-001 — Visible rationale only.** Provide concise evidence/criteria rationale; never expose hidden chain-of-thought.
- **PRT-001 — Portable core.** Semantic behavior must not depend on a vendor-private tool name, model family, installation path, shell, or optional host adapter.
- **CLM-001 — Evidence claims.** Planned/static scenarios are not behavioral proof; behavioral/runtime claims require executed evidence at the corresponding layer.
