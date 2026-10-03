# Artifact-native release delivery

## Delivered scope

This full repository is based on the supplied `rhapsodia-main (2).zip`, not a merge of the old refactor. Unrelated skills and original evaluator/fixture data are retained. Native artifact operation replaces Board as the default; supported legacy compatibility is explicit, not a future implementation task.

| Surface | Delivered behavior |
|---|---|
| Domain ownership | Nomia owns governance, Mago planning, Magia execution. Each decides, authors and validates its own artifacts. |
| Independent storage | `docs/product/<work_item_id>`, `docs/specs/<work_item_id>`, `docs/implementation/<work_item_id>`; configurable non-overlapping owner roots. |
| Artifact publication | Adjacent strict/versioned sidecars, exact source hashes, identity/revision guards, privacy/provenance and a uniform validated `artifact_actions` contract. |
| Planning | Local immutable planning identity and quick/standard/governed semantic gates, without Board identity/path requirements. |
| Execution | Explicitly trusted command execution, exact candidate/planning receipts, REQ/AC/VAL/dependency checks, own-only execution state and stale-evidence rejection. No Mago task checkbox, registry or governance writeback. |
| Workspace | Standalone optional skill: discover, validate, index, project and render. Only derived outputs are writable. |
| Interface | Offline HTML: portfolio, metadata-update timeline, typed relations, per-skill inventory, search, filters, details, themes, snapshot import/export and narrow-screen layout. |
| Agents | Existing roles preserved; seventh bounded Workspace operator added; Supervisor routes owners and optionally refreshes the view after source writers finish. |
| Legacy migration | Owner-local plan/apply, original preservation, exclusions, unknown-state publication, idempotency, conflict rejection and hash-approved recovery/finalization. |
| Packaging | External executed evidence with exact tree digest; packagers never execute target validators; deterministic archive, stale-evidence rejection and last-good preservation. |
| Legacy hardening | Canonical root containment/identity, real dates, created-at/spec/cycle agreement, dependency parser and manifest/registry consistency. |

## Version and compatibility decision

Mago, Magia and Nomia are a coordinated **2.0.0** set. Workspace starts at **1.0.0**. The agent-layer distribution manifest is **3.0.0**, and marketplace/plugin metadata is **0.2.0**. These are component identities, not interchangeable version numbers.

Domain handoff v3 and its ownership, privacy, provenance, direction and freshness gates remain in force. Artifact envelopes/actions are a separate version-1 extension. Existing frozen cross-skill and routing scenarios are retained byte-for-byte and explicitly hash-pinned. The old Nomia packaging subprocess helpers are deliberately retired with a major-release migration declaration; no failing/dead compatibility stubs replace them.

## Executed test evidence

The table counts each test suite once; repeat executions during attestation are not added to the total.

| Suite | Tests passed | Subtests passed | Result |
|---|---:|---:|---|
| root | 74 | 6 | pass |
| mago | 189 | 21 | pass |
| magia | 197 | 10 | pass |
| nomia | 167 | 21 | pass |
| rhapsodia-workspace | 59 | 127 | pass |
| **Total** | **686** | **185** | **pass** |

The complete native integration test creates governance without a Board/spec, creates and validates Mago planning, executes a real bounded Magia check, closes only Magia state, publishes the three owners' records and recreates the Workspace while verifying source bytes are unchanged. Migration tests include interrupted copies, explicit recovery approval, preservation of later user edits, committed-copy finalization and cross-root rejection.

Browser validation executed **13 checks** in system Chromium: all four views, search/empty state, producer filter, details, theme, export, import warning, invalid-import last-good preservation, and 320px layout. There were no console errors or external network requests. The generated HTML was loaded with Playwright `set_content`; this managed browser blocks `file://` navigation, so operating-system file association / file-URL policy is not claimed as tested. Desktop and mobile screenshots were inspected.

The baseline Magia package had two failing packaging tests. The candidate repairs the structural-validator/test-recursion boundary and updates the packaging API regression test to require explicit external evidence rather than silently execute target code. Negative gate assertions are retained and extended; frozen evaluator expected results were not rewritten.

Exact commands, output logs, return codes, hashes, browser checks, structural portability reports and release receipts are in `validation/`. Full external-host agent behavior was not simulated or scored.

## Acceptance and finding closure

| Finding | Disposition | Evidence |
|---|---|---|
| Board as mandatory shared storage | fixed | Native publishers, planning, execution and end-to-end tests; Board-absent migration/index test. |
| Central organizer moving peer files | rejected design | Workspace has no canonical mutation operation; owner/cross-root regression tests. |
| Inconsistent worker artifact outputs | fixed | Common action schema and live receipt validation; agent contract v3. |
| Arbitrary target execution during packaging | fixed | Data-only packagers, external execution boundary and untrusted-target negative tests. |
| Stale validation or stale source accepted | fixed | Exact tree/source/candidate/planning hashes and mutation/conflict tests. |
| Legacy date/identity/dependency drift | fixed | Restored stricter parsers and regression cases. |
| Migration loss / interrupted partial copy | fixed | Copy-only journal, recovery approval, original preservation and edited-target rejection tests. |
| Per-skill runtime coupling | fixed | Package-local protocol copies; standalone tests and provenance equality gates. |
| Legacy Board retained | accepted design boundary | Explicit maintenance/migration profile; never required by native operation. No further removal is needed to use native workflows. |
| Unsigned receipt authenticity | accepted trust boundary | Controlled runner/receipt channel required. A hash proves identity/freshness, not authorship. |
| Offline snapshot instead of live server | accepted design boundary | Synchronous rebuild; no daemon, backend, dependency installation or writeback. |
| External IDE/model execution | evidence boundary | Structural host matrix passed; no claim of runtime execution inside each external product. |

There are no deferred implementation items within the agreed scope. These explicit compatibility, trust and evidence boundaries are part of the delivered design, not hidden completion claims.

## Start using the interface

From the Rhapsodia checkout, select the repository that contains real producer-published artifacts:

```text
python skills/rhapsodia-workspace/scripts/workspace.py validate --repo-root /path/to/project
python skills/rhapsodia-workspace/scripts/workspace.py index --repo-root /path/to/project
python skills/rhapsodia-workspace/scripts/workspace.py render --repo-root /path/to/project
```

The output is `/path/to/project/.rhapsodia/views/index.html`. No backend is required. A project with no published sidecars correctly produces an empty view; it does not invent project progress. `demo.html` is a ready-to-inspect **synthetic** UI specimen, not live repository state.

Each owner publishes only after its domain validation:

```text
python <installed-owner-skill>/scripts/native_artifacts.py publish --repo-root <PROJECT> --input <REQUEST.json>
python <installed-owner-skill>/scripts/native_artifacts.py validate-actions --repo-root <PROJECT> --input <RECEIPT.json>
```

See each owner's `references/artifact-native.md` for the complete request/workflow rules, `docs/agents/ARTIFACT-ORCHESTRATION.md` for agent responsibilities, and `skills/mago/references/ecosystem-migration.md` for coordinated migration/rollback. Existing install and marketplace commands remain in the root README.

## Reproduce checks

Use Python 3.11+ and the documented development dependencies. Workspace/native publication uses the standard library; existing Mags semantic validation retains its declared YAML dependencies. Commands are portable argv/paths, not vendor-private invocation APIs.

```text
python -m pytest -q -p no:cacheprovider tests
python scripts/validate_agents.py --target .
python scripts/generate_marketplace_manifests.py --check
python scripts/validate_and_attest.py --target skills/mago --output /outside/target/mago-validation.json --trust-target-code
```

Repeat trusted attestation for each of the four changed skills. Inspect target code before giving execution approval. `package_skill.py` consumes the resulting evidence without executing target code. Receipts bind these exact skill bytes; editing them requires revalidation. Old Board artifacts remain intact for rollback, and derived catalogs may always be deleted and rebuilt.

## Final release verification

All four packages passed the three external executed gates (structure, full tests, contracts): **12/12 gates**. All four passed the canonical Agent Skills structure validator and structural portability checks for portable-core, OpenAI, Codex, Claude, Copilot and Cursor. Native execution inside each external product was not claimed. The agent-layer validator reports zero errors/warnings, and generated marketplace manifests are synchronized.

The frozen SDD auditor's **current-package audit passed for all three Mags**. Its before/after text-diff mode still returns `fail` for **36 removed-line signals**, including version changes and minified JSON replaced by formatted JSON. The evaluator and raw results were not changed. Every signal was reviewed against the actual replacement, parsed semantic differences, ownership boundaries, frozen fixture hashes and executed tests; all 36 are closed in `validation/semantic-adjudication.md` / `.json`. The semantic review outcome is **pass with warnings**, not an invented automated diff-check pass. This was an assistant read-only review, not a separate-model review.

A final review also repaired stale release prose and the handoff's nested required-release declaration, and added a standalone/pytest-compatible regression test plus a contract gate tying both to `VERSION`. The final evidence includes these repaired bytes.

Each changed skill was packaged **twice** using its executed receipt; both runs produced byte-identical ZIPs. See `validation/skill-packaging-results.json` for archive hashes and source/evidence binding. The complete repository archive is broader than those individual packages: it retains the full main source tree, unrelated skills, original evaluators, all implemented changes, this report, audit receipts and a synthetic UI demo.

The external full-repository manifest and `.sha256` companion bind the final delivery archive. No input archive was modified, and no source file from main was removed.
