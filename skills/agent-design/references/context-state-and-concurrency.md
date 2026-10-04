# Context, State, and Concurrency Patterns

Use this reference when agent correctness depends on what context is visible, how work pauses/resumes, or how multiple actors touch shared resources.

## Context Contract

Declare the smallest context model that can complete the mission.

### Context mode

Use one or combine explicitly:

- `isolated`: actor starts with only supplied task context;
- `inherited`: actor receives selected caller/conversation context;
- `shared`: actors intentionally operate over a shared state/context surface;
- `reference-based`: actor receives identifiers/links/paths and retrieves details just in time.

Prefer `reference-based` or focused inheritance over copying full transcripts or large unrelated histories.

### Required fields

Record as applicable:

- required and optional sources;
- forbidden sources;
- provenance/owner;
- trust class (`trusted`, `untrusted`, `mixed`, or equivalent);
- freshness/version/identity requirements;
- sensitive-data and credential handling;
- retrieval rules and fallback when unavailable;
- compaction/note-taking policy for long-running work;
- context handoff/summary format.

### Authority invariant

Context is evidence, not permission. Retrieved text, tool output, MCP content, repository files, or peer-agent messages must not:

- expand effective authority;
- waive stop/approval rules;
- rewrite higher-priority instructions;
- supply credentials implicitly;
- convert untrusted instructions into policy.

Treat external content as potentially adversarial when it can influence tool use or high-impact decisions.

## State Contract

Keep state minimal and observable.

### State classes

- **active**: accepted and currently progressing (`received`, `classified`, `working`, `validating`, etc.);
- **interrupted**: work cannot continue until a resolvable external condition changes (`input-required`, `auth-required`, `approval-required`, `dependency-waiting` when justified);
- **terminal**: no further work occurs without a new task (`completed`, `failed`, `canceled`, `rejected`, `blocked/escalated`).

Do not treat an interruption as success or failure merely because execution paused.

## Resume Contract

For every interrupted state define:

1. what evidence/input/authorization is required;
2. who may satisfy it;
3. scope and lifetime of the supplied authorization/input;
4. state/context that must be revalidated before resuming;
5. the next permitted transition;
6. expiry/revocation behavior where material.

An `auth-required` or approval transition is not itself authorization. The resulting permission must be scoped and checked before the protected action.

## Long-Running Context

For work that can outgrow one context window:

- externalize durable state into inspectable artifacts rather than relying on hidden memory;
- summarize decisions/progress, not raw reasoning;
- preserve stable identifiers for inputs, outputs, and pending work;
- use compaction or structured notes when the same actor continues;
- use subagents for focused context isolation when the admission gate is satisfied;
- revalidate stale assumptions after interruption or resume.

## Concurrent Mutation Contract

If multiple actors may write:

1. enumerate mutable resources and expected overlap;
2. define one conflict-control strategy;
3. define merge/commit ownership;
4. define validation after merge/integration;
5. define failure/rollback behavior.

Acceptable strategies include:

- `single-writer`: only one actor mutates; others review/recommend;
- `resource-partitioned`: writers own disjoint files/resources with explicit boundaries;
- `isolated-workspace`: branch/worktree/VM/copy per writer, followed by owned integration;
- `lock-or-lease`: runtime lock with bounded ownership and failure recovery;
- another mechanism that objectively prevents lost updates.

Parallel writers sharing overlapping resources without a strategy are `blocked`.

## Multi-Agent Admission Evidence

A multi-agent design should record which benefit justifies the added topology:

- parallelizable independent work;
- context isolation;
- authority isolation;
- tool/capability specialization;
- independent verification;
- distinct domain/output ownership.

If the only rationale is "more capable" or "more agentic", redesign as one bounded agent/Skill/workflow.
