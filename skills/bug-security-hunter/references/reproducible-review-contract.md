# Reproducible Review Contract

Use this contract for every substantive review. It constrains process, evidence, severity, ordering, and closure without pretending that security or correctness judgment is fully deterministic.

## 1. Review identity

Record the strongest available identity for the reviewed target before drawing conclusions:

- target kind: PR, diff, repository area, flow, incident, config, migration, or infrastructure change;
- source identity: repository plus revision/commit when available, or supplied artifact identity;
- reviewed paths/ranges and excluded paths;
- selected mode;
- language/framework only when evidenced by the target;
- environment/version details when they materially change behavior;
- assumptions and unresolved context.

When a repository revision is supplied and tooling permits it, prefer immutable revision bytes over a mutable working tree for evidence tied to that revision. If only mutable files are available, say so.

## 2. Separate evidence status from confidence

Do not use one label for both source strength and conclusion confidence.

### Evidence status

Use exactly one primary status for each material finding or gap:

- `measured`: produced by an executed command, test, scan, trace query, replay, benchmark, or other observed runtime validation;
- `observed`: directly visible in inspected source, diff, config, migration, log, or supplied artifact;
- `supplied`: asserted in user-provided text or external result that was not independently reproduced;
- `inferred`: derived from observed/supplied evidence but not directly demonstrated;
- `planned`: validation or test proposed but not executed;
- `blocked`: relevant evidence could not be obtained;
- `out-of-scope`: intentionally excluded from the declared review surface.

Never describe `planned`, `blocked`, or `supplied` evidence as measured. A static code read is `observed`, not `measured`.

### Confidence

Use one of:

- `confirmed`: the failure/control gap is directly established for the stated scope;
- `likely`: evidence strongly supports the conclusion but one material confirmation point is missing;
- `needs-verification`: the hypothesis can change the review decision but evidence is insufficient;
- `not-applicable`: only for dimensions where confidence is not meaningful.

A `needs-verification` item is normally a `QUESTION` or validation gap, not a confirmed finding.

## 3. Canonical finding record

Every material finding must map to this logical record even when the user-facing answer is Markdown:

```text
finding_id
category
subject/location
severity
confidence
evidence_status
evidence_refs[]
trigger_or_condition
problem
impact
severity_rationale
smallest_fix
validation
blocks_merge
expected_treatment
fingerprint
```

`finding_id` must be unique inside the review. Prefer deterministic IDs such as `BSH-001`, assigned after final sorting.

### Finding fingerprint and deduplication

Create a semantic fingerprint from:

`root cause + affected subject + failure/abuse mechanism + material impact`

Merge two observations into one finding when they share that fingerprint. Keep multiple evidence references under the same finding. Do not create separate findings merely because the same root cause appears in multiple lines or symptoms.

Keep findings separate when the root cause, affected security boundary, required fix, or material impact differs.

## 4. Severity contract

Severity remains judgment, but use stable floors and tie-breakers.

### Hard floors

Use `BLOCKER` when the inspected evidence establishes or strongly supports any of these on the changed/reviewed path and there is no demonstrated mitigation:

- authorization bypass or tenant/resource isolation break enabling unauthorized state/data access;
- credible real credential/private-key/token exposure requiring rotation or revocation;
- destructive data loss/corruption or migration incompatibility with no safe rollout/recovery path;
- remote code execution, privilege escalation, or equivalent severe compromise path;
- duplicate irreversible financial/legal/security-sensitive side effect caused by retry/replay/concurrency;
- broken external contract or production-failure path that makes the change unsafe to release;
- unrecoverable rollback/forward-only failure for a high-impact change.

Use `MAJOR` for material correctness, security, reliability, contract, migration, or operational risk that should be fixed before merge unless explicitly accepted and that does not meet a `BLOCKER` floor.

Use `MINOR` for bounded non-critical risk or missing validation/observability that does not by itself make the change unsafe.

Use `NIT` only for cosmetic/readability/local-consistency issues. Never classify security, data-integrity, concurrency, reliability, or deployment risk as `NIT`.

Use `QUESTION` when missing evidence can materially change severity or the merge decision.

### Tie-breakers

When two severities seem plausible:

1. apply any hard floor first;
2. prefer concrete demonstrated impact over hypothetical blast radius;
3. if a material confirmation point is missing, use `QUESTION` or `needs-verification` instead of inflating severity;
4. do not reduce severity because a future issue exists;
5. risk acceptance changes treatment/verdict, not the technical severity itself.

## 5. Deterministic ordering

Sort user-facing findings by:

1. severity rank: `BLOCKER`, `MAJOR`, `MINOR`, `NIT`, `QUESTION`;
2. merge-blocking items before non-blocking items within the same severity;
3. category priority: authorization/data exposure, data loss/corruption, irreversible side effects, contracts/migrations, reliability/concurrency, performance, observability, maintainability/style;
4. normalized subject/location;
5. stable fingerprint.

Assign sequential `finding_id` values only after sorting. This reduces order drift between equivalent reviews.

## 6. Hypothesis budget and stop rules

Do not turn bug hunting into random search.

- Generate at most eight open hypotheses in one analysis pass unless separate evidence supports additional `BLOCKER`/`MAJOR` candidates.
- Prioritize by severity floor potential, evidence availability, changed-path relevance, and falsifiability.
- Validate the highest-value hypothesis first when execution is requested.
- Reject or merge duplicate hypotheses using the same fingerprint rule as findings.
- After two consecutive validation attempts on the same hypothesis produce no new evidence, stop that branch unless the user supplies new evidence or a different test can materially discriminate the outcome.
- Convert a hypothesis to a finding only when evidence meets the finding quality bar.

## 7. Verdict derivation for PRs

Derive the PR verdict from the final finding/gap set after deduplication:

1. `CHANGES_REQUESTED` if any unresolved `BLOCKER` exists.
2. `CHANGES_REQUESTED` if any unresolved `MAJOR` is marked `blocks_merge=true`.
3. `NEEDS_MORE_CONTEXT` if essential context for authz, data integrity, destructive migration, compatibility, or irreversible operational behavior is `blocked` or `needs-verification` and no stronger blocking finding already determines the verdict.
4. `APPROVED_WITH_COMMENTS` if only non-blocking `MINOR`/`NIT` findings or explicitly accepted non-blocking `MAJOR` items remain and required context is sufficient.
5. `APPROVED` only when no material finding remains and validation/evidence is adequate for the declared scope.

Do not treat "no finding observed" as proof of safety. Approval is limited to the inspected scope and available evidence.

## 8. Validation claims

Keep these distinct:

- source inspection: `observed`;
- executed test/scan/build/replay: `measured`;
- user-provided test result: `supplied`;
- suggested check: `planned`;
- inaccessible check: `blocked`.

Never state that a test, scan, exploit, replay, or benchmark passed unless it actually ran or the result is clearly attributed as supplied.

## 9. Closure and coverage

A substantive review closes only when:

- every supplied artifact in scope is inspected or explicitly excluded;
- every `BLOCKER`/`MAJOR` hypothesis is a finding, rejected with evidence, merged as duplicate, or named as a validation gap;
- findings are deduplicated and sorted deterministically;
- required verdict fields are internally consistent;
- uninspected surfaces and blocked evidence are explicit;
- the next action is concrete;
- no absolute "bug-free" or "secure" guarantee is made.

## 10. Machine-readable receipt

When the user requests a durable audit, automation, comparison, or machine-readable result, emit a JSON receipt conforming to `schemas/review-receipt.schema.json` and validate it with:

```text
python scripts/validate_review_receipt.py <receipt.json>
```

The receipt is an evidence record, not proof that the review conclusion is objectively correct.

## 11. Baseline/candidate comparisons

When comparing two versions of code, configuration, architecture, or a skill/package:

- use the same review mode, scope, evidence set, and rubric for both arms;
- pin or snapshot target identities when possible;
- do not change severity rules or acceptance criteria after seeing one arm's result;
- separate structural/package validity from behavioral/runtime evidence;
- do not claim improvement from a static rubric change alone.
