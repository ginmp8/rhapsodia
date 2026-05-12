# Frontend leak prevention and browser-side security

Use this reference for frontend security reviews focused on data exposure, browser storage, logs, analytics, XSS risk, CSP posture, source maps, cache behavior, and authorization boundaries.

## Security boundary

The frontend is not a trusted security boundary. It can improve user experience and reduce accidental exposure, but real authorization and sensitive operations must be enforced by backend or trusted server-side systems.

## Never allow

- Secrets, client secrets, service tokens, private keys, passwords, or signing keys in frontend code.
- Secret-like values in public environment variables such as `VITE_*` or `NEXT_PUBLIC_*`.
- Sensitive auth/session/refresh tokens in `localStorage` or `sessionStorage`.
- Raw personal, financial, authentication, or document payloads in console logs, analytics, error trackers, URLs, or third-party scripts.
- Frontend-only authorization checks for protected operations.
- Unsafe HTML rendering without sanitizer and explicit approval.

## Environment variables

Public frontend environment variables are bundled or exposed to the browser. Treat them as public configuration.

Allowed examples:

```txt
VITE_APP_ENV=production
VITE_PUBLIC_API_BASE_URL=https://api.example.com
NEXT_PUBLIC_ANALYTICS_WRITE_KEY=<public client key if approved>
```

Blocked examples:

```txt
VITE_CLIENT_SECRET=...
NEXT_PUBLIC_SERVICE_TOKEN=...
VITE_PRIVATE_KEY=...
NEXT_PUBLIC_PASSWORD=...
```

If a browser needs to call a third-party service that requires a secret, route the request through a backend or BFF.

## Token and storage rules

Prefer secure, httpOnly, sameSite cookies for sensitive session material when the architecture supports it. If tokens must be held in browser memory, keep lifetime short and document the trade-off.

Avoid:

- refresh tokens in web storage;
- long-lived access tokens in web storage;
- storing raw identity documents, financial data, or sensitive onboarding payloads client-side;
- persisting drafts with sensitive fields without product/security approval.

## Logs, analytics, and error tracking

Use allowlists, not blocklists, for analytics payloads.

Do not send:

- passwords, tokens, session IDs, cookies, authorization headers;
- raw documents or images;
- personal identifiers unless explicitly approved;
- full API request or response bodies;
- form values from sensitive flows;
- stack traces containing sensitive route/query data.

Recommended wrapper pattern:

```txt
shared/observability/analytics.ts
shared/observability/logger.ts
shared/observability/redaction.ts
```

Centralize event names and payload schemas so sensitive fields can be rejected before shipping.

## URL and cache exposure

Review whether sensitive values appear in:

- query strings;
- route params;
- redirect URLs;
- browser history;
- referrer headers;
- cache keys;
- screenshots or downloadable reports.

Prefer opaque IDs or server-side state for sensitive flows. Configure cache behavior deliberately for pages that display sensitive data.

## XSS and unsafe HTML

High-risk patterns:

- `dangerouslySetInnerHTML`;
- rendering markdown or rich text from untrusted sources;
- manually concatenating HTML strings;
- unsafe URL schemes such as `javascript:`;
- third-party widgets with broad script access.

Required controls:

- sanitizer with documented configuration;
- content source allowlist;
- CSP review;
- tests or runtime validation for known malicious samples when feasible.

## CSP, third-party scripts, and source maps

Check production posture:

- CSP exists and avoids unnecessary `unsafe-inline` or broad wildcard sources;
- third-party scripts are justified and reviewed;
- source maps do not expose sensitive code comments, internal routes, or secrets;
- error reporting does not include sensitive payloads;
- dependency additions are justified by feature value.

## Authorization and permission UX

Frontend permission checks are useful for hiding controls, explaining access, and reducing dead ends. They are not real enforcement.

A safe answer should state:

- backend must enforce authorization;
- frontend can mirror permissions only for UX;
- protected API calls must fail safely if the frontend is bypassed;
- permission-denied states should be explicit and accessible.

## Security review output

Report:

1. reviewed scope and data sensitivity;
2. findings by severity;
3. smallest safe fix;
4. required backend or policy dependency;
5. validation executed and recommended;
6. unverified risks.
