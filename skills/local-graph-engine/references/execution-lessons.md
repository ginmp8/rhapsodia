# Source-pinned execution lessons and read-only pattern review

## Purpose, load and decision impact

- **Purpose:** Preserve reusable observations about feature-execution mistakes as advisory data across authorized sessions.
- **Load when:** Publishing `workspace-knowledge-v2` lessons, reviewing recurring failures, or assessing whether a candidate rule may be proposed to an independent evaluator.
- **Decision impact:** Distinguishes observed and hypothetical outcomes, independent evidence from duplicated records, and candidate guidance from authorized instructions. Does not grant Magia planning/governance authority or change frozen tests.

## Contract and examples

Use `scripts/workspace_memory.py --workspace <ROOT> learn` with JSON on stdin or `--input <file>`. The workspace graph must already be initialized by the normal session gate unless the user expressly opted out (in which case do not use this command). The complete [v2 JSON schema](../contracts/workspace-knowledge-v2.schema.json) is normative for lessons. `v1` references/remedies are unaffected.

```json
{
  "schema": "workspace-knowledge-v2", "key": "feature-a-public-flow",
  "kind": "lesson", "title": "Public flow not wired",
  "summary": "An isolated test passed but the public path did not use the new behavior.",
  "tags": ["integration"],
  "sources": [{"path": "docs/implementation/feature-a-evidence.md", "sha256": "<actual_sha256>"}],
  "episode_id": "feature-a", "failure_signature": "missing-public-wiring",
  "observed_outcome": "observed-failure", "integration_status": "not-integrated",
  "verification": "Observed the public route still using the old handler.",
  "proposed_rule": "Verify consumer-path wiring with a suitable integration check."
}
```

The snippet is illustrative: replace the placeholder digest with the actual value from `pin`; do not publish without a real content-pinned file. A failed test is evidence only of what that test observed; do not relabel a hypothesis as an observed failure. Each episode is one bounded feature/run and needs its own supported source record. No credentials, environment values or raw logs. Stable keys are revision-locked; use `expected_revision` for updates.

## Review and stop policy

`<PYTHON> -I -S -B scripts/workspace_memory.py --workspace <ROOT> review-lessons` is **read-only** and does not bootstrap missing state. It considers up to 512 pinned lesson records, rejects stale sources, excludes unobserved failures, deduplicates matching episode IDs and identical content digests, and requires **at least two** independent source-backed failures with one consistent proposed rule per failure signature. Conflict returns an explicit conflict; oversized scopes return `blocked`, never truncated candidate evidence.

Returned `candidates[].promotion=requires-independent-evaluation` is **not approval**: the evaluator/test/acceptance semantics must be frozen independently of the producer. Revisit affected callers, runtime integration, security and failure modes. A review cannot change prompts, agent roles, skill files, evaluators, expected outputs, or production code. MAGIA alone owns execution/repair in authorized scope; Mago owns new technical intent and acceptance; Nomia owns governance. Apply learned guidance only via a separate authorized, versioned, independently gated change. A noncandidate finding can remain in memory for future investigation.

## Portability and limits

Stdlib Python 3.10+ and SQLite; no cloud, service, external orchestrator, host-specific hooks, MCP requirement or automatic long-running process. Hash identity verifies source bytes, not the truth or completeness of the contents. Agent-reported lessons may be wrong; source reading, independent tests and fresh host verification remain necessary. Private `.rhapsodia/` memory is not a package fixture, public data export or replacement for canonical artifacts.
