# Evaluation Provenance

Use when a durable comparison/promotion record should explain how evaluation evidence was produced. The shape borrows provenance concepts from SLSA but does not claim SLSA compliance or supply-chain attestation strength.

Validate with:

```text
<PYTHON> scripts/validate_evaluation_provenance.py <PROVENANCE.json>
```

Record separately:

- harness/builder identity and invocation id;
- process/evaluation-policy identity;
- external parameters that materially configure the run;
- resolved dependencies such as scenario/evaluator/environment identities;
- baseline/candidate/trace identities as applicable;
- produced report/package/evidence subjects by digest.

The provenance identity binds the declared record. It does not prove that an unavailable external service or hidden runtime state was reproduced. Keep it distinct from source, environment, candidate, and delivery receipts.
