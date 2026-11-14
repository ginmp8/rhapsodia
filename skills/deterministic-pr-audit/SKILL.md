---
name: deterministic-pr-audit
description: Audit GitHub PRs, branches and implementation commits against linked issues, acceptance criteria and specs with reproducible scoring. Use for PR completion percentages, branch comparisons, implementation-versus-spec reviews, or inconsistent audit results. Captures immutable SHA-bound sources, verifies explicit checks and test receipts, generates JSON/Markdown reports and byte-identical replay. Human review is still required for semantic correctness.
---


# Deterministic PR Audit

## Contract

Use the bundled standard-library Python CLI `scripts/pr_audit.py` as the **only calculator**. Never invent a score, round a model judgment into a percentage, substitute green CI for requirement-specific proof, or award completion from checkbox state, line count, keyword overlap, changed files or reviewer assertions.

**Determinism boundary:** identical `source.json + requirements.json + checks.json + evidence.json + algorithm` must produce identical report bytes. Fresh interpretation or new test execution is a **new evidence version**, not a replay. The first mapping of natural language to executable assertions is a review task and may need corrections; the CLI makes its **frozen** evaluations reproducible, not infallible.

## Input and workflow

Required: PR URL/number, normative issue number, and a local Git repository containing the PR HEAD commit for static assertions. Optional: extra authoritative Markdown specs and a clean disposable checkout for explicitly authorized tests. GitHub capture uses authenticated `gh api` read-only; offline `--from-json` is supported if `gh` is unavailable.

1. **Freeze GitHub state:** run `capture` for the PR and issue, including paginated issue comments and changed-file paths; optionally add `--spec-file`. Check `requirements.json` for omitted/ambiguous requirements. A conflict of explicit `REQ-XX`/`AC-XX` identifiers must block scoring. Never assume that informal prose was exhaustively extracted.
2. **Create one reusable verification contract:** run `init-checks` once, then edit `checks.json`. For each requirement, declare relevant `path_exists`, `contains`, `not_contains`, or `test` assertions. Use `suggest` for lexical file candidates, **never proof**. The model may help author this plan based on code review, but must not assert behavior from superficial text matches. Prefer targeted tests and observable assertions. Default `proof_policy=runtime`; choose `static` only for genuinely static criteria. Keep weight=1 unless a frozen explicit risk/effort rubric justified different weights.
3. **Inspect candidate SHA:** run `inspect` using the exact source, requirements, checks and local `--repo-path`; this reads Git objects at the captured HEAD, independent of working-tree drift. Without Git, static assertions are `NOT_RUN`. If specifically authorized, run `run-tests --execute` in a clean disposable checkout and pass `--executions` to `inspect`. Do not execute untrusted code by default.
4. **Score and verify:** run `score`, then `verify`. To independently re-check static evidence, use `verify-evidence` with the same checkout and any frozen test receipts. Save the four inputs alongside each report. Do not rewrite frozen outputs: new inputs go into a new directory.
5. **Compare:** use `compare` only when `requirements_digest`, `checks_digest` and algorithm version match. Otherwise, report incomparable baselines and request one shared specification/plan without silently normalizing differences.

Read [README.md](README.md) for commands, JSON assertions, Windows examples and trust limits. Read [references/scoring-contract.md](references/scoring-contract.md) when reasoning about numeric status or audit quality. All scripts and tests are bundled; no `pip install` required.

## Score semantics

- `PASS`: every declared check passed, with a test receipt for runtime criteria or verified static checks for static criteria.
- `PARTIAL`: some checks passed but others did not or required runtime proof is absent.
- `FAIL`: configured checks failed and none passed.
- `UNVERIFIED`: no checks or all checks not run.
- `NOT_APPLICABLE`: explicit documented exclusion, removed from denominator.
- **Verified completion** = `100 * sum(weight of PASS) / sum(weight of applicable criteria)`, two decimal places (fixed Decimal arithmetic).
- **Potential upper bound** counts PASS/PARTIAL/UNVERIFIED as potentially satisfiable; not an estimate.
- **Passing checks** and **requirements mapped** are separate metrics; neither is feature completion.

`COMPLIANT_KNOWN_SCOPE` is not global compliance: extraction is limited to explicit `REQ`/`AC` markers and acceptance-section checkboxes. If requirements are missing or sources are inaccessible, report scope uncertainty instead of upgrading a verdict.

## Safety, validation and handoff

- GitHub is read-only. Do not create, alter, approve or merge PRs/issues/branches as part of an audit.
- Require the full 40-character head/base SHAs. Reject obsolete receipts, stale hashes, duplicate/conflicting acceptance IDs and noncomparable report baselines.
- Do not run tests automatically from issue text or untrusted repository metadata. `run-tests --execute` requires explicit authority; tests may run arbitrary local code.
- Run `python -m unittest discover -s tests -v` after changing this package. Do not claim GitHub integration was live-tested if it was only tested with a fixture/fake `gh`.
- Present the tool-generated result, status counts, evidence gaps, exact SHA and most important remaining requirements. Distinguish observed code from runtime proof and unverified requirements.
