# AI Impact Assessment

Use with `responsible-ai-review` when the system can materially affect people, access, rights, finances, employment, health/safety, privacy, reputation, essential services, or other consequential outcomes. Keep this evidence-based and domain-specific.

## Assessment record

Capture, when applicable:

- **system/use identity** — exact model/agent/workflow/version and intended use;
- **affected populations** — direct users plus people indirectly affected;
- **decision/action type** — recommendation, classification, generation, moderation, autonomous action, or human-decision support;
- **data context** — personal/sensitive data, proxies, retention, provenance, and purpose limits;
- **harm categories** — exclusion/denial, economic, privacy/surveillance, safety, reputational, accessibility, discriminatory/disparate impact, manipulation, legal/regulatory, or operational harm;
- **magnitude and reversibility** — scope, duration, recoverability, and who bears the cost of error;
- **human agency** — notice, explanation, consent where appropriate, contestability, override, and path to a human;
- **controls/mitigations** — thresholds, abstention, fallback, monitoring, access controls, redaction, testing, and operational containment;
- **validation evidence** — tests/metrics/reviews tied to the affected group and failure mode;
- **residual impact/risk owner** — what remains and who owns review/escalation.

Do not fabricate demographic impact metrics or fairness conclusions without data and a valid measurement design.

## Reassessment triggers

Define which changes invalidate or reopen the assessment. Typical triggers include:

- model/provider/version or material prompt/policy change;
- new tool/authority or autonomous action capability;
- new intended use, jurisdiction, population, or high-impact domain;
- new data source/sensitive attribute/proxy or retention change;
- material drift, incident, complaint pattern, disparate-impact signal, or safety event;
- control/approval/fallback removal or changed threshold;
- relevant regulatory/policy change.

A stale impact assessment is not current evidence. Record last assessment identity/date and the trigger that requires refresh when known.

## Output discipline

Map each finding to affected population -> evidence -> plausible harm -> mitigation -> validation -> residual impact. If domain/population/use evidence is missing and could change the conclusion, use `needs-verification` rather than a generic responsible-AI verdict.
