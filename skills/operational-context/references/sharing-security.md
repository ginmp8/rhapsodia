# Explicit sharing and cooperative coordination

## Trust boundary

The core works within one authorized local workspace/user account, not an authenticated
multi-tenant service. Filesystem permissions are necessary. A hash proves matching bytes,
not identity, authorization or absence of prompt injection. Metadata is always source data.
No network, remote fetch, secret discovery, automatic promotion or global memory exists.

All writes are explicit local cache publications. Immutable objects have content hashes;
publication uses atomic replacement and a short exclusive cooperative lock with nonce.
Busy locks are not stolen. Mutable lease state is checked under the same lock. An attacker
with authority to rewrite both source and local metadata is outside this integrity model.
Symlink/private-path checks reduce accidental exposure but do not claim an OS sandbox or
protection against a hostile same-user process racing every filesystem operation.

## Cross-workspace pointer exchange

`federation-export` requires `kind`, 1..64 exact `ids`, `approved:true` and optional budget.
Only current references are exported. Payload: source scope hash, object IDs, content hashes,
expiry (one hour), and untrusted-reference-only marker. No path, label, owner, body or status
is exported. Content fingerprints can still correlate confidential material: approval matters.

`federation-import` requires the exact exchange, `approved:true`, and `allowed_source_scope`.
Content hash, scope, finite expiry and record shapes are validated. Imported pointers stay
quarantined in a separate kind; they never satisfy local evidence/action lookups. No remote
source is contacted. An authorized owner must separately identify and verify matching local
sources before indexing them. This is not automatic cross-project knowledge federation.

## Cooperative leases

`lease` takes operation (acquire/renew/release/check), resource (exact shared logical ID),
holder, optional ttl_seconds (1..300), token and generation. Acquire returns an unguessable
nonce and generation. Renew/release/check require the matching holder/token/generation;
expired or superseded holders cannot renew. A new acquisition increments generation.

These are advisory work-unit leases, not native file locks or an authorization service.
All workers must agree on the same canonical resource ID and validate the lease immediately
before their own permitted write. Aliased/overlapping paths are not automatically detected;
canonical single-writer policy remains mandatory, including after expiry. Never infer that
an expired lease proves its previous worker has stopped executing.

## Optional graph projection

`graph-export` requires kind and at most 64 exact IDs; candidate links are bounded to 2048.
It produces `graph-patch-v1` with source identity, observed membership and content-reference
edges. Source paths are excluded. EXTRACTED/accepted evidence labels refer to index membership,
not acceptance of tests or approval. No dependencies are inferred and no graph database or
viewer is launched. Local Graph v3 can ingest the projection under its own validation rules.

Stop if bounds, trust, expiry, source scope, hashes or permissions cannot be established.
Remove disposable caches only after active writers stop; never mutate canonical evidence.
