# Premortem method

## Purpose and load condition

Use for `standard` and `governed` prospective plan reviews. The method owns selection, causal development, interventions, and plan change reconciliation, not project decisions or tests.

## 1. Establish a bounded scenario

The failure scenario is a *counterfactual* about a future project. Record a failure criterion tied to the user's actual objective (not "everything went wrong"), a reasonable horizon, planned dependencies, and stakeholders whose perspective may reveal contextual barriers. Never assert project properties absent from the supplied plan. If a horizon is unknown, use a non-date-specific future milestone such as "after launch" and label it as an assumption.

## 2. Diverge without anchoring

Before offering solutions or ranking causes, write distinct initiating mechanisms. In a team, collect silent independent submissions and then combine without allowing seniority or loudness to dominate. For an autonomous agent, perspective variation is a *prompting technique* only; do not fabricate human participation, independence, or dissent. Include internal execution, external dependencies, and contextual adoption only where causal relevance exists. Merge duplicates after ideation; do not reward quantity.

## 3. Build testable causal chains

Every retained risk should answer:

- **Initiating condition:** what must be true or occur?
- **Mechanism:** by what steps does it reach the failure?
- **Consequence:** which concrete objective or acceptance criterion fails?
- **Critical assumption:** what is inferred, unverified, or missing?
- **Controllability:** `internal`, `external`, or `shared`; this is a responsibility lens, not a blame assignment.
- **Discriminator:** what observation would confirm, weaken, or falsify this explanation?

Example (hypothetical): a consumer acknowledges an event before durable state transition -> process termination -> event cannot be retried -> a requested update is missing. Verification would inject failure after ACK under an authorized test plan. Do not report this as a tested defect.

Reject circular reasons ("the launch failed because implementation was bad"), mechanisms that do not affect the objective, and vague prevention ("monitor closely") without an observable signal and action.

## 4. Challenge the imagined story

For each prioritized chain, ask what contradicts it, whether the same outcome could arise by a simpler mechanism, and whether the team is overassigning blame to vendors, environment, or uncontrollable events. Deliberately seek at least one internal/changeable assumption across the analysis if applicable; report `none-evidenced` rather than fabricate one. Test whether reducing scope, delaying, cancelling, or a simpler approach is a genuine alternative. Do not *force* an opposite scenario if this only generates noise.

## 5. Decide what deserves attention

Qualitatively sort supported/uncertain material risks using consequence severity, causal credibility, controllability, detectability, and cost of prevention. Do not multiply ordinal categories, create pseudo-precise risk priority numbers, or convert qualitative confidence to calibrated percentage. Describe tradeoffs; a lower-probability, high-consequence risk may still justify testing when reversibility is low.

## 6. Close the prevention loop

For each prioritized risk, record:

1. **Prevention:** design/plan change that makes initiating conditions less likely or reduces impact.
2. **Detection:** measurable indicator, test, review, threshold or event that could reveal onset.
3. **Response:** who acts, what contingency or rollback may be needed, and the operational dependency.
4. **Validation:** test or evidence needed to establish that the control works. Untested safeguards remain proposed.
5. **Plan delta:** specific change with decision disposition and owner or `unknown`.

Avoid treating a mitigation brainstorm as a changed plan. `accepted` requires a supplied recorded owner decision, not the agent's recommendation. `complete` is permitted for a *completed analysis* with open actions, but never implies plan approved or project safe.

## 7. Governance and stopping

For `governed`, explicitly identify irreversible consequences, security/privacy/legal/safety exposures, domain-specific validation, evidence that blocks a decision, and authorized reviewers. The skill never self-approves release or waives policy. If evidence is insufficient for consequential acceptance, return `partial` or `blocked`; state the smallest next validation that could change it. If risk mitigation depends on significant project redesign, hand it back to the plan owner and the appropriate specialist.

The method is intentionally not a substitute for technical verification, reliability tests, threat modeling, incident RCA, or quantitative engineering risk analysis. Its value is exploratory and preparatory.
