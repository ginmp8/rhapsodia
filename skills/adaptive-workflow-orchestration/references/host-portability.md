# Host Portability

## Portable core

Describe workflow needs as semantic capabilities. Do not make correctness depend on a vendor API, fixed installation path, specific model, MCP server, or third-party orchestration runtime.

Common capabilities:

- `read-context`;
- `invoke-specialist-agent`;
- `parallelize-independent-work`;
- `isolated-context`;
- `run-bounded-process`;
- `write-scoped-artifacts`;
- `persist-workflow-state`;
- `request-human-approval`.

## Native-first mapping

Use host-native agents/subagents, tool scoping, approvals, workspaces, or process execution when they satisfy the plan. Keep adapters thin: they translate a semantic capability but do not redefine ownership, authority, budgets, termination, or evidence.

## Degradation

- no parallel dispatch -> serial execution when the same stage semantics remain valid;
- no subagents -> one-agent sequential role execution only when authority/isolation claims remain valid;
- no isolated verifier -> block an independence claim or use a weaker explicitly labeled verification mode;
- no durable state -> keep a bounded session plan and do not claim long-running resumability;
- no command execution -> mark mechanical validation `not-run` and do not infer a pass.

Required capability loss blocks the affected workflow. Never auto-install an external orchestrator to hide the gap.

## Host claims

Separate:

- structural portability;
- documented host capability;
- observed host behavior;
- measured runtime behavior.

Support on one host is not evidence of support on another.
