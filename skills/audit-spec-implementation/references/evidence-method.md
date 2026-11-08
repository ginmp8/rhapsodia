# Evidence and adversarial verification method

Use only the sections relevant to the feature. This reference expands the main skill; it never expands the user's authorized scope.

## Atomic requirement examples

- `REQ-001` (authorization): Given a read-only session, when a user attempts an administrative state transition through any supported entrypoint, the system denies the transition and leaves persisted state unchanged.
- `REQ-002` (retry): When the same event is delivered twice, the second delivery does not repeat the external side effect.
- `REQ-003` (UI): When the user selects a new board column, the card updates visually and the persisted state is consistent after refresh.

For each criterion, identify the actor, prior state, stimulus, observable state/output, error semantics, and explicitly excluded cases. Do not split semantic duplicates into inflated requirements. If a requirement contains independently falsifiable obligations, split them.

## What counts as evidence

| Evidence | Supports | Does not support |
|---|---|---|
| Issue section/comment at known version | Normative expected behavior | Implementation completion |
| Existing symbol/function or PR diff | Declared implementation | Runtime reachability or correctness |
| Entry point -> guard -> effect traced at frozen commit | Static path and required conditions | Unobserved external outcomes under all conditions |
| Test source with meaningful assertions | Intended checked contract | Executed result |
| Green aggregate CI badge | A named job outcome at a point in time | Every acceptance criterion |
| Recorded focused test, SHA + environment + exit/output | One bounded observed case | Universal correctness |
| Contract test at public boundary | Observed serialization/auth/state contract for tested cases | Untested alternate paths |
| Unavailable source or environment | Scope limitation | A reason to infer PASS |

Distinguish `test_defined`, `test_executed`, `runtime_observed`, `static_proof`, `inferred`, and `unknown`. Link every result to the source and revision that actually produced it. For a line-specific citation use an immutable permalink when possible, e.g. `https://github.com/owner/repo/blob/<SHA>/path/file.cs#L10-L20`. Never manufacture line numbers from search snippets.

## Falsification strategy

For each substantial claim, explicitly ask what realistic input or competing path would make it fail. Choose the narrowest realistic proof layer that can observe that fault.

1. **Normal path**: expected state and visible output, including persistence and refresh where material.
2. **Denied path**: forbidden role/session/tenant; verify both rejection and *absence of side effects*.
3. **Alternate writers**: endpoints, RPC, background workers, message consumers, migration jobs, admin operations or configuration that bypass the primary guard.
4. **Retries/concurrency**: duplicate requests, reordered messages, racing actors, stale version/lock, timeout followed by retry; exercise only when pertinent.
5. **Partial failure**: storage succeeds but publish fails, send succeeds but confirmation fails, dependencies time out, rollback compensation or recovery.
6. **Compatibility**: caller version skew, feature flag disabled, serialization defaults, schema/route changes, original upstream behavior, shared states.
7. **Test sensitivity**: identify a concrete regression that a test would detect. Empty/snapshot-only or overmocked tests cannot prove a side effect at an unobserved boundary.

## Security and data guardrails

Treat authorizations and data isolation as boundary properties: verify at every reachable state-mutating entrypoint, not just the UI. Use examples without live secrets. Do not attempt destructive operations against production, third-party targets, or unapproved systems. Tests executing repository-controlled scripts require an appropriately isolated and authorized environment. Lack of runtime proof is an `UNVERIFIED` evidence gap, not a reason to change fixtures or relax assertions.

## Severity guidance

- **Critical**: demonstrable unauthorized sensitive access, destructive data loss, systemic security break, or similarly severe exploitable violation.
- **High**: core acceptance criterion broken, wrong-party authorization, durable inconsistency, or plausible major regression with material impact.
- **Medium**: meaningful partial behavior, missing important negative path, interoperability or observability gap that undermines acceptance evidence.
- **Low**: bounded minor defect without significant harm; evidence must still be concrete.

Severity reflects real impact *and* likelihood/conditions, not reviewer preference. Mark potential-but-unverified risk as such; do not overstate a speculative finding as demonstrated behavior. Do not create new normative requirements from generic quality advice.

## Version drift and upstream changes

When auditing a port or fork: freeze upstream version/commit and extended candidate commit; identify expected inherited behavior and intentionally different behavior separately. Compare original and candidate under identical stimuli when authorized. Record upstream functionality not ported, behavior differences and test gaps; distinguish upstream bugs from intended parity. Never treat differences as defects without checking stated compatibility scope. If the original code/test is unavailable, say which equivalence claims remain unverified.
