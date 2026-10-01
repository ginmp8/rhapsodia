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

## Supporting Agent Skill discovery

When a plan declares a semantic capability that can be supplied by an Agent Skill, resolve it through the current host's native skill discovery. The plan must not require a particular external skill package name, repository path, vendor, or model.

Resolution rules:

- keep the lifecycle/domain owner unchanged;
- choose the minimum matching installed skill(s), not every potentially relevant skill;
- treat supporting skill instructions as guidance inside the active agent's existing authority;
- never let a supporting skill add tools, write scope, approval, delegation, or external-side-effect authority;
- record the semantic capability result and resolved skill identity when observable;
- do not persist the resolved implementation into the portable plan as a new hard dependency.

This is late binding: a different compatible skill may satisfy the same semantic capability on another host without changing the workflow contract.

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
