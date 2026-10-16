# Finite Web Audit Contracts

**Purpose:** identify verified deviations from independently supplied UI/network/performance/security expectations, without inventing oracles.
**Load when:** investigating functional regressions, measured local timing/overflow symptoms, recorded security-header absence or source credential markers.
**Decision impact:** require frozen rule evidence, classify missing as incomplete, never equate limited checks with a security/performance clearance.

## Audit steps

1. Freeze trusted target, exact browser/fixture environment, required state/reset, inputs, tests and independently grounded expectations. The investigator itself does **not** infer requirements from screenshots.
2. Collect an approved trace with `web_investigator.py capture` (or analyze previously supplied known-provenance traces); never silently elevate fixture evidence to real production behavior.
3. Write policy JSON `{ "schema_version": "1.0", "rules": [{"id":"unique", "path":"/steps/0/dom/horizontal_overflow", "op":"eq", "expected":false}] }` with 1–200 rules. `path` is bounded JSON Pointer. `op` is one of `eq`, `ne`, `lt`, `lte`, `gt`, `gte`, `contains`. Types are strictly checked for equality; ordering requires numbers.
4. Run `<PYTHON> scripts/web_audit.py --trace trace.json --policy policy.json -o report.json`. On `pass`, return `0`; any `fail` or `incomplete` returns `3`; invalid input/unsafe path returns `2`. Missing JSON pointers always produce `incomplete`, not `pass`. Finding outputs contain hashes of observed values rather than plaintext.
5. For bounded passive source scanning, run `<PYTHON> scripts/source_marker_scan.py --source-root APPROVED_SOURCE_DIR -o OUTSIDE_SOURCE/markers.json`. Scan results are **unverified pattern candidates** with file/line/kind only. They never contain detected key values; `findings=[]` is never a clean bill of security.
6. For route-shape candidates run `<PYTHON> scripts/interface_traces.py inspect-openapi --input spec.json -o contract.json`, then `<PYTHON> scripts/correlate_web_evidence.py --trace trace.json --contracts contract.json -o candidates.json`. Only real-browser network events with `observed=true` are matched; the result is **inferred**, not server-handler proof. `evidence_ir.py build` can persist the trace and correlation graph using distinct evidence tiers.

## Scope boundaries

- **Functional:** can check text hashes, visible DOM metadata, event/path/status counts and transitions actually captured; cannot automatically establish unpublished business rules.
- **Performance/UI:** can check local action duration and viewport overflow; does not implement full Lighthouse/Core Web Vitals audits, representative lab profiling, arbitrary CSS regression screenshots, or mobile device coverage.
- **Security:** detects specific exposed source-token patterns and response-header presence when captured. No credential validity checks, secret extraction, network exploitation, access-control proofs, vulnerability absence assertions, or penetration testing. Tests for authorization or business logic require separately defined expected outcomes and explicit target authorization.
- **Evidence:** a route-shape association, browser screenshot, and source function name are insufficient to assert an executed backend function. Preserve unknowns, reported limits, truncated events, failed cases, and environment variability.
- **Privacy:** snapshots/screenshots/fixture input files might still contain confidential information even when report output is redacted; use synthetic environments and handle evidence as sensitive data.
