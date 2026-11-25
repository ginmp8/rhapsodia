# V3 reproducibility protocol

**Scope:** `frozen-obligation-reconciliation-v3` extends the existing v2 structural evidence gate; the `code-delivery-v1` arithmetic, parent REQ exclusion and CI independence do not change. New substantive audits use v3; existing v1/v2 bundles replay under their own policy. Do not compare grades across policies or different plan identities as development progress.

## 1. Freeze specification scope before candidate adjudication

Capture complete original issue, comments, pinned normative files and canonical requirements. Review all normative prose, applicability, exceptions, linked parent requirements and explicit test obligations. Reuse an already frozen plan with the same requirements/spec digest whenever available. Otherwise prepare `obligation-draft.json` with **every** extracted AC/REQ as a key and a nonempty list of distinct descriptors. Example fragment (illustrative, not evidence):

```json
{"criteria":{"AC-01":[{"kind":"behavior","quote":"The request must preserve the original body.","subject":"original body preservation","polarity":"none"}]}}
```

For actual inputs include all criteria, not just the example. `kind` is `behavior`, `mandatory_test`, `documentation` or `delivery_config`. Quote exact normative text; enumerate distinct mandatory parts without adding optional requirements. Explicit named positive/negative subjects require both polarities. A parent REQ's quote must belong to its linked normative text. The helper checks membership and exact descriptor shape, not semantic exhaustive decomposition. Challenge the draft against the complete specification before freeze.

Run `python scripts/pr_audit.py freeze-obligations --source source.json --requirements requirements.json --draft obligation-draft.json --out obligation-plan.json`. The command writes once and derives stable obligation IDs from criterion identity plus normalized descriptor; candidate HEAD, CI and verdicts are not plan inputs. Preserve the file separately and its digest. Never edit this file or recreate the same plan after viewing code merely to obtain a preferred grade. If the specification or an actual decomposition error requires a change, freeze a new plan, explain the scope change, and re-adjudicate all comparison candidates under that plan.

## 2. Freeze available prior audits and initialize

Search authorized user-supplied reports, current workspace and available task-owned evidence for earlier audits of the same issue/PR/HEAD. Record what was searched and unavailable. Do not assume access to prior chats, files or remote artifacts, and do not retrieve unrelated private artifacts. Do not omit available contrary reports. Run:

```bash
python scripts/pr_audit.py prepare-audit-history --search "Sources actually inspected and unavailable locations" \
  --prior-grade earlier/implementation-grade.json --prior-grade other/implementation-grade.md --out audit-history.json
python scripts/pr_audit.py init-code-review --source source.json --requirements requirements.json \
  --obligation-plan obligation-plan.json --audit-history audit-history.json --out implementation-review.json
```

Repeat `--prior-grade` as needed; omit only when none is available. Full prior JSON is preferred; Markdown inventory is a provisional lead, with no independent normative digest. The history contains the supplied prior report bytes/content and explicit search description; keep evidence private and avoid unnecessary disclosure. The v3 review binds its inventory digest (excluding mutable resolutions) and the separate plan digest. Every obligation is scaffolded UNKNOWN. Keep every descriptor unchanged, including those with unresolved evidence. `validate_scope` rejects omitted, substituted or added descriptors and changed prior inventory. If additional prior reports are discovered, initialize a new review using the same plan and expanded history; transfer only still-supported source judgments, then reconcile. Do not change a bound inventory in place.

## 3. Complete source coverage, challenge, reconcile

Perform a breadth-first source inspection of all criteria, then a focused second pass on remaining UNKNOWN obligations and material counterexamples. Inspect whole relevant flows, tests and known opposing paths rather than repeating descriptions. Missing evidence is UNKNOWN, not missing implementation. Fill the existing v2 `coverage` fields without changing descriptors; use the causal test witnesses and `remaining` format in [adjudication.md](adjudication.md). Follow shared causal paths across every affected criterion, including paths that do not share a citation. Record affirmative and contrary references; do not propagate one defect automatically or erase it because another path succeeds.

Run `code-grade` with the review, plan and history plus exact-SHA Git or snapshots (provisional fallback only when required). The reconciliation section reports:

- `prior_verdict`: same repository/PR/HEAD and matched criterion text, but a different prior/current status. JSON additionally requires matching requirements digest; Markdown remains provisional. A transition from UNKNOWN to known also needs a source explanation; this may be valid new evidence rather than a contradiction.
- `prior_obligation`: differing verdicts inside the same criterion with the same plan identity, even if aggregate status is unchanged.
- `shared_counterexample`: an overlapping pinned blob/line span between a proven gap and an affirmative source reference in a different COMPLETE criterion. This is a bounded discovery heuristic, not a proof that the gap applies. Trace actual reachability, applicability and scope.

The grader records each lead with a deterministic `REC-...` ID bound to the current row digest; changing the row invalidates stale resolutions. Revisit source and revise incorrect judgments. For a lead that remains after correction, make a new copy of the history JSON (preserve `schema`, `search`, `reports` exactly) and set `resolutions` by lead ID, e.g.:

```json
{"REC-<actual lead ID>":{"anchor":"src/handler.py:L17-L41","rationale":"Explain the prior or shared counterexample, the actual applicable input/guard/effect, and why the current verdict is supported by the cited source."}}
```

This is the shape of the `resolutions` object, not a real resolution. Use an exact inspected reference already in the affected criterion's current evidence. The validator requires a current lead, a cited anchor and specific rationale; it cannot independently certify whether prose is true. Recompute in a new output directory; remove stale resolutions only after re-adjudication makes their leads disappear. No automatic verdict changes, majority vote, best-score selection or artificial reconciliation. Keep unresolved leads explicit. Same-HEAD differences reflect evidence/judgment changes, never development progress.

## 4. Report closure separately from delivery

- `UNRECONCILED`: at least one known prior/shared-source lead still needs review. No final score claim; keep diagnostic floor and queue.
- `INCOMPLETE`: unknown criteria or unknown obligations (including inside a PARTIAL criterion) remain. Report coverage, bounds and the unresolved obligation IDs. Continue safe source inspection when possible.
- `PROVISIONAL`: all planned obligations are adjudicated and supplied leads reconciled, but source/spec provenance is not fully independently verified. Show limitations prominently; no claim of verified completeness.
- `REVIEW_COMPLETE`: all planned obligations are adjudicated, supplied leads reconciled, Git commit membership and paginated issue completeness checked. This is an audit-closure label, not a claim of semantic infallibility, implementation completion, CI success or merge readiness. Proven gaps can remain in a complete audit.

All four states preserve unchanged numeric floors, assessed scope, bounds, evidence and ZIP. Never present an incomplete floor as a measured amount of developed code. `compare-code-grade` rejects incomplete/unreconciled v3 reports and same-HEAD differences in aggregate or obligation verdicts; provisional comparisons retain their evidence label. The plan and history are included and hashed in `audit-bundle.zip`. Replay with the same files and `verify-code-grade`. Prior report discovery, complete semantic decomposition, reachability and resolution truth remain analyst responsibilities; this is not a cross-chat persistent registry, trusted timestamp or deterministic semantic oracle.
