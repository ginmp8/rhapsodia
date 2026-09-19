# Evidence and Source Integrity

Use this reference whenever review conclusions depend on file identity, dependency identity, external advisories, scanner results, or protected material.

## Evidence snapshot

Before substantive analysis of a filesystem target, prefer a deterministic receipt:

```text
<PYTHON> scripts/evidence_snapshot.py --target <TARGET_PATH> --output <WORK>/evidence-receipt.json
```

The receipt records relative paths, hashes for safe sources, dependency-source roles, protected states, and a stable tree identity. It intentionally omits timestamps so equivalent source bytes produce equivalent receipts.

## Protected evidence

Treat these as protected from mutation by default:

- credentials and secret stores;
- `.env` files;
- private keys/certificates carrying private material;
- fixtures/golden inputs;
- expected outputs;
- frozen evaluator evidence;
- generated baseline evidence.

For secret-bearing paths, prefer `protected-unread`: record presence/metadata only. For fixtures/expected outputs, `protected-hash-only` is allowed when identity is needed; never print their content merely to prove identity. Never follow symlinks into protected/out-of-scope locations.

## Dependency/source identity

A dependency finding should bind evidence to the exact manifest/lockfile/package/version available. External evidence should record enough source identity to distinguish current scanner/advisory data from model memory. If source freshness or applicability cannot be verified, classify the claim `needs-verification`.

## Evidence receipts

A machine-readable report should reference:

- evidence receipt/tree hash;
- exact local source identity for each finding where available;
- external scanner/advisory identity for current vulnerability claims;
- commands and result identity for executed validation.

Receipts are evidence, not proof of semantic correctness. A hash proves byte identity only.

## Evidence-layer separation

Always distinguish:

- **structural evidence:** files, schemas, static checks, hashes, package shape;
- **behavioral evidence:** executed scenarios/tests demonstrating behavior;
- **runtime evidence:** actual application/agent/tool execution;
- **external-current evidence:** current scanner/advisory/policy source data.

Do not let one layer stand in for another.
