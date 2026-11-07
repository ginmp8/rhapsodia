# Review readiness and decision guide

## At a Glance

- **Purpose:** Govern initial and repeated Archify PR reviews using independently assessed value, cost, impact and evidence.
- **Load when:** Review is requested for an Archify issue, PR, source change, proposal or revised PR head.
- **Decision impact:** Determines when review should proceed, defer, ask for evidence or block; keeps evaluation separate from merge authority.

## Contents

- Readiness gate
- Investigate and verify
- Decision language
- Re-review and integration boundary
- Primary sources

## Readiness gate

Determine the target repository and actual branches first. For the upstream Archify contribution process, functional changes require a related issue and explicit maintainer agreement on problem, value and scope before substantial implementation or a formal PR. Purely mechanical documentation corrections can proceed directly. Reuse existing issue decisions and discussions; an issue URL without scope agreement is not sufficient.

Every PR must disclose whether AI assistance was used; when used, identify tools, model if known and affected work. Human contributors remain accountable and must understand and explain the solution. Do not assume an AI contribution is low quality based on writing style; assess actual evidence.

If required agreement is missing, defer or close/defer review with a specific path back through an issue. If critical evidence is missing, request the **smallest discriminating check** and review again after it is supplied; do not reconstruct unaffected test suites by default.

## Investigate and verify

Pin base/head revisions and identify what currently happens. Separate reported harm from proposed implementation. Evaluate Value, Cost and Impact together and favor a smaller mechanism when equivalent.

Check impact across callers, submodes and documentation/schema consumers. For shared changes, inspect fixed examples under base and candidate and relevant failure/compatibility cases. Reused CI receipts must match the reviewed commit, inputs and coverage. Distinguish machine checks, real-browser evidence and human perceptual review; screenshot differences are changes, not quality scores.

Generated snapshots and adjusted golden files do not themselves prove compatibility. For generation-comparison claims, assess independent authoring outcomes and representative real-repository artifacts, not only synthetic render success or route length. Treat unverified risk as a question, not a reproduced defect.

## Decision language

- **Blocking defect:** verified trigger and unacceptable outcome; identify failing requirement and actionable correction.
- **Required evidence or scope decision:** material uncertainty that can change acceptance; state minimal required proof or decision.
- **Suggestion:** useful nonblocking improvement outside agreed acceptance criteria.
- **Ready:** scope delivered, relevant evidence sufficient and no acceptance blockers remain.

Lead with the decision, consolidate related findings in the first substantive review, and exclude unrelated feature requests from the blocking scope. Review bot findings independently before forwarding them.

## Re-review and integration boundary

Compare against the last reviewed candidate head and evaluate any changes to the base that invalidate evidence. Avoid duplicating prior analysis when inputs, contracts and required checks are unchanged. Review acceptance does **not** authorize GitHub approval, merge, branch mutation, release tagging or publication.

## Primary sources

- [Archify REVIEWING.md at pinned fork revision](https://github.com/ginmp8/archify/blob/a4065941f12be7967436261d9934784e381d423c/REVIEWING.md)
- [Archify current REVIEWING.md](https://github.com/ginmp8/archify/blob/main/REVIEWING.md)
- [Archify CONTRIBUTING.md](https://github.com/ginmp8/archify/blob/main/CONTRIBUTING.md)
