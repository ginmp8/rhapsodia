# External Tool Evidence

Use this reference when the review consumes SARIF, SAST, SCA, secret scanners, linters, dependency scanners, IaC scanners, code-quality tools, or other analyzer output.

## Core rule

`tool result != confirmed finding`

A result produced outside this review starts as `supplied` evidence unless the reviewer executes the tool under a captured identity/environment and inspects the result. Even executed scanner output proves that the tool emitted a result; it does not by itself prove the underlying security conclusion.

## Normalize evidence

Preserve, when available:

- evidence id;
- tool name and tool version;
- source format/version, such as `SARIF-2.1.0`;
- rule/query id and rule version;
- stable result fingerprint or normalized location fingerprint;
- reported severity/level without converting it to review severity;
- file/object/URI and bounded location;
- result/message summary with secrets redacted;
- evidence status;
- whether the reviewer independently verified the underlying behavior;
- target revision/artifact identity the tool result belongs to.

SARIF is a preferred interchange format when supplied because it can carry standardized tool/result metadata, but the skill must also accept equivalent structured or textual evidence.

## Correlation and deduplication

1. Group tool alerts by target identity first; do not mix results from different revisions.
2. Normalize subject/location and rule metadata.
3. Inspect the target behavior or data flow.
4. Deduplicate alerts that share the same root-cause fingerprint, affected subject, failure mechanism, and material impact.
5. Keep distinct findings when one alert reveals materially different causes or impacts.
6. Preserve contributing tool evidence on the resulting finding rather than inflating finding count.

Do not count agreement between two scanners as independent confirmation when both derive from the same rule family, database, or static pattern. Treat correlation strength separately from source count.

## Severity discipline

Never inherit `critical`, `high`, or another tool level directly into `BLOCKER`/`MAJOR`. Re-evaluate severity from target evidence, exploit/failure path, changed-path relevance, exposure, data/side-effect impact, and confidence. A probable secret or known exploitable dependency can still become a blocker, but because target evidence supports it, not because the scanner label says so.

## False positives and unresolved results

- Confirmed false positive: record the rejection rationale and the target/tool identity.
- Plausible result with missing context: use `QUESTION` or a validation gap.
- Result whose relevant source is inaccessible: `blocked` or `supplied`, not `measured`.
- Secret-like result: never echo the full value; mask evidence and recommend rotation/revocation when exposure is credible.

## Research basis

SARIF 2.1.0 OASIS Standard provides the common interchange model. Evidence status, finding deduplication, severity, and redaction remain Bug Security Hunter contracts rather than delegated scanner authority.
