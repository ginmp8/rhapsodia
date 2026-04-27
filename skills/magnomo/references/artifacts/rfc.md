# RFC Artifacts

## rfc-proposals.md

Mutable governance proposal log owned by Magnomo. Use for material decisions that are not decided yet.

Required sections:

- `# RFC Proposals`
- `## Entries`

Use one `### <proposal_id> - Title` heading per RFC entry. `proposal_id` must be lowercase hyphen-case and stable across edits.

Each RFC entry must include these labels in order:

- `Status`
- `Impact`
- `Driver`
- `Approvers`
- `Contributors`
- `Informed`
- `Due Date`
- `Background`
- `Assumptions`
- `Decision Criteria`
- `Options`
- `Recommendation`
- `Outcome`
- `Links`

Quality rules:

- Define decision criteria before options.
- Include at least two real options; include status quo or `Do Nothing` when relevant.
- Include assumptions with confidence and invalidation triggers when known.
- Keep `Outcome: pending` until the decision is made.
- Do not include implementation task decomposition, acceptance criteria, code instructions, or Magia execution evidence.

