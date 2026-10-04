# Agentic Security Checklist

Use for `agentic-security-review` or as a focused overlay on `llm-agent-governance-review` when the target can plan, invoke tools, retain memory/context, delegate, or act across multiple steps.

## Coverage lens

Use current agentic-security taxonomies as **coverage aids**, not as SGR severity or confirmation oracles. At minimum inspect evidence for:

- goal/instruction hijacking through untrusted content or delegated context;
- tool misuse and unsafe action composition;
- identity, credential, privilege, and delegated-authority abuse;
- agentic supply-chain compromise affecting models, tools, prompts, skills, plugins, MCP servers, or runtime configuration;
- unexpected code/command execution and generated-code execution;
- memory/context poisoning and cross-session/cross-tenant contamination;
- insecure inter-agent communication, spoofing, message integrity, and delegation drift;
- cascading failures, recursive delegation/retries, cost amplification, and side-effect storms;
- human-agent trust exploitation, misleading approvals, and automation bias;
- rogue/out-of-scope action after policy, goal, or runtime state changes.

Do not manufacture a finding merely because a framework category exists. Map only when target evidence supports relevance.

## Review controls

For each material risk, identify:

1. **entry/trust boundary** — where untrusted or lower-trust content enters;
2. **authority affected** — which read/write/execute/delete/send/publish/deploy/delegate action could be influenced;
3. **policy source** — what constrains the action;
4. **enforcement point** — where policy is actually checked, if any;
5. **evidence layer** — structural, behavioral, runtime, or external-current;
6. **blast radius/containment** — tenant, repository, account, environment, downstream agent/tool, budget, or data scope;
7. **validation probe** — safe scenario or runtime evidence needed to resolve uncertainty.

## Agent-specific stop rules

- Capability never establishes authorization.
- Tool descriptions, retrieved content, peer-agent messages, memory, and model output are untrusted unless an explicit trust policy says otherwise.
- A documented policy without an enforcement point is not a behaviorally demonstrated control.
- Delegated authority must not silently exceed the caller's authority.
- Recursive/long-running agent flows require bounded termination, budgets/rate limits where impact is material, and idempotency/containment for side effects.
- Do not call an unexecuted scenario a successful defense.
