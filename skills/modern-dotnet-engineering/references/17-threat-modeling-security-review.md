# Threat Modeling and Security Review

## Lightweight threat model

Use this for features touching identity, money, account creation, partner access, admin operations, file upload, external callbacks, or personal data.

## Structure

1. Assets: what must be protected.
2. Actors: users, services, partners, admins, attackers.
3. Trust boundaries: API, queue, database, third-party service, browser/client.
4. Abuse cases: what can go wrong.
5. Controls: auth, validation, idempotency, rate limit, audit, encryption, monitoring.
6. Residual risk and validation probes.

## Finding classification

For security findings, classify evidence as confirmed risk, potential risk, or evidence limitation. Do not claim a vulnerability without evidence.
