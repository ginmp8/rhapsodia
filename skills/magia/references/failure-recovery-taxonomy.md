# Failure and Recovery Taxonomy

Classify the primary blocker before choosing repair, retry, rollback, stop, or handoff. Report category, evidence, current safe state, permitted action, and next required evidence.

| Category | Meaning | MAGIA action |
|---|---|---|
| `input_blocker` | required repository, scope, task, path, or validation target is missing | inspect available evidence; stop before unsafe mutation; request or identify the concrete input |
| `repository_drift` | tracked source or dependency assumptions changed after checkpoint | stop; re-inspect; create a new checkpoint or run; never resume blindly |
| `reproducibility_failure` | the reported behavior cannot be reproduced with available evidence | narrow the reproduction, preserve observations, avoid speculative patching |
| `implementation_failure` | bounded code/config change does not achieve intended behavior | repair the smallest causal change or revert the candidate |
| `test_failure` | an executed check fails | diagnose, repair in scope, rerun the same check, retain failure history |
| `environment_failure` | runtime, permission, dependency, service, or tool environment prevents evidence | retry only after environment evidence changes; do not fabricate a code fix |
| `dependency_failure` | upstream/downstream package, repository, service, or contract is unavailable/incompatible | preserve compatibility, stop at checkpoint, repair locally only when ownership permits |
| `contract_conflict` | code, consumer, API, event, schema, or file contracts disagree | stop breaking rollout; use compatibility strategy or hand off material contract change |
| `planning_gap` | approved intent, task, acceptance criteria, architecture, or sequence must change | create technical-gap evidence and hand off to Mago; do not rewrite planning intent |
| `governance_gap` | owner, due date, accepted risk, stakeholder state, release posture, or priority must change | preserve execution evidence and hand off to nomia; do not make the governance decision |
| `security_stop` | secrets, authorization, PII, unsafe permission, or serious security risk blocks work | fail closed, redact values, preserve evidence, recommend rotation or authorized remediation |
| `rollback_failure` | reversal failed or cannot restore a safe compatible state | stop; report side effects; prefer authorized forward fix or escalation; never mark rolled back |

## Recovery Rules

- **repair** only within approved product intent and writable scope;
- **retry** only when the failed step is unchanged and tracked assumptions still match;
- **rollback** only with a defined target state and evidence;
- **stop** when continuing increases uncertainty, exposure, or partial-state risk;
- **handoff** when the decision belongs to planning or governance authority.

Secondary failures may be recorded, but one primary category should drive the immediate action. A failure response is concise: category, evidence, safe partial work, permitted next action, and residual risk.
