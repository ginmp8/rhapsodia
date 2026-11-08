# Decision map contract

## Purpose

Define a minimal portable decision map for Wayfinder. It is an index of decisions and evidence, not a competing roadmap, task scheduler or technical plan.

## Load when

Creating, resolving, reconciling or publishing a multi-session decision map.

## Decision impact

Constrains states, dependency closure, claims, scope boundaries and handoffs; avoids fabricated issue links and accidental ownership changes.

## Map format

```markdown
# Decision map: <goal>

## Destination
<explicit objective and completion criterion>

## Owner and source
<user-approved owner, source revision and map path>

## Decisions so far
- <decision title> (`<actual relative path or issue URL>`): <one-line confirmed answer>

## Frontier
- <stable decision ID and exact title; no unresolved blockers>

## Not yet specified
- <known direction without a sufficiently precise question>

## Out of scope
- <excluded work and reason>
```

Each child decision contains `id`, `title`, `type`, `status`, `blocked_by`, `evidence`, `answer` and `owner`. Allowed statuses: `open`, `claimed`, `blocked`, `resolved`, `out-of-scope`.

## Concurrency and evidence

- A decision is frontier-ready only if it is open, unclaimed and every known blocker is resolved.
- Use native tracker dependency/claim relationships only when available and authorized; otherwise use explicit local links and recheck current state before writing.
- A decision is resolved only with its actual answer and a primary evidence pointer or a recorded user decision. Agent recommendations are not acceptance.
- Names and IDs must be real. Do not invent issue numbers or rewrite canonical owner artifacts.
- When a previously resolved answer is contradicted, preserve history and record a supersession; never erase the earlier decision as if it never happened.

Replace each placeholder with a verified real path or URL; create a Markdown link only when its destination exists. Do not treat this example as a link to a bundled asset.
