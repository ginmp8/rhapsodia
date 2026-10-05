# System Explanation

## Purpose
Explain how an existing system or flow works using the smallest visual and code evidence that preserves the important control, data, and dependency relationships.

## Workflow
1. Identify the exact reader question and the entry point: request, command, event, UI action, scheduled job, consumer, or data operation.
2. Trace the relevant path through current code/config/schema/tests. Include only components that materially participate.
3. Separate control flow from data shape. Record dominant relationship signals for visual selection.
4. Select one primary visual: sequence, flowchart, state, ER/data, or architecture/component.
5. Explain the path in reader order, linking claims to concrete source locations when the host supports locators.
6. Call out invariants, ownership boundaries, asynchronous handoffs, retries/failure paths, or persistence boundaries only when supported and relevant.
7. Mark architectural interpretations that are not explicitly encoded as `inferred`.

## Scope control
- Prefer a narrow end-to-end slice over a repository-wide diagram.
- Do not include libraries/infrastructure merely because they exist.
- If multiple repositories are required and accessible, name each source boundary. If one is unavailable, show the gap rather than inventing it.
- If one sentence or one code excerpt answers the question, do not add a diagram.
