# Canonical Governance And Projections

Nomia keeps one canonical governance truth per governed item and generates human or external views from it.

## Canonical Source Rule

- Before a Mago spec identity exists, the canonical item is the matching `roadmap.yaml` feature entry.
- After an externally sourced `spec_id` is accepted, `ops.yaml` under the spec folder becomes canonical for delivery governance. The roadmap entry retains only roadmap placement and a reference to the spec; repeated delivery facts are generated projections, not separately maintained truth.
- `status.md`, `stakeholder-brief.md`, `replanning.md`, `portfolio.md`, `release-notes.md`, `internal-notes.md`, and `feature-report.md` are human-facing projections. Their source reference and generation timestamp must be visible when generated.
- `portfolio.yaml` and `roadmap.yaml` remain canonical only for their board-level aggregation or pre-spec scope. They must not override fresher spec-scoped `ops.yaml` facts.

## Minimal Logical Record

The canonical logical record covers:

- request: title, rationale/context, requester, requested date, source;
- ownership: owner, backup owner, stakeholders, decision maker;
- priority and target date;
- governance profile, lifecycle stage, and governance status;
- separate planning, execution, validation, and release statuses;
- risks, blockers, dependencies, and accepted business risk;
- decision state and material change history;
- Mago handoff and Magia evidence references;
- closure or release state;
- fact-level provenance, actor, timestamps, freshness, and conflicts.

Existing `ops.yaml` fields remain valid. New sections are optional for legacy records but required when the corresponding fact is asserted:

```yaml
governance:
  profile: quick|standard|governed|unknown
  lifecycle: intake|triage|commit|track|decide|close|unknown
  status: intake|triage|planned|ready|in_progress|blocked|validating|releasable|released|closed|canceled|superseded|unknown
technical_state:
  planning: {state: unknown, source: null, observed_at: null}
  execution: {state: unknown, source: null, observed_at: null}
  validation: {state: unknown, source: null, observed_at: null}
release:
  state: unknown
  released_at: null
  evidence: []
dependencies: []
decision:
  state: unknown
  current: null
  evidence: []
handoffs:
  mago: {state: unknown, source: null, observed_at: null}
  magia: {state: unknown, source: null, observed_at: null}
provenance:
  updated_at: null
  facts: {}
  changes: []
```

Nomia never invents missing sections or upgrades unknown technical state. Technical values are valid only with attributed Mago or Magia evidence.

## Deterministic Human Views

Use `scripts/project_governance_views.py` with one canonical YAML source. It emits:

- `one-line`: state, owner, target, top blocker/risk, and unknown/stale marker;
- `operational`: current facts, next governance action, blockers, dependencies, and evidence;
- `stakeholder`: outcome, timing, impact, decision needed, and communication risks;
- `executive`: commitment, confidence, material risk, decision, and release/closure evidence;
- `audit`: canonical values, provenance, changes, conflicts, and generation metadata.

A projection must never state released, validated, implemented, or complete unless the corresponding attributed evidence is present and current. Unknown and stale facts are displayed, not hidden.

## Public Adapters

Adapters are generated and non-authoritative. They may map to lightweight proposals, roadmap items, status reports, decision logs, release-note inputs, Spec Kit references, OpenSpec references, or Kiro references. Every adapter includes:

- `authority: non_authoritative_projection`;
- canonical source and generation time;
- mapped fields;
- `lossy_fields` for every canonical value without an external equivalent;
- `unknown_fields` and `stale_fields`;
- no implementation tasks, architecture, or technical approval authored by Nomia.

External formats never become canonical and must not be imported as current volatile truth without field-level provenance and conflict review.
