# Deterministic PR Audit v0.4.0

An evidence-backed, standard-library Python skill for auditing a GitHub PR against the full linked issue, comments and acceptance criteria. It creates an on-disk artifact **even when no source checkout or runtime test is available**. It never equates missing evidence to missing implementation. **The main metric is now code-delivery progress independent of CI.**

## At a Glance

- **Purpose:** Reproduce evidence-bound PR-vs-spec implementation grades independently of CI and preserve the original runnable-test evidence floor as a separate signal.
- **Load when:** Auditing a code PR, preparing its source review ledger, running the CLI, comparing candidate HEADs, or packaging the skill.
- **Decision impact:** An analyst must trace source code before grading; frozen AC statuses and Git blob references control the grade, while CI cannot change it. Missing proof remains unknown with disclosed coverage and bounds.

## Contents

- One-shot audit: default
- Primary: deterministic implementation progress from source code (CI-independent)
- Separate optional executable verification (not implementation grade)
- Scoring model and boundaries
- Testing and packaging

## One-shot audit: default

```bash
# Authenticated gh API capture, no local Git checkout required for a diagnostic bundle
python scripts/audit_bundle.py --repo ginmp8/pandacode-extended --pr 155 --issue 147 --out /mnt/data/pr155-audit
# Deliver /mnt/data/pr155-audit/audit-bundle.zip
```

When GitHub is accessible only through a connector, collect PR and normative issue **in full** and save an offline JSON source input. Preserve the exact head/base 40-character SHA, every issue comment with stable ID, changed paths and the full issue body. An offline capture is intentionally marked completeness-unverified:

```json
{
  "repository": "owner/repo",
  "pull_request": {
    "number": 155,
    "title": "PR title",
    "body": "Full PR body",
    "head_sha": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "base_sha": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
    "files": ["src/path.py"]
  },
  "issue": {
    "number": 147,
    "title": "Normative issue title",
    "body": "Full normative issue body with explicit AC-01 etc.",
    "comments": [{"id": 123456, "body": "Full issue comment"}]
  }
}
```

The example SHAs are placeholders, not evidence. Replace every field with observed GitHub data. Then:

```bash
python scripts/audit_bundle.py --from-json source-input.json --out /mnt/data/pr155-audit
```

The output contains the original verification artifacts plus `implementation-review.json`, `implementation-grade.json`, `implementation-grade.md`, `manifest.json`, `README.txt`, and `audit-bundle.zip` (and `code-snapshots.json` when supplied). **No checks or no observed evidence is `NOT_ASSESSED` with `null` numeric evidence floor**, not 0% implemented. All explicit ACs are included with `UNVERIFIED` as appropriate. `audit-bundle.zip` has deterministic member order, fixed timestamps, and a SHA-256 file inventory for reproducible replay.

## Primary: deterministic implementation progress from source code (CI-independent)

Start with `capture` or a complete connector snapshot and its generated source and requirements files. Scaffold a review ledger; **read the code of the exact HEAD** (including reachable files outside the diff), trace behaviors and fill all ACs with code references:

```bash
python scripts/pr_audit.py init-code-review --source audit/source.json --requirements audit/requirements.json --out audit/implementation-review.json
# Edit every criterion with COMPLETE, PARTIAL, MISSING or UNVERIFIED, an explicit source trace and source evidence.
# Source reference: {"path":"src/handler.py", "blob_sha":"<40-digit Git blob SHA>", "line_start":17,
#                    "line_end":41, "role":"implementation", "claim":"Entry point enforces the guarded transition"}
python scripts/pr_audit.py code-grade --source audit/source.json --requirements audit/requirements.json \
  --review audit/implementation-review.json --repo-path /path/to/repo --out audit/grade-001
python scripts/pr_audit.py verify-code-grade --source audit/source.json --requirements audit/requirements.json \
  --review audit/implementation-review.json --repo-path /path/to/repo \
  --report-json audit/grade-001/implementation-grade.json --report-md audit/grade-001/implementation-grade.md
python scripts/audit_bundle.py --from-json source-input.json --review audit/implementation-review.json \
  --repo-path /path/to/repo --out audit/bundle-001
```

When a checkout is inaccessible, use `--snapshots code-snapshots.json` in place of `--repo-path`. Each snapshot must include the exact frozen `source_digest`, `head_sha` and full `files` list:

```json
{
  "schema": "pr-audit/code-snapshots/v1",
  "source_digest": "<sha256 of canonical source.json>",
  "head_sha": "<40-character PR HEAD>",
  "files": [{"path": "src/handler.py", "blob_sha": "<Git blob SHA>", "content": "<full UTF-8 file at HEAD>"}]
}
```

The code snapshot validates blob integrity, but unlike a local Git object it does not prove remote tree membership; separately attest that the connector fetched it at that HEAD. The scoring model is **one vote per AC**, with no weighting of parent REQs: `COMPLETE=1`, `PARTIAL=0.5`, `MISSING=0`, and `UNVERIFIED=unknown`. The report includes **functional completion**, **development progress**, **reviewed coverage**, and **issue-wide conservative bounds**. An unreviewed criterion cannot be scored as missing. A code path's semantics must be reviewed; correct SHA and lines alone do not make a claim true.

Compare two review reports only when their normative spec and assessed AC scope match:

```bash
python scripts/pr_audit.py compare-code-grade \
  --left first/implementation-grade.json --right second/implementation-grade.json
```

**Important:** An LLM's semantic classification is not inherently deterministic. Reproducibility applies to the exact **frozen adjudication ledger**, source, requirement set and formula. Freeze the same ledger before comparing PRs; reject source/issue drift. Generic CI outcomes do not enter this calculation. For the full scoring contract, see `references/scoring-contract.md`.

## Separate optional executable verification (not implementation grade)

A **separate verified-check score** is defensible only after mapping each applicable requirement to an assertion that meaningfully tests it. The model must not create superficial path/text checks to inflate progress. Tests must be actually executed at a pinned commit with explicit authorization; source text or green generic CI is not enough.

```bash
python scripts/pr_audit.py capture --pr-url https://github.com/owner/repo/pull/155 --issue 147 --out audit/frozen
python scripts/pr_audit.py init-checks --requirements audit/frozen/requirements.json --out audit/checks.json
# Review and populate every applicable AC's checks; prefer targeted native tests.
python scripts/pr_audit.py preflight --source audit/frozen/source.json --requirements audit/frozen/requirements.json --checks audit/checks.json --repo-path /path/to/repo
# After preflight succeeds, build a new versioned bundle with these verified inputs:
python scripts/audit_bundle.py --from-json source-input.json --checks audit/checks.json --repo-path /path/to/repo --out audit/verified-001
python scripts/pr_audit.py verify --source audit/verified-001/source.json --requirements audit/verified-001/requirements.json --checks audit/verified-001/checks.json --evidence audit/verified-001/evidence.json --report-json audit/verified-001/report.json --report-md audit/verified-001/report.md
```

**Important:** the connector-supplied `source-input.json` used for `audit_bundle.py` must describe the *same frozen issue/source* used to create `audit/checks.json`; otherwise digests reject it. Prefer generating the check plan from the bundle's own requirements, then rerunning the bundle:

```bash
cp audit/frozen/requirements.json audit/requirements.json
python scripts/pr_audit.py init-checks --requirements audit/frozen/requirements.json --out audit/checks.json
# Or use /mnt/data/pr155-audit/requirements.json generated by the default bundle.
```

For optional execution receipts, the existing CLI `run-tests --execute` requires a clean disposable checkout pinned to the exact HEAD and an explicit user authorization. Do not run untrusted code from the PR by default. Use `--executions path/to/executions.json` only for receipts generated for the same source, plan and SHA.

## Scoring model and boundaries

| Field | Meaning |
|---|---|
| `assessment_state` | NOT_ASSESSED, INCOMPLETE_PLAN, PARTIALLY_ASSESSED or EVALUATED_KNOWN_SCOPE |
| `completion_verified_pct` | **Verified evidence floor**, not a feature completion estimate; null without adequate checks |
| `completion_possible_upper_pct` | Mathematical upper bound only; not a forecast |
| `acceptance_criteria` | AC-specific denominator and counts |
| `parent_requirements` | Parent REQ summary, excluded from the AC-only headline |
| `capture.issue_completeness` | Completeness of normative issue capture; offline input is not independently attested |

The implementation grade is computed by `implementation_review.py`; the independent check-evidence floor is computed by `audit_core.py`. Both calculators use frozen source observations and deterministic formulas. No numeric score should be invented by the reviewing model. Identical JSON inputs and algorithm produce byte-identical `report.json` and Markdown. Any source, check, evidence or algorithm change is a new evidence version. A passing test receipt only proves the declared command exited as expected; the adequacy of its assertions is reviewed separately.

## Testing and packaging

```bash
python -m unittest discover -s tests -v
python scripts/audit_bundle.py --help
```

Installable ChatGPT archive layout: `deterministic-pr-audit/SKILL.md`, `deterministic-pr-audit/scripts/`, `tests/`, `agents/openai.yaml`, `references/`, and `assets/`. Zip the folder itself, not just its contents. The skill requires Python 3.10+ for CLI use; `gh` is optional with `--from-json` and Git is optional when no static checks are evaluated. No third-party Python dependencies are required.
