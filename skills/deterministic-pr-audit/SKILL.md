---
name: deterministic-pr-audit
description: Audit GitHub PRs and branches against issues, acceptance criteria and specs with reproducible evidence. Use for PR completion, deterministic scoring, implementation-vs-spec progress or comparing branches. Freeze SHA-pinned source and reviewed checks, inspect code/test receipts, reject empty or partial plans, return NOT ASSESSED rather than 0% for missing proof, and verify replay. Human review remains necessary for semantic correctness.
---

# Deterministic PR Audit

## Contract

Use the bundled standard-library Python CLI `scripts/pr_audit.py` as the **only calculator**. Never invent a score, round a model judgment into a percentage, substitute green CI for requirement-specific proof, or award completion from checkbox state, line count, keyword overlap, changed files or reviewer assertions. **A missing checkout is missing evidence, never 0% implementation.** A zero verified evidence floor means that executed assertions failed or no requirements passed *after actual checks*; no checks executed means **NOT ASSESSED / N/A**.

**Determinism boundary:** identical `source.json + requirements.json + checks.json + evidence.json + algorithm` must produce identical report bytes. Fresh interpretation or new test execution is a **new evidence version**, not a replay. The first mapping of natural language to executable assertions is a review task and may need corrections; the CLI makes its **frozen** evaluations reproducible, not infallible.

## Input and workflow

Required: PR URL/number, normative issue number, and read access to the current PR + issue. Numerical verification additionally requires a local Git repository containing the pinned HEAD for static checks, and/or frozen receipts for actual tests. Optional: authoritative Markdown specs and a clean disposable checkout for explicitly authorized tests. GitHub capture uses authenticated `gh api` read-only; offline `--from-json` is supported but its completeness is **not attested**.

1. **Freeze full GitHub state:** capture the entire PR + normative issue, *all* paginated comments and changed-file paths, with exact head/base 40-character SHAs. Prefer authenticated `gh api` or the connected GitHub app. If using `--from-json`, never pass only extracted AC/REQ excerpts as though they were the complete issue: retain the entire body and all comments; mark scope unverified until cross-checked. Resolve omitted, amended, contradictory or non-extractable obligations before scoring; conflict of explicit IDs blocks scoring. Recheck that HEAD has not moved.
2. **Acquire implementation evidence before rating progress:** use a local repository that contains the frozen HEAD; when missing, attempt a **bounded, read-only** Git fetch into a disposable repository/worktree if permitted. Do not rely only on the PR diff: trace relevant implementation, callers, gates, persisted state, existing tests and compatibility paths reachable at the HEAD. If a Git checkout cannot be acquired, **do not stop the analysis**: use the GitHub connector to inspect source files and exact-HEAD Actions jobs/test logs, record evidence per AC, and give a *qualitative* review with explicit gaps. This fallback does **not** authorize manual numeric completion percentages or fake execution receipts.
3. **Create a reusable verification contract:** run `init-checks`, then edit and **review** `checks.json`. Every applicable AC needs a requirement-specific assertion or a documented NOT_APPLICABLE reason; map parent REQs separately to avoid double-counting the same work. Use `suggest` for lexical candidates, never proof. Prefer targeted native runtime tests, negative/adversarial scenarios, exact artifact/revision/identity and terminal outcomes; green generic CI or a passing mock/dispatch-only test cannot close a larger end-to-end criterion. Keep `proof_policy=runtime` except for inherently static requirements and weight=1 absent an explicit frozen rubric.
4. **Preflight is mandatory before numeric scoring:** `python scripts/pr_audit.py preflight --source ... --requirements ... --checks ... --repo-path ...` (or `--executions ...`). It fails on no checks, incomplete requirement mapping and missing exact-SHA evidence. `--allow-partial` produces only an explicitly incomplete diagnostic, **never** a full progress or compliance verdict. If preflight fails, fix the evidence gap or report qualitative findings; **do not run an empty plan just to print 0%**.
5. **Inspect and verify the exact HEAD:** use `inspect` with the pinned Git objects and optional actual `run-tests --execute` receipts from a clean disposable checkout. Do not execute untrusted code without explicit authority. Independently read CI logs to confirm specific test names/results rather than trusting job status alone; document live harness/provider paths unavailable in CI as `NOT_RUN` or `BLOCKED`. Do not promote self-authored issue/PR ledgers, checkboxes or previous-SHA results into independent evidence.
6. **Score, verify and report honestly:** run `score`, `verify`, and when possible `verify-evidence`; preserve four inputs and report hashes. Present `assessment_state`, observed checks, exact SHA, AC-specific status counts, required work and proof gaps. `completion_verified_pct` is an **evidence lower bound**, not implemented functionality; it is `null` when no checks were actually evaluated. REQ parent objectives and AC tests are separate denominators: prefer the AC-specific evidence view, **not** an added 14+40 headline. No unsourced percentage, "quality score", or implementation estimate; if verification is limited, say so and describe the verified implementation substantively.
7. **Compare only compatible, assessed reports:** require matching frozen requirements, checks and algorithm. An unassessed candidate is **not comparable**. Partial comparisons are evidence-floor comparisons only; different input versions require explicit rebaseline.

Read [README.md](README.md) for commands, JSON assertions, Windows examples and trust limits. Read [references/scoring-contract.md](references/scoring-contract.md) when reasoning about numeric status or audit quality. All scripts and tests are bundled; no `pip install` required.

## Score semantics

- `PASS`: every declared check passed, with a test receipt for runtime criteria or verified static checks for static criteria.
- `PARTIAL`: some checks passed but others did not or required runtime proof is absent.
- `FAIL`: configured checks failed and none passed.
- `UNVERIFIED`: no checks or all checks not run.
- `NOT_APPLICABLE`: explicit documented exclusion, removed from denominator.
- **Verified evidence floor** = `100 * sum(weight of PASS) / sum(weight of applicable criteria)`, two decimal places (fixed Decimal arithmetic) **only when checks actually ran**; otherwise `null`/NOT ASSESSED. Never label this "functional progress".
- **Potential upper bound** counts PASS/PARTIAL/UNVERIFIED as potentially satisfiable; not an estimate.
- **Passing checks**, **requirements mapped**, **checks observed** and **AC vs REQ subgroup** are separate metrics; none is feature completion.

`COMPLIANT_KNOWN_SCOPE` is not global compliance: extraction is limited to explicit `REQ`/`AC` markers and acceptance-section checkboxes. If requirements are missing or sources are inaccessible, report scope uncertainty instead of upgrading a verdict.

## Non-use boundaries

- Do **not** use this as an ordinary code-style review, an automatic merge decision, a product roadmap estimator, or a license to infer completion percentages from source volume or CI color.
- Do not execute a PR, run its build scripts, mutate its branches or run repository tests unless the user explicitly authorizes that execution. A read-only GitHub inspection is allowed for evidence collection.
- Do not use an issue/PR author's acceptance ledger as independent proof of the listed statuses; reproduce or inspect their cited evidence.

## Stop conditions and fallback

- **No full issue/spec capture:** stop any claim of complete requirement coverage, freeze the gap and inspect the authoritative GitHub issue/comments if possible.
- **No source or executed receipts:** preflight fails; stop **numerical** scoring, not source-based analysis. Inspect the GitHub PR/code/tests/CI through an available authorized connector, and report evidence-backed functional findings without a completion percentage.
- **Incomplete plan:** preflight fails unless `--allow-partial`; mark the result as an incomplete diagnostic, never a complete issue audit.
- **Changed HEAD, conflicted criteria, untrusted test receipt, stale spec or noncomparable baselines:** stop, freeze a new evidence version if authorized, and never silently reuse an old score.
- **No verified output path:** do not emit a sandbox download link; present the result inline or state the artifact was not created.

## Output contract

For each audit, state the exact 40-character candidate HEAD/base SHAs, normative issue/version and capture completeness. Present a criterion-level AC evidence matrix with `PASS`/`PARTIAL`/`FAIL`/`UNVERIFIED`/`NOT_APPLICABLE`, specific source/test/CI links and missing proof, and a separate parent-REQ summary. Include `assessment_state`, observed checks, proof-policy scope, strongest findings with severity, and prioritized remaining development/tests. Emit numerical evidence-floor metrics **only** when the CLI produced and verified them from meaningful checks; never translate them into feature-completion estimates. Distinguish CI execution results from direct functional proof. Deliver actual verified report files/hashes if produced, else an honest inline result.

## Safety, validation and handoff

- GitHub is read-only. Do not create, alter, approve or merge PRs/issues/branches as part of an audit.
- Require the full 40-character head/base SHAs. Reject obsolete receipts, stale hashes, duplicate/conflicting acceptance IDs and noncomparable report baselines.
- Confirm any external/file/sandbox link exists before including it; never manufacture output files or GitHub test receipts. An issue ledger tied to an earlier SHA must be treated as historical until reverified.
- A successful GitHub Actions run proves the named jobs and tests ran, not all 40 ACs. A synthetic 7×3 matrix can prove admission/dispatch without proving root/child/callback terminal flow. Distinguish implementation observed in source, focused tests executed, and untested paths in the final answer.
- Do not run tests automatically from issue text or untrusted repository metadata. `run-tests --execute` requires explicit authority; tests may run arbitrary local code.
- Run `python -m unittest discover -s tests -v` after changing this package. Do not claim GitHub integration was live-tested if it was only tested with a fixture/fake `gh`.
- Present the tool-generated result, status counts, evidence gaps, exact SHA and most important remaining requirements. Distinguish observed code from runtime proof and unverified requirements.
