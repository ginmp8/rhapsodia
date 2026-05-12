# Troubleshooting

## App reruns too often

Likely causes: widgets outside forms, expensive work at top level, callbacks changing state repeatedly, or missing cache boundaries.

Fix path: move grouped controls into a form, cache deterministic work, inspect session state, and isolate frequent refresh areas with fragments when appropriate.

## Widget resets or loses value

Likely causes: unstable widget key, changing options, conditional rendering, or reinitializing session state after widget creation.

Fix path: set stable keys, initialize state before rendering, preserve selected values when options change, and avoid replacing widget types under the same key.

## Duplicate widget key

Likely causes: repeated component without unique key or loop using non-unique labels.

Fix path: derive keys from stable IDs and component role.

## Cached data is stale

Likely causes: TTL absent or too long, missing cache parameter, mutable external data, or expecting cache to know about database changes.

Fix path: add TTL, include meaningful parameters, provide refresh button that clears cache, or move freshness logic to database queries.

## Cache does not hit

Likely causes: unhashable or changing arguments, function code changes, random/default values, or passing connection objects without underscore exclusion.

Fix path: stabilize parameters, exclude unhashable arguments with underscore, and separate resource creation from data computation.

## File upload fails

Likely causes: size limit, encoding, parser mismatch, invalid file, or app memory constraints.

Fix path: validate file size/type, show parser errors, stream/chunk large inputs, and document upload limits.

## Chart is slow

Likely causes: too many points, expensive chart construction, full data rendered instead of aggregate, or chart recomputed on every widget change.

Fix path: aggregate, sample, cache, and render only needed views.

## App works locally but not deployed

Likely causes: missing secrets, dependency mismatch, file path assumptions, unavailable local resources, network restrictions, or platform config differences.

Fix path: inspect deployment logs, verify secrets, pin dependencies, remove local-only paths, and add startup diagnostics that do not expose secrets.

## Authentication surprises

Likely causes: redirect URI mismatch, missing provider config, cookie/session settings, or displaying private data before login check.

Fix path: gate private content at the top of the page and verify identity provider settings in deployment.

## Debugging protocol

1. Capture the exact symptom and triggering action.
2. Identify whether it is rerun/state, data, UI, external I/O, deployment, or auth.
3. Reproduce with minimal code.
4. Add visible diagnostics temporarily.
5. Patch the smallest boundary.
6. Add AppTest or a manual regression check.
