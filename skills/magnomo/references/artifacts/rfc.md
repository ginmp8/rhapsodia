# RFC Artifacts

Magnomo RFC artifacts are governance proposal logs. They exist to align humans on business/process decisions before acceptance; they are not technical RFCs, TDDs, ADRs, task plans, implementation notes, or validation evidence.

## rfc-proposals.md

Mutable Magnomo governance proposal log for material decisions not yet decided.

Required sections: `# RFC Proposals`, `## Entries`. Use one `### <proposal_id> - Title` heading per RFC entry; `proposal_id` is stable lowercase hyphen-case.

Each entry includes labels in order: `Status`, `Impact`, `Driver`, `Approvers`, `Contributors`, `Informed`, `Due Date`, `Background`, `Assumptions`, `Decision Criteria`, `Options`, `Recommendation`, `Outcome`, `Links`.

Quality rules: define criteria before options; include at least two real options and `Do Nothing`/status quo when relevant; include assumptions with confidence and invalidation triggers when known; keep `Outcome: pending` until decision; exclude implementation task decomposition, acceptance criteria, code instructions, technical design ownership, and Magia execution evidence except as a cited source. Use Mago for technical planning/RFC-style reasoning and Magia implementation ADRs for execution-grounded technical decisions.
