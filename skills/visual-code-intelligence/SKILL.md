---
name: visual-code-intelligence
description: Create evidence-backed visual explanations of software changes and systems from repositories, PRs, diffs, commits, files, specs, and history. Use when humans need to understand what changed, how code works, why code exists, or when a visual scratchpad would clarify multi-file behavior. Produces semantic change maps plus architecture, sequence, flow, ER/data, state, or timeline views with claim-to-evidence links. Do not use for live agent execution monitoring, generic implementation work, or visual design unrelated to software understanding.
---

# Visual Code Intelligence

## Mission

Transform observable software-work results into concise, visual, evidence-backed explanations for humans. Explain the result, not private chain-of-thought or live agent execution.

## Activation and boundaries

Use this skill when the user wants one or more of these outcomes:
- understand what a change, branch, commit, or PR actually changed;
- understand how a multi-file system, feature, request path, state flow, or data model works;
- understand why code exists using repository/history evidence;
- sketch a focused visual explanation of code that would otherwise become a long textual or ASCII explanation.

Do not use it to implement/fix code, monitor agents in real time, reconstruct hidden reasoning, produce generic project status, or design non-code visuals. If the request is mainly implementation/review-for-defects, route to the appropriate engineering/review skill and use this skill only for the explanatory visualization layer.

## Modes

| Mode | Select when the dominant question is | Required result |
|---|---|---|
| `change-review` | What changed and how does the change fit together? | what/why, semantic file lenses, design view, implementation walkthrough, evidence |
| `system-explanation` | How does this system/flow/component work? | focused architecture/behavior explanation with the smallest useful visual |
| `code-archaeology` | Why does this code exist or how did it evolve? | provenance chain, historical evidence, current-code check, uncertainty |
| `visual-scratchpad` | Can you show/draw this code concept or flow? | one compact explanation and the smallest visual that makes the point |

When multiple modes apply, choose one primary mode by the user's dominant question and compose only the minimum secondary material needed. Do not duplicate the same facts across mode-shaped sections.

## Workflow at a Glance

1. **Resolve scope.** Identify the repository/files/change/history the user means. Prefer immutable commit/PR identities when available; otherwise state the working-tree/current-file scope.
2. **Read before explaining.** Inspect the relevant source, diff, tests, contracts/config, docs, and history that can materially change the explanation. Never infer unseen file content.
3. **Build semantic evidence.** Separate current behavior, requested intent, validation evidence, and historical rationale. Mark unsupported gaps explicitly.
4. **Choose the mode.** Apply the table above. If the choice is materially ambiguous, prefer the narrower mode that answers the user's explicit question; ask only when different modes would change the result substantially.
5. **Normalize the result.** Identify claims, changed-file lenses when applicable, dominant relationship signals, risks/invariants, and evidence locators. For repeatable workflows, represent this as a `visual-code-intelligence/1` visual plan.
6. **Choose visuals deterministically where possible.** Explicit user choice wins. Otherwise use the relationship rules below or `scripts/select_visual.py`; do not pick a diagram by aesthetics alone.
7. **Write for human comprehension.** Lead with the result/shape of the system, then the visual, then the implementation/evidence details. Prefer one strong visual; use a second only when it explains a distinct dimension.
8. **Verify before finalizing.** Re-read the evidence behind every material claim, check that historical explanations still match current code, and remove contradictions or unsupported certainty.
9. **Render portably.** Default to Markdown + Mermaid. Use a richer standalone visual artifact only when explicitly requested and the host supports it. Fall back to structured text when diagram rendering is unavailable.

## Non-negotiable rules

- Current source/config/schema defines current implementation behavior; history explains past intent and must not override current state.
- Never invent line numbers, commit/PR rationale, trace events, requirements, test results, or tool execution.
- Distinguish `observed`, `inferred`, and `historical` claims. Every material claim needs evidence; inferred claims must remain visibly inferential.
- For change reviews, account for every changed file exactly once in a semantic lens. Classify non-implementation noise first, then group implementation by responsibility in reader order.
- Choose sequence for interactions over time; flowchart for branching/retries/control flow; ER/data view for persistent data relationships/read-write shape; state diagram for lifecycle transitions; architecture/component view for dependency structure; timeline for historical evolution; change-map for semantic file responsibilities.
- If several visual types fit, apply explicit request first, then mode-specific rules, then the stable tie-break order in [visual language](references/visual-language.md). Do not force a winner when evidence cannot establish the dominant relationship.
- Use the lowest reliable control layer: scripts/schema for mechanical structure, ordered rules for constrained choices, evidence + rubric for architectural interpretation. Do not fake determinism for subjective judgment.
- Keep the semantic core host-neutral. Describe capabilities, not vendor-private tool names. Missing capabilities degrade output; they never justify fabricated evidence.
- Avoid diagram overload. A visual must answer a concrete reader question; omit it when prose/code is clearer.

## Output contract

- `portable` (default): concise Markdown narrative + Mermaid source/render + evidence locators.
- `rich`: standalone HTML or host-native visual artifact when explicitly requested and supported; semantics must match the portable result.
- `text-fallback`: headings, compact trees/tables, and ordered steps when Mermaid/rendering is unavailable.

## Direct resource map

Load only the branch needed; every required reference is one hop from this file:
- [change review](references/change-review.md) — semantic diff/file lenses and review structure.
- [system explanation](references/system-explanation.md) — architecture and behavior explanation workflow.
- [code archaeology](references/code-archaeology.md) — provenance/history investigation and current-state checks.
- [visual scratchpad](references/visual-scratchpad.md) — compact ad-hoc visual explanations.
- [visual language](references/visual-language.md) — diagram selection, deterministic tie-breaks, density, and composition.
- [evidence model](references/evidence-model.md) — evidence roles, claim classes, precedence, and uncertainty.
- [output contract](references/output-contract.md) — portable/rich/text output shape and audience depth.
- [portability](references/portability.md) — capability detection and host-neutral degradation.

## Deterministic helpers

Use `scripts/select_visual.py` after normalizing relationship signals when a stable diagram choice matters. Use `scripts/validate_visual_plan.py` to validate `visual-code-intelligence/1` plans, claim/evidence integrity, selected visuals, and complete file-lens accounting. These scripts use only Python standard library and are optional when process execution is unavailable; report such gates as `not-run` rather than pretending validation occurred.

The schema is `assets/schemas/visual-plan.schema.json`. The scripts enforce semantic invariants beyond basic JSON shape.

## Finalization gates

Before claiming a result is complete:
- scope/target is explicit enough for the claims made;
- every material claim is evidence-backed and correctly labeled;
- change-review file lenses account for all known changed files exactly once;
- selected diagram(s) match the declared relationship signals or an explicit user request;
- historical rationale has been checked against current code when it is used to explain current behavior;
- no visual adds unsupported entities/relationships merely for completeness;
- output profile degrades honestly when capabilities are missing.

## Examples of activation

- “Review this PR visually and explain the architectural change.”
- “Show me how this request travels through the service and database.”
- “Why does this retry layer exist? Check git history and current code.”
- “Draw the relationship between these handlers, queue, and worker.”

## Stop conditions

Stop or return a bounded partial explanation when required source content is unavailable; target identity is ambiguous enough to change the explanation; historical evidence conflicts materially with current state and cannot be resolved; a requested interactive/rich surface is unavailable and the user rejects portable fallback; or correctness would require inventing evidence.

Non-activation examples: “Implement this endpoint”; “Find every security vulnerability”; “Show me live what the agent is doing”; “Design a marketing infographic.”
