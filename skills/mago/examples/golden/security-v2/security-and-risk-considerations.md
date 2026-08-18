# Security and Risk Considerations

- Contract version: 2

## Scope

- Spec: `spec-2026-07-20-filtered-export`
- Security domains: authorization, sensitive_data
- In-scope components and consumers: export API and export worker

## Assets and Data Classification

### ASSET-001 - Exported customer data

- Classification: restricted
- Sensitive data or secrets: customer identifiers and financial attributes
- Retention and logging constraints: values must not be logged; generated files follow restricted-data retention

## Trust Boundaries

### BOUNDARY-001 - API to export worker

- Source: authenticated export API
- Destination: export worker
- Authentication: workload identity
- Authorization: API policy and worker-side column allowlist

## Threats

### THREAT-001 - Restricted column disclosure

- Assets: ASSET-001
- Trust boundaries: BOUNDARY-001
- Threat actor: unauthorized internal caller
- Likelihood: medium
- Impact: high
- Security domains: authorization, sensitive_data

## Misuse and Abuse Cases

### ABUSE-001 - Request restricted columns

- Threats: THREAT-001
- Observable misuse: caller submits restricted or unknown column identifiers
- Expected prevention or detection: reject the request and record only safe metadata

## Planned Controls

### CONTROL-001 - Server-side column allowlist

- Threats: THREAT-001
- Abuse cases: ABUSE-001
- Owner: export service owner
- Validation: SECVAL-001
- Failure behavior: deny

## Risks and Residual Risk

### RISK-001 - Allowlist configuration drift

- Threats: THREAT-001
- Controls: CONTROL-001
- Residual likelihood: low
- Residual impact: high
- Risk authority: application security
- Status: review_required
- Acceptance evidence: none while review is pending

## Validation Expectations for Magia

### SECVAL-001 - Restricted-column negative tests

- Controls: CONTROL-001
- Threats: THREAT-001
- Test type: negative
- Expected evidence: contract tests proving restricted and unknown columns are rejected
- Sensitive logging check: verify customer values and requested restricted values are absent from logs

## Required Review

- Security reviewer: application security
- Compliance reviewer: data governance
- Review evidence required before handoff closure: linked review record or unresolved blocker
