# Deterministic PR Audit

A **working Python CLI plus ChatGPT Skill** for comparing PRs to GitHub issues with a stable, evidence-backed score. Python 3.10+ and `git` are required for source inspection. The GitHub CLI (`gh`) is needed only to capture live GitHub data (`gh auth login` if needed). There are no Python dependencies.

> Deterministic **calculation** is not the same as automated understanding of an arbitrary specification. The first-time mapping from each acceptance criterion to meaningful code and test checks must be reviewed and frozen. **No executed checks yields `NOT ASSESSED` and an N/A verified evidence floor, NOT 0% implementation.** An incomplete plan is not a full audit. The CLI cannot honestly estimate implemented percentage from source presence, PR size, or green CI alone.

## Fast start (example: PR #154, issue #148)

From the extracted Skill folder, run:

```bash
# 1. Freeze issue, all issue comments, PR metadata, full SHAs, and changed files.
python scripts/pr_audit.py capture \
  --pr-url https://github.com/ginmp8/pandacode-extended/pull/154 \
  --issue 148 --out audits/pr154-a

# 2. Generate one reviewable evidence plan. Do this only once per spec version.
python scripts/pr_audit.py init-checks \
  --requirements audits/pr154-a/requirements.json \
  --out audits/issue148-checks.json

# 3. Find possible code locations (advisory only).
python scripts/pr_audit.py suggest \
  --source audits/pr154-a/source.json \
  --requirements audits/pr154-a/requirements.json \
  --repo-path /path/to/pandacode-extended \
  --out audits/pr154-a/hints.json

# 4. Edit audits/issue148-checks.json once, adding real assertions.
# 5. REQUIRED PREFLIGHT: fail if no evidence, no plan, or incomplete mapping.
python scripts/pr_audit.py preflight \
  --source audits/pr154-a/source.json \
  --requirements audits/pr154-a/requirements.json \
  --checks audits/issue148-checks.json \
  --repo-path /path/to/pandacode-extended

# 6. Inspect immutable Git objects at the captured SHA.
python scripts/pr_audit.py inspect \
  --source audits/pr154-a/source.json \
  --requirements audits/pr154-a/requirements.json \
  --checks audits/issue148-checks.json \
  --repo-path /path/to/pandacode-extended \
  --out audits/pr154-a/evidence.json

# 7. Deterministic calculation and byte-exact verification.
python scripts/pr_audit.py score \
  --source audits/pr154-a/source.json \
  --requirements audits/pr154-a/requirements.json \
  --checks audits/issue148-checks.json \
  --evidence audits/pr154-a/evidence.json \
  --out audits/pr154-a/output

python scripts/pr_audit.py verify \
  --source audits/pr154-a/source.json \
  --requirements audits/pr154-a/requirements.json \
  --checks audits/issue148-checks.json \
  --evidence audits/pr154-a/evidence.json \
  --report-json audits/pr154-a/output/report.json \
  --report-md audits/pr154-a/output/report.md
```

**Windows:** Run the same commands in PowerShell, placing each command on one line (or using PowerShell's backtick continuation); replace `/path/to/pandacode-extended` with `C:\work\pandacode-extended`. Do not type shell `\` line continuations into PowerShell.

The local repository must contain the SHA captured from GitHub. If missing, fetch the PR ref read-only from GitHub into that local repository, e.g. `git -C C:\work\pandacode-extended fetch origin pull/154/head`.

### Missing checkout or executable test evidence

Do not create an empty plan and call the resulting 0% an audit. The `preflight` gate fails with:

- `NO_VERIFICATION_PLAN`: no assertions were authored.
- `INCOMPLETE_VERIFICATION_PLAN`: some applicable criteria have no check; add checks, justified NOT_APPLICABLE exclusions, or use `--allow-partial` only for a clearly incomplete diagnostic.
- `NO_AUDIT_EVIDENCE`: no pinned Git object and no executed, frozen test receipts.

Try a **bounded, read-only** Git fetch into a disposable repository before giving up on source inspection. If the environment cannot obtain a Git checkout, use the authorized GitHub connector to read the **entire issue and comments**, current PR metadata, implementation (including code outside the diff), focused tests and exact-SHA Actions logs. Produce a source-grounded, *qualitative* implementation assessment and a gap list. Do **not** invent 0%, a completion percentage, a fake report, or test receipts from CI log summaries. Green CI is only evidence that the executed jobs passed.

`capture --from-json` marks the issue's completeness unverified, because an offline JSON file can be a truncated excerpt. A manually constructed `source.json` with only REQ/AC lines is not a complete normative snapshot. Only a live paginated `gh api` capture marks comment pagination as verified. For connected GitHub data, explicitly check full content, provenance, exact SHA and any unstructured normative amendments before claiming known-scope completeness.

### Evidence plan example

`init-checks` creates one object per extracted criterion with empty checks and `proof_policy: runtime`. Add checks like the following **inside** the entry for a real requirement, without removing IDs or changing `requirements_digest`:

```json
{
  "weight": 1,
  "proof_policy": "runtime",
  "checks": [
    {"id": "implementation", "kind": "contains", "path": "src/feature.py", "text": "def execute_feature("},
    {"id": "acceptance-test", "kind": "test", "argv": ["python", "-m", "unittest", "tests.test_feature"], "timeout_seconds": 120}
  ]
}
```

The `contains` check by itself yields `PARTIAL` under runtime policy. The test check is `NOT_RUN` until a test receipt is produced. Prefer assertions that discriminate correct and incorrect behavior, not a generic `npm test` unrelated to the criterion. `path_exists` and `not_contains` are also supported.

For an **inherently static** requirement only (e.g. a config file must exist), set `"proof_policy":"static"` and declare objective static checks. Avoid setting runtime requirements to static merely to make them pass. To exclude a criterion, set `"not_applicable":true`, `"reason":"...specific grounded rationale..."` and clear its checks.

### Optional: run targeted tests (explicit authorization)

Test commands in the plan may execute arbitrary code from the repository. Use a **clean disposable checkout** at the captured HEAD. There is no automatic test execution from a GitHub issue or PR.

```bash
python scripts/pr_audit.py run-tests \
  --source audits/pr154-a/source.json \
  --requirements audits/pr154-a/requirements.json \
  --checks audits/issue148-checks.json \
  --repo-path /path/to/clean-disposable-checkout \
  --execute --out audits/pr154-a/executions.json
```

Then pass `--executions audits/pr154-a/executions.json` to `inspect` **before** creating `evidence.json`. If a frozen `evidence.json` already exists, use a new output directory. For accurate evidence receipts, the test command must return the correct exit status and checkout must remain clean. Tests that create build caches or reports in the checkout may be blocked by that cleanliness gate; use a disposable test environment and output paths outside the checkout.

### Compare two PRs or successive commits

1. Capture each candidate into a different directory (`pr154-a`, `pr155-a`).
2. Reuse the **same** `requirements.json` content and `checks.json` contract (same hashes) when the normative issue hasn't changed. Generate evidence/results for each SHA.
3. Compare outputs:

```bash
python scripts/pr_audit.py compare \
  --left audits/pr154-a/output/report.json \
  --right audits/pr155-a/output/report.json
```

A changed spec or check plan blocks direct comparison; intentionally rebaseline both candidates under one agreed contract.

### Offline fixture mode

With a local source JSON object containing `repository`, `pull_request`, `issue` and `issue.comments`, capture without network:

```bash
python scripts/pr_audit.py capture --from-json source-input.json --out audits/offline
```

Required source fields: `repository` (`owner/repo`), `pull_request.number`, `pull_request.head_sha` and `.base_sha` (full 40-character SHA), `issue.number`; optional fields include title/body, URL, `pull_request.files`, `issue.comments` (each with stable `id` and `body`), `spec_files` (`name`, `body`). Live capture uses read-only `gh api` endpoints with pagination and checks for source changes during capture.

### Verify evidence against Git

```bash
python scripts/pr_audit.py verify-evidence \
  --source audits/pr154-a/source.json \
  --requirements audits/pr154-a/requirements.json \
  --checks audits/issue148-checks.json \
  --repo-path /path/to/pandacode-extended \
  --evidence audits/pr154-a/evidence.json
```

Add `--executions` when the evidence contains test results. The command re-inspects all static checks and validates that the frozen result matches. `verify` recomputes the score and checks output bytes. These are consistency checks, not cryptographic source authentication.

## Design and limitations

- The numeric output is a **verified evidence floor**, not an implementation-completion estimate. It is `null`/N/A if no check ran, if the plan is incomplete, or if no applicable criterion achieved a conclusive `PASS` or `FAIL` despite preliminary probes. A 0% floor is possible only if a fully mapped plan has conclusive evaluated criteria and none passed. `assessment_state` is `NOT_ASSESSED`, `INCOMPLETE_PLAN`, `PARTIALLY_ASSESSED` or `EVALUATED_KNOWN_SCOPE`.
- The report separately exposes `acceptance_criteria` and `parent_requirements` groups. The combined all-explicit count may overlap (e.g. 40 AC + 14 parent REQ), so do **not** report that combined ratio as feature completion.
- A separate metric reports percent of declared checks passing; when none ran, it is N/A. Neither code length nor checkboxes drive these values.
- `PARTIAL`, `FAIL`, `UNVERIFIED`, and `NOT_APPLICABLE` remain distinct; unresolved criteria appear in `report.md` with check-level detail.
- Extraction recognizes explicit `REQ-01`, `AC-01`, and checkboxes inside acceptance headings. Unstructured prose or requirements spanning multiple lines need a structured spec before a comprehensive assessment. Duplicated IDs with conflicting meaning abort extraction.
- All issue comments are captured, but comments without extractable criteria produce a warning. The tool does not decide which conversational comments are normative.
- The same canonical inputs yield byte-identical `report.json` and `report.md`. Re-running tests or changing evidence creates new observations, not a nondeterministic replay.
- GitHub capture is best-effort consistent at API request boundaries, not an atomic GitHub transaction.
- A passing test receipt demonstrates the declared command exited as expected at the pinned SHA; it does not independently prove assertions adequately cover the requirement.
- GitHub capture is not exercised against a live repository in the bundled offline test suite; it is tested through a simulated `gh api` client.
- A GitHub connector source/CI inspection can support a strong qualitative review while the CLI is unable to score; it is **not** a substitute for verified local Git objects or genuine runtime receipts in deterministic numeric scoring.

## Self-tests

```bash
python -m unittest discover -s tests -v
```

All scripts are read-only with respect to GitHub and the target repository except for **explicit test command execution**, which may write local files. Script outputs are immutable by default: if the requested output exists with different bytes, the tool refuses to overwrite it.
