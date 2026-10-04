# Security Threat Model

Use this reference for security issues in code, PRs, flows, infrastructure, logs, brokers, and reprocessing operations.

## Trust boundaries

Identify boundaries across:

- user/API/client to backend;
- backend to broker;
- broker to consumer;
- consumer to database/cache/storage;
- service to external API;
- logs/traces/DLQ/replay tools to operators;
- CI/CD/IaC to runtime infrastructure.

## Security invariants

- every privileged action is authorized at the component that performs it;
- event payload is context, not proof of authorization;
- tenant/resource ownership is revalidated before state-changing work;
- events do not carry tokens, passwords, private keys, session cookies, or avoidable sensitive personal data;
- duplicate/replayed/stale events cannot duplicate critical effects or regress terminal state;
- DLQs, logs, traces, test fixtures, and audit exports do not expose secrets or unnecessary sensitive data;
- reprocessing and redrive are authorized, auditable, and idempotent;
- broker, storage, and service permissions follow least privilege.

## Abuse cases

Test or reason about:

- tenant crossing: tenant id from one tenant with resource id from another;
- actor spoofing: event claims a privileged actor;
- payload escalation: role, status, approval, limit, bypass, or validation fields are altered;
- replay: old valid event is resent after state changed;
- stale terminal violation: event arrives after completed/cancelled/rejected state;
- injection: SQL, command, path, template, deserialization, log, and HTML/script injection payloads;
- data exfiltration: event, DLQ, log, trace, or notification carries sensitive data;
- subscriber confusion: unintended consumer receives sensitive or privileged event;
- operational bypass: manual redrive/replay bypasses normal controls.

## Secret and sensitive data handling

Treat as critical/high depending on blast radius:

- hardcoded credentials, client secrets, API keys, private keys, connection strings;
- auth headers, bearer tokens, cookies, JWTs, refresh tokens in logs or events;
- secrets in examples, tests, fixtures, Docker, Terraform, Kubernetes, CI/CD, screenshots, or comments;
- broad secrets in environment variables without managed secret store or workload identity where available.

When exposure is plausible, recommend rotation/revocation, log cleanup where feasible, blast-radius analysis, least-privilege tightening, and secret scanning.

## Security review output

For every issue include:

- asset and boundary;
- actor or abuse path;
- evidence;
- impact;
- smallest fix/control;
- validation or detection.

## Exceptional-condition lens

For privileged, stateful, transactional, or externally dependent paths, explicitly test or reason about abnormal conditions rather than only expected errors:

- authorization/authentication/risk dependency timeout or unavailable response;
- insufficient privilege or missing/extra parameter;
- partial transaction, partial side effect, cleanup failure, or rollback failure;
- resource exhaustion, quota exhaustion, memory/disk/connection pressure, retry exhaustion;
- repeated identical failures or attacker-induced error amplification;
- stale/contradictory state after an exception;
- fallback that weakens authorization, validation, durability, or confidentiality;
- fail-open versus fail-closed behavior;
- recovery, monitoring, alerting, and operator visibility.

A security-sensitive fallback must not silently convert uncertainty into authorization. For multi-step side effects, inspect whether every relevant state change can be rolled back or made safe through idempotent forward recovery.

## Upstream trust and API abuse

Treat service-to-external-API and partner-to-service responses as trust boundaries in both directions. Validate upstream data before it influences authorization, persistence, rendering, paths/commands, redirects/URLs, downstream requests, or expensive actions. Load `api-and-business-abuse.md` for API-specific authorization, resource/cost, business-flow, SSRF, inventory, and unsafe-consumption hypotheses.

## CAPEC as hypothesis input

CAPEC or another attack-pattern catalog may be used to generate abuse hypotheses and test cases after assets/trust boundaries are mapped. An attack pattern is not evidence that the target has the weakness; confirm or reject the hypothesis from target-specific evidence before creating a finding.
