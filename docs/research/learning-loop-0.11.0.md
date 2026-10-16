# RhapsodIA 0.11.0: evidence-backed execution learning

## Source and scope

Bounded source: user-supplied automatically generated transcript for [qLfSDQ5NGh0](https://www.youtube.com/watch?v=qLfSDQ5NGh0), SHA-256 `13e04708b4400741318141a7a8e4d29da8eae446c4651e448f5f44aa170b8ba8`. Baseline: original supplied distribution archive SHA-256 `f5780134b28e5b82c0db94e0ea8b56281fce7c11fcf324e89dab5b30f7b92cc8`. No claim that video authors' benchmark numbers independently apply to Rhapsodia. See [machine-readable trace](learning-loop-0.11.0-traceability.json) for all six findings, dispositions and source-to-requirement-to-change-to-evaluation links.

## Decisions

- **Implement:** optional `workspace-knowledge-v2` execution episodes in the existing Graph, with distinct observed evidence, read-only grouping, stale-source/duplicate/conflict exclusions and explicit independent promotion requirement. Do not add an unrelated memory service, graph provider or orchestrator.
- **Implement:** MAGIA verifies the actual caller/public path for integrated features rather than equating isolated checks with feature completeness; report integration evidence gaps without inventing proof.
- **Already covered:** bounded loops, frozen evaluators, independent reviewers, and canonical Mago/Magia/Nomia ownership. Retain existing gates and only reference them.
- **Not applicable:** automatically making new project-context skills, replacing canonical product source or silently updating agent instructions. Treat video-described automatic rewriting as a proposal mechanism subject to a separate owner and frozen gate.
- **Uncertain:** model/host behavior, quality improvements and billed-token savings across VS Code/Copilot, Cursor, Codex, Claude, ChatGPT and other runtimes. Static portable contracts are not host execution evidence.

## Independent safety contract

The producer records sanitized, source-pinned observed episodes but cannot edit its own reviewer, evaluator, fixtures, or the instruction promotion gate. `review-lessons` is a read-only bounded report, not instruction deployment. Candidate guidance must pass authorized owner decisions, separate frozen evaluator identity, semantic regression and packaging gates. Distinct file hashes are not independent proof of causal truth; the reviewer still inspects actual sources. Content freshness is rechecked before reliance.

## Compatibility and validation

RhapsodIA distribution remains **0.11.0** as explicitly requested. Local Graph Engine changes to **3.2.0** (additive CLI/schema); Mago, Magia and Nomia remain together at their coordinated **2.0.0** skill identities; only the native MAGIA agent profile and release guidance expand the explanation of execution closure. Existing v1 records, SQLite storage, legacy graph queries, harness start, opt-outs, native agent routing, security/authority boundaries and other 55 skills are not replaced. `VERSION`/changelogs describe changed subpackages; changed distribution bytes cannot be asserted identical to the original published 0.11.0.

Executed evidence: eight new CLI/regression scenarios passed; the existing graph suite completed 103 tests with five skips; the agent validator reported zero errors/warnings, and the distribution generator/check retained `0.11.0`. These checks do not prove cross-host runtime equivalence, live native editor behavior, or performance/tokens. The complete mandatory-session suite exceeded the command limit and is **not claimed passing**. Verification must be rerun in the intended host/CI environment for full release assurance.

## Exact reproduction (from repository root)

```text
python -I -S -B -m unittest discover -s tests -p 'test_workspace_lessons.py' -q
python -I -S -B -m unittest discover -s skills/local-graph-engine/tests -p 'test_*.py' -q
python -B scripts/validate_agents.py --target .
python -B scripts/prepare_release.py --check
python -B skills/research-traceability/scripts/validate_traceability.py docs/research/learning-loop-0.11.0-traceability.json --phase final
```
