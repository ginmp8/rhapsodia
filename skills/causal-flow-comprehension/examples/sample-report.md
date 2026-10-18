# Example report (synthetic, not system evidence)

**Question:** Can Active be persisted without approval?
**Verdict:** Insufficient evidence. **Scope:** Two illustrative excerpts at fixture-v1; no runtime observation.

**Mechanism:** In the sample API, approval guards event publication (`SRC-001`, `CL-001`). A separate consumer depicts a write to Active (`SRC-002`); delivery and all possible writers are unverified (`CL-002`).

| Claim | Class | Evidence |
| --- | --- | --- |
| Approval guards the shown route | static-observed | `SRC-001` |
| No other path can activate | unknown (not established) | `CL-003`, no exhaustive inspection |

**Counterexample/next check:** Look for any other state writer, an independent consumer, or a feature-flag bypass. Inspect actual repo + runtime config and run a controlled test before claiming a universal invariant.
