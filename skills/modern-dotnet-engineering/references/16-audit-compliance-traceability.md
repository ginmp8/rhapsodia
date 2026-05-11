# Audit, Compliance, and Traceability

## When audit is required

Use audit trails for regulated, financial, identity, onboarding, access, approval, rejection, risk, consent, and data-change flows.

## Minimum audit fields

- who initiated the action;
- who approved/operated when different;
- when it happened;
- system/channel/originator;
- target entity;
- before/after meaningful state or reason code;
- correlation id/trace id;
- source IP/device only if policy allows and requires it.

## Rules

- Audit records must be append-oriented and tamper-resistant according to risk.
- Logs are not sufficient for audit.
- Do not store excessive PII in audit details.
- Make retention and access rules explicit.
