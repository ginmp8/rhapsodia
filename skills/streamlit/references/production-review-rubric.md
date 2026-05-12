# Production Review Rubric

Use this rubric when a user asks whether a Streamlit app is ready for team, customer, internal, or public use.

## Scoring model

Do not present a numeric score unless you inspected enough evidence. Use qualitative status when evidence is incomplete.

Statuses:

- `ready`: all required gates passed with evidence.
- `ready with reservations`: no blocking issues, but moderate risks remain.
- `not ready`: one or more blocking gates fail.
- `insufficient evidence`: readiness cannot be judged from available files/context.

## Required gates

### App startup

Evidence:

- app starts locally or in target runtime;
- dependencies install;
- entrypoint is correct;
- Python and Streamlit versions are compatible.

Blocking failures:

- app cannot start;
- missing dependency with no install path;
- import requires unavailable secret at module import time;
- deployment points to wrong file.

### Rerun and state

Evidence:

- key workflows survive widget reruns;
- session keys are initialized;
- callbacks are simple and bounded;
- multipage state is validated.

Blocking failures:

- writes happen repeatedly on rerun;
- user can reach private data by manipulating state/query params;
- workflow loses required state without recovery.

### Data and cache

Evidence:

- expensive reads are cached or intentionally uncached;
- data freshness is explicit;
- cache keys include user/tenant/privacy boundaries;
- writes clear or bypass stale caches.

Blocking failures:

- shared cache leaks user or tenant data;
- query runs unbounded on every interaction;
- SQL injection risk from user input;
- private uploads are stored or logged unexpectedly.

### Security

Evidence:

- secrets are externalized;
- auth model is documented;
- authorization is applied before data retrieval;
- uploads are constrained and validated;
- errors/logs do not expose secrets/private data.

Blocking failures:

- hardcoded real secret;
- unauthenticated private app;
- user can access unauthorized records;
- raw file path input reads arbitrary files;
- unsafe deserialization of uploaded data.

### Deployment

Evidence:

- target platform is named;
- configuration and secrets are supplied by platform;
- network access to data sources is understood;
- file paths are portable;
- logs are accessible.

Blocking failures:

- required local-only files are absent from repo/image;
- secrets missing with no fallback;
- container does not expose/listen on expected port;
- platform cannot reach data source.

### Testing and validation

Evidence:

- static review or AppTest covers main flow;
- smoke test is documented;
- upload and empty-state behavior tested;
- deployment smoke test plan exists.

Blocking failures:

- no validation evidence for a high-risk production claim;
- critical write or auth path untested;
- tests require production secrets.

### UX and operations

Evidence:

- clear page purpose;
- empty/error/loading states;
- data freshness shown;
- high-risk actions require confirmation;
- rollback is known.

Blocking failures:

- app can trigger irreversible writes accidentally;
- user cannot distinguish stale/empty/error state;
- no rollback for risky release.

## Review output

Use this structure:

```markdown
## Verdict
[ready | ready with reservations | not ready | insufficient evidence]

## Evidence inspected
[files, commands, logs, deployment target]

## Blocking findings
[only blockers]

## Non-blocking findings
[high/medium/low]

## Required before production
[ordered fixes]

## Validation plan
[commands and manual checks]
```

## Minimum questions when evidence is missing

Ask only the questions that affect readiness:

1. Where will this run?
2. Who can access it?
3. What data can it show?
4. Where are secrets stored?
5. What is the smoke test?
6. What is the rollback path?
